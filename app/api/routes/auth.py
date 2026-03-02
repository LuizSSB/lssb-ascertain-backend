from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.middleware.auth import ROUTE_AUTH
from app.models.api import EntityResponse, ErrorResponse
from app.models.api.auth import AuthResponse, POSTSignUp
from app.models.exceptions import NotFoundException
from app.models.user import User, UserBaseData
from app.tooling.ioc import ioc_container_type
from app.usecases.auth import AuthUsecases

ROUTER_AUTH = APIRouter(prefix=f"/{ROUTE_AUTH}")

AuthUsecasesDependency = Annotated[AuthUsecases, Depends(Provide[ioc_container_type().auth_usecases])]


@ROUTER_AUTH.post(f"")
@inject
async def auth(
    usecase: AuthUsecasesDependency, credentials: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> AuthResponse:
    try:
        token = await usecase.log_user_in(credentials.username, credentials.password)
    except NotFoundException:
        raise HTTPException(status_code=403, detail=ErrorResponse(message="Username and/or password invalid"))

    return AuthResponse(
        access_token=token,
        token_type="bearer",
    )


@ROUTER_AUTH.post("sign-up", status_code=201)
@inject
async def sign_up(usecase: AuthUsecasesDependency, user_data: POSTSignUp) -> EntityResponse[User]:
    user = await usecase.sign_up(UserBaseData.model_validate(user_data.model_dump()), user_data.password)
    return EntityResponse(data=user)
