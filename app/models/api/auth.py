from typing import Literal

from openai import BaseModel

from app.models.user import UserBaseData


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class POSTSignUp(UserBaseData):
    password: str
