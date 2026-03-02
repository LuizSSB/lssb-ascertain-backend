from pydantic import BaseModel


class AuthTokenPayload(BaseModel):
    sub: str
    exp: int
