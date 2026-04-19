from typing import (
    Callable,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.application.queries import (
    RoleQuery,
)
from src.infrastructure.database import (
    models,
)


class RoleRepository(RoleQuery):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session=session_factory, model=models.Role)
