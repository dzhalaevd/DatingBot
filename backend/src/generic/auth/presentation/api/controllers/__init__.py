from .auth import (
    auth_router,
)
from .healthcheck import (
    healthcheck_router,
)
from .photo import (
    photo_router,
)
from .profile import (
    profile_router,
)
from .role import (
    role_router,
)
from .user import (
    user_router,
)

__all__ = (
    "auth_router",
    "user_router",
    "role_router",
    "healthcheck_router",
    "profile_router",
    "photo_router",
)
