from typing import (
    Annotated,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from src.application.services import (
    UserService,
)
from src.infrastructure.database import (
    models,
)
from src.presentation.api import (
    dto,
    exceptions,
)
from src.presentation.api.providers import (
    Container,
    get_current_user,
)

user_router = APIRouter()


@user_router.get(
    "/",
    summary="Getting all users",
    response_model=list[dto.UserResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_list(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> list[models.User]:
    return await user_service.get_users(skip=skip, limit=limit)


@user_router.get(
    "/me/",
    summary="Getting user details",
    response_model=dto.UserResponse,
    responses={400: {"description": "Your account is deactivated"}},
    status_code=status.HTTP_200_OK,
)
@inject
async def get_user(
        current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    if not current_user.is_active:
        raise exceptions.UserDeactivatedError()
    return current_user


@user_router.patch(
    "/me/",
    response_model=dto.UserResponse,
    responses={400: {"description": "Your account is deactivated"}},
    status_code=status.HTTP_200_OK,
)
@inject
async def update_user(
        user_in: dto.UserUpdate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> models.User:
    if not current_user.is_active:
        raise exceptions.UserDeactivatedError()
    return await user_service.update_user(pk=current_user.id, user_in=user_in)


@user_router.post(
    "/me/reactivate/",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def reactivate_user(
        current_user: Annotated[models.User, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> None:
    return await user_service.reactivate_user(user_id=current_user.id)


@user_router.delete(
    "/me/",
    summary="Deactivate user account",
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def deactivate_user(
        current_user: Annotated[models.User, Depends(get_current_user)],
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> None:
    return await user_service.deactivate_user(user_id=current_user.id)
