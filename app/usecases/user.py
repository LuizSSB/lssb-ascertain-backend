from app.data.user import UserRepository
from app.models.user import User, UserNextToken, UserUpdateData
from app.tooling.logging import AppLogger


class UserUsecases:

    def __init__(self, repository: UserRepository, logger: AppLogger) -> None:
        self.repository = repository
        self.logger = logger

    async def list_users(
        self, *, next_token: UserNextToken | None = None, limit: int | None = None
    ) -> tuple[list[User], UserNextToken | None]:
        self.logger.debug("list_users usecase", next_token=next_token, limit=limit)

        next_token = next_token or UserNextToken(skip=0)
        users = list(
            await self.repository.list_users(
                name=next_token.search_term,
                sort_by=(next_token.sort_field, next_token.sort_order or "asc") if next_token.sort_field else None,
                skip=next_token.skip,
                limit=limit,
            )
        )

        if limit and len(users) >= limit:
            next_next_token = next_token.model_copy()
            next_next_token.skip += len(users)
        else:
            next_next_token = None

        self.logger.debug("list_users returned", next_token=next_token, limit=limit, next_next_token=next_next_token)
        return users, next_next_token

    async def get_user(self, user_id: str) -> User | None:
        self.logger.debug("get_user usecase", user_id=user_id)
        if user_and_password := await self.repository.get_user(user_id):
            return user_and_password[0]
        return None

    async def update_user(self, user_id: str, user_data: UserUpdateData) -> User | None:
        self.logger.debug("update_user usecase", user_id=user_id, user_data=user_data.model_dump())
        return await self.repository.update_user(user_id, user_data)

    async def delete_user(self, user_id: str) -> User | None:
        self.logger.debug("delete_user usecase", user_id=user_id)
        return await self.repository.delete_user(user_id)
