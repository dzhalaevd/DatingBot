from typing import (
    Callable,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.application.queries import (
    UserQuery,
)
from src.infrastructure.database import (
    models,
)


class UserRepository(UserQuery):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        super().__init__(session=session_factory, model=models.User)
