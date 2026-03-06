from abc import ABC, abstractmethod

from app.models.auth import AuthTokenPayload


class AuthService(ABC):
    @abstractmethod
    def parse_token(self, token: str) -> AuthTokenPayload:
        pass

    @abstractmethod
    def create_token(self, payload: AuthTokenPayload) -> str:
        pass

    @abstractmethod
    def hash_password(self, pwd: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, pwd: str, hash: str) -> bool:
        pass
