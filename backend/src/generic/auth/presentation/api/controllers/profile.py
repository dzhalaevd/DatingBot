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
    Path,
)
from starlette import (
    status,
)

from src.application.services.profile import (
    ProfileService,
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
from src.shared import (
    ex,
)

profile_router = APIRouter()


@profile_router.post(
    "/",
    response_model=dto.ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_profile(
        profile_in: dto.ProfileCreate,
        profile_service: ProfileService = Depends(Provide[Container.profile_service]),
        user: models.User = Depends(get_current_user)
) -> models.Profile:
    return await profile_service.create_profile(profile_in=profile_in, user_id=user.id)


@profile_router.get(
    "/{user_id}",
    response_model=dto.ProfileResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
@inject
async def get_profile(
        user_id: Annotated[int, Path],
        profile_service: ProfileService = Depends(Provide[Container.profile_service])
) -> models.Profile:
    try:
        return await profile_service.get_profile_by_id(user_id=user_id)
    except ex.ProfileNotFound:
        raise exceptions.ProfileNotFoundError()


@profile_router.patch(
    "/{profile_id}",
    response_model=dto.ProfileResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
@inject
async def update_profile(
        profile_id: Annotated[int, Path],
        profile_in: dto.ProfileUpdate,
        profile_service: ProfileService = Depends(Provide[Container.profile_service])
) -> models.Profile:
    return await profile_service.update_profile(profile_id=profile_id, profile_in=profile_in)


@profile_router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
@inject
async def delete_profile(
        profile_id: Annotated[int, Path],
        profile_service: ProfileService = Depends(Provide[Container.profile_service])
) -> None:
    return await profile_service.delete_profile(profile_id=profile_id)
