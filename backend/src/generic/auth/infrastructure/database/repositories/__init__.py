from .auth import (
    AuthRepository,
    IAuthStrategy,
    DefaultAuthStrategy,
    TelegramAuthStrategy,
)
from .photo import (
    PhotoRepository,
)
from .profile import (
    ProfileRepository,
)
from .role import (
    RoleRepository
)
from .user import (
    UserRepository,
)

__all__ = (
    "UserRepository",
    "AuthRepository",
    "RoleRepository",
    "IAuthStrategy",
    "DefaultAuthStrategy",
    "TelegramAuthStrategy",
    "ProfileRepository",
    "PhotoRepository",
)
