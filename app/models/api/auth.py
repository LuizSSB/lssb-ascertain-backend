from typing import Literal

from openai import BaseModel


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class POSTSignUp(BaseModel):
    name: str
    email: str
    password: str
