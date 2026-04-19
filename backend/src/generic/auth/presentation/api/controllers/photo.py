from typing import (
    Annotated,
    Any,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from src.application.services import (
    PhotoService,
)
from src.infrastructure.database import (
    models,
)
from src.presentation.api import (
    dto,
)
from src.presentation.api.providers import (
    Container,
    get_current_user,
)

photo_router = APIRouter()


@photo_router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=dto.PhotoUploadResponse,
)
@inject
async def upload_photo(
        file: UploadFile = File(...),
        user: models.User = Depends(get_current_user),
        photo_service: PhotoService = Depends(Provide[Container.photo_service])
) -> Any:
    return await photo_service.upload_file(user_id=user.id, file=file)


@photo_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    # response_model=dto.PhotosResponse,
)
@inject
async def get_all_user_photos(
        user: models.User = Depends(get_current_user),
        photo_service: PhotoService = Depends(Provide[Container.photo_service])
) -> Any:
    return await photo_service.get_all_photos_from_s3(user_id=user.id)


@photo_router.get(
    "/db",
    status_code=status.HTTP_200_OK
)
@inject
async def get_all_user_photos_from_db(
        user: models.User = Depends(get_current_user),
        photo_service: PhotoService = Depends(Provide[Container.photo_service]),
) -> Any:
    return await photo_service.get_all_photos_from_db(user_id=user.id)


@photo_router.patch(
    "/",
    status_code=status.HTTP_200_OK,
)
@inject
async def update_photo(
        old_photo_url: str = Form(...),
        file: UploadFile = File(...),
        user: models.User = Depends(get_current_user),
        photo_service: PhotoService = Depends(Provide[Container.photo_service])
) -> Any:
    try:
        return await photo_service.update_photo(
            user_id=user.id,
            new_file=file,
            old_photo_url=old_photo_url
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@photo_router.post(
    "/delete",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
@inject
async def delete_photo(
        photo: dto.PhotoDeleteResponse,
        photo_service: PhotoService = Depends(Provide[Container.photo_service])
) -> Any:
    try:
        await photo_service.delete_photo(
            photo_url=photo.photo_url
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@photo_router.get(
    "/{photo_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
@inject
async def get_photo_by_id(
        photo_id: Annotated[int, Path()],
        photo_service: PhotoService = Depends(Provide[Container.photo_service]),
) -> Any:
    return await photo_service.get_photo_by_id(photo_id=photo_id)
