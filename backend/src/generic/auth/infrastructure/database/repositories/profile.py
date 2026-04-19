from typing import (
    Callable,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.application.queries.profile import (
    ProfileQuery,
)
from src.infrastructure.database import (
    models,
)


class ProfileRepository(ProfileQuery):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session=session_factory, model=models.Profile)
