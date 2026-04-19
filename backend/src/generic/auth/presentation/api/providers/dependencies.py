from typing import (
    Any,
    Callable,
    Coroutine,
    Literal,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)
from fastapi import (
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from jose import (
    JWTError,
)

from src.application import (
    dto,
)
from src.application.services import (
    UserService,
)
from src.infrastructure.database import (
    JTIRedisStorage,
    models,
)
from src.infrastructure.services.security import (
    JWTService,
)
from src.presentation.api.exceptions import (
    CredentialsError,
    TokenExpiredError,
)
from src.presentation.api.providers.di_containers import (
    Container,
)
from src.shared import (
    ex,
)


def _get_token_from_request(
        request: Request,
        token_type: Literal["access_token", "refresh_token"],
) -> str | None:
    authorization = request.headers.get("Authorization")
    token = request.cookies.get(token_type) or (authorization and authorization.split()[1])
    if token is None:
        raise CredentialsError
    return token


def _decode_token_from_request(
        request: Request | None = None,
        token: str | None = None,
        token_type: Literal["access_token", "refresh_token"] | None = None
) -> dto.TokenData:
    if token is None and token_type is not None:
        token = _get_token_from_request(request=request, token_type=token_type)
    try:
        payload = JWTService.decode_token(token=token)
        user_id: int = int(payload.get("sub"))
        jti: str = payload.get("jti")
        if jti is None:
            raise CredentialsError
        if user_id is None:
            raise CredentialsError
        return dto.TokenData(
            user_id=user_id,
            jti=jti
        )
    except JWTError:
        raise CredentialsError
    except ex.JWTDecodeError:
        raise TokenExpiredError


@inject
async def _get_user_and_tokens(
        request: Request,
        response: Response,
        user_service: UserService = Depends(Provide[Container.user_service]),
        blacklist_service: JTIRedisStorage = Depends(Provide[Container.blacklist_service]),
) -> tuple[models.User, str, str] | None:
    try:
        token_data = _decode_token_from_request(request=request, token_type="access_token")
    except CredentialsError:
        token_data = _decode_token_from_request(request=request, token_type="refresh_token")
        if token_data is None:
            raise CredentialsError

    user = await user_service.get_user_by_id(user_id=token_data.user_id)
    if user is None:
        raise CredentialsError
    is_in_blacklist = await blacklist_service.is_in_blacklist(jti=token_data.jti)
    if is_in_blacklist:
        raise CredentialsError
    access_token = JWTService.create_access_token(uid=str(user.id), fresh=False)
    refresh_token = JWTService.create_refresh_token(uid=str(user.id))
    JWTService.set_cookies(response=response, access_token=access_token, refresh_token=refresh_token)

    return user, access_token, refresh_token


@inject
async def get_current_user(
        request: Request,
        response: Response,
        user_service: UserService = Depends(Provide[Container.user_service]),
        blacklist_service: JTIRedisStorage = Depends(Provide[Container.blacklist_service])
) -> models.User:
    user, _, _ = await _get_user_and_tokens(request, response, user_service, blacklist_service)
    return user


@inject
async def refresh_tokens(
        request: Request,
        response: Response,
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> dto.JWTokens:
    user, access_token, refresh_token = await _get_user_and_tokens(request, response, user_service)
    return dto.JWTokens(access_token=access_token, refresh_token=refresh_token)


@inject
async def verify_token_from_request(
        request: Request,
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> bool:
    try:
        token_data = _decode_token_from_request(request=request, token_type="access_token")
        user = await user_service.get_user_by_id(user_id=token_data.user_id)
        if user is None:
            return False
        return True
    except JWTError:
        return False


@inject
def require_role() -> Callable[[models.User], Coroutine[Any, Any, models.User]]:
    async def check_user_roles(user: models.User = Depends(get_current_user)) -> models.User:
        if user.is_superuser:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this operation",
            )

    return check_user_roles


@inject
async def revoke_tokens(
        request: Request,
        blacklist_service: JTIRedisStorage = Depends(Provide[Container.blacklist_service])
) -> None:
    access_token = _get_token_from_request(request, "access_token")
    refresh_token = _get_token_from_request(request, "refresh_token")
    decode_access_token = JWTService.decode_token(token=access_token)
    decode_refresh_token = JWTService.decode_token(token=refresh_token)
    access_jti = decode_access_token["jti"]
    await blacklist_service.add(access_jti)

    refresh_jti = decode_refresh_token["jti"]
    await blacklist_service.add(refresh_jti)
