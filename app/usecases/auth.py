from datetime import datetime

from app.data.user import UserRepository
from app.models.auth import AuthTokenPayload
from app.models.exceptions import NotFoundException, ResourceExpiredException
from app.models.user import User, UserBaseData, UserRole
from app.services.auth import AuthService
from app.tooling.logging import AppLogger

_TTL_TOKEN_MINUTES = 30


class AuthUsecases:

    def __init__(self, user_repository: UserRepository, auth_service: AuthService, logger: AppLogger) -> None:
        self.user_repository = user_repository
        self.auth_service = auth_service
        self.logger = logger

    async def sign_up(self, user_data: UserBaseData, password: str) -> User:
        self.logger.debug("create_user usecase", user_data=user_data.model_dump())
        hashed_password = self.auth_service.hash_password(password)
        return await self.user_repository.create_user(user_data, hashed_password)

    async def authenticate_user(self, token: str, allowed_roles: set[UserRole]) -> User:
        payload = self.auth_service.parse_token(token)

        if payload.exp < datetime.now().timestamp():
            raise ResourceExpiredException()

        if not (user_and_password := await self.user_repository.get_user(payload.sub)):
            raise NotFoundException()

        if user_and_password[0].role not in allowed_roles:
            raise PermissionError(
                f"User with {user_and_password[0].role} cannot access route reserved to role {allowed_roles}"
            )

        return user_and_password[0]

    async def log_user_in(self, email: str, password: str) -> str:
        if not (
            user_and_password := await self.user_repository.get_user(email)
        ) or not self.auth_service.verify_password(password, user_and_password[1]):
            raise NotFoundException

        return self.auth_service.create_token(
            AuthTokenPayload(
                sub=user_and_password[0].id,
                exp=int(datetime.now().timestamp()) + _TTL_TOKEN_MINUTES * 60,
            )
        )
