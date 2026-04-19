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
    Query,
    status,
)

from src.application.services import (
    RoleService,
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
    require_role,
)

role_router = APIRouter()


@role_router.post(
    "/",
    response_model=dto.RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role())],
)
@inject
async def create_role(
        role_in: dto.RoleCreate,
        role_service: RoleService = Depends(Provide[Container.role_service])
) -> models.Role:
    return await role_service.create_role(role_in=role_in)


@role_router.get(
    "/single/",
    response_model=list[dto.RoleResponse] | dto.RoleResponse,
    summary="Get the single role by title or role id",
    status_code=status.HTTP_200_OK,
)
@inject
async def get_role(
        role_id: Annotated[int | None, Query] = None,
        title: Annotated[str | None, Query] = None,
        role_service: RoleService = Depends(Provide[Container.role_service]),
) -> list[models.Role] | models.Role:
    if role_id is not None:
        role = await role_service.get_role_by_id(role_id=role_id)
    elif title is not None:
        role = await role_service.get_role_by_title(title=title)
    else:
        return await role_service.get_all_roles()

    if role is None:
        raise exceptions.RoleNotFoundError()
    return role


@role_router.patch(
    "/{role_id}/",
    response_model=dto.RoleResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role())],
)
@inject
async def update_role(
        role_id: Annotated[int, Path],
        role_in: dto.RoleUpdate,
        role_service: RoleService = Depends(Provide[Container.role_service]),
) -> models.Role:
    return await role_service.update_role(pk=role_id, role_in=role_in)


@role_router.delete(
    "/{role_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role())],
)
@inject
async def delete_role(
        role_id: Annotated[int, Path],
        role_service: RoleService = Depends(Provide[Container.role_service]),
) -> None:
    return await role_service.delete_role(role_id=role_id)
