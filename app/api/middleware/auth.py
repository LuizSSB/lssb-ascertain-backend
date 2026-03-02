from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.api import ErrorResponse
from app.models.exceptions import NotFoundException, ResourceExpiredException
from app.models.user import User, UserRole
from app.tooling.ioc import ioc_container_type
from app.usecases.auth import AuthUsecases

ROUTE_AUTH = "auth"
_SCHEME_OAUTH_2 = OAuth2PasswordBearer(tokenUrl=ROUTE_AUTH)

AuthUsecasesDependency = Annotated[AuthUsecases, Depends(Provide[ioc_container_type().auth_usecases])]


def authenticate(allowed_roles: set[UserRole] = set(UserRole)):
    if not allowed_roles:
        raise Exception("Allowed roles cannot be empty")

    @inject
    async def _authenticate(
        usecase: AuthUsecasesDependency,
        token: Annotated[str, Depends(_SCHEME_OAUTH_2)],
    ) -> User:
        credentials_exception = HTTPException(
            status_code=401,
            detail=ErrorResponse(message="Could not validate credentials"),
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            return await usecase.authenticate_user(token, allowed_roles)
        except ValueError:
            raise credentials_exception
        except NotFoundException:
            raise credentials_exception
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=ErrorResponse(message=str(e)))
        except ResourceExpiredException:
            raise HTTPException(status_code=401, detail=ErrorResponse(message="Expired credentials"))

    return _authenticate
