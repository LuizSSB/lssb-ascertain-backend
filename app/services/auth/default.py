import jwt
from pwdlib import PasswordHash

from app.models.auth import AuthTokenPayload
from app.services.auth import AuthService
from app.tooling.logging import AppLogger

_PASSWORD_HASH = PasswordHash.recommended()
_SECRET_KEY_TOKEN = "b40f0fc98382861f637f88e5cc78cf0eca8f7ebddd7f11a84e9f13e45ddfc056"
_ALGORITHM_TOKEN = "HS256"


class DefaultAuthService(AuthService):
    def __init__(self, logger: AppLogger):
        self.logger = logger

    def parse_token(self, token: str) -> AuthTokenPayload:
        payload_dict = jwt.decode(jwt=token, key=_SECRET_KEY_TOKEN, algorithms=[_ALGORITHM_TOKEN])
        payload = AuthTokenPayload(**payload_dict)
        return payload

    def create_token(self, payload: AuthTokenPayload) -> str:
        token = jwt.encode(payload.model_dump(), _SECRET_KEY_TOKEN, algorithm=_ALGORITHM_TOKEN)
        return token

    def hash_password(self, pwd: str):
        return _PASSWORD_HASH.hash(pwd)

    def verify_password(self, pwd: str, hash: str) -> bool:
        return _PASSWORD_HASH.verify(pwd, hash)
