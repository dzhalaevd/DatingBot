from .controllers import (
    auth_router,
    healthcheck_router,
    role_router,
    user_router,
    profile_router,
    photo_router,
)

__all__ = (
    "user_router",
    "auth_router",
    "healthcheck_router",
    "role_router",
    "profile_router",
    "photo_router",
)
