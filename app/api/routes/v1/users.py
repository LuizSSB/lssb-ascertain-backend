from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from app.api.middleware.auth import authenticate
from app.api.routes.auth import AuthUsecasesDependency
from app.models.api import EntityResponse, ListResponse
from app.models.api.users import GETUsers, PATCHUser, POSTUser
from app.models.user import User, UserBaseData, UserRole
from app.tooling.ioc import ioc_container_type
from app.usecases.user import UserUsecases

ROUTER_V1_USERS = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(authenticate({UserRole.ADMIN}))],
)

UserUsecasesDependency = Annotated[UserUsecases, Depends(Provide[ioc_container_type().user_usecases])]


@ROUTER_V1_USERS.get("")
@inject
async def get_users(usecase: UserUsecasesDependency, request: Annotated[GETUsers, Depends()]) -> ListResponse[User]:
    users, next_token = await usecase.list_users(
        limit=request.limit,
        next_token=request.parsed_next_token,
    )
    return ListResponse(next_token=str(next_token) if next_token else None, data=users)


@ROUTER_V1_USERS.get("/{user_id}")
@inject
async def get_user(usecase: UserUsecasesDependency, user_id: str) -> EntityResponse[User]:
    if not (user := await usecase.get_user(user_id)):
        raise HTTPException(404)

    return EntityResponse(data=user)


@ROUTER_V1_USERS.post("", status_code=201)
@inject
async def sign_up(usecase: AuthUsecasesDependency, user_data: POSTUser) -> EntityResponse[User]:
    user = await usecase.sign_up(UserBaseData.model_validate(user_data.model_dump()), user_data.password)
    return EntityResponse(data=user)


@ROUTER_V1_USERS.patch("/{user_id}")
@inject
async def patch_user(usecase: UserUsecasesDependency, user_id: str, update: PATCHUser) -> EntityResponse[User]:
    if not (user := await usecase.update_user(user_id, update)):
        raise HTTPException(404)

    return EntityResponse(data=user)


@ROUTER_V1_USERS.delete("/{user_id}")
@inject
async def delete_user(usecase: UserUsecasesDependency, user_id: str) -> EntityResponse[User]:
    if not (user := await usecase.delete_user(user_id)):
        raise HTTPException(404)

    return EntityResponse(data=user)
