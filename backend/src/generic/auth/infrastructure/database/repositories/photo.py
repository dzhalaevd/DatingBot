from typing import (
    Callable,
)

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.infrastructure.database import (
    models,
)


class PhotoRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def create(self, user_id: int, remote_url: str) -> models.Photo:
        async with self._session_factory() as session:
            async with session.begin():
                photo = models.Photo(user_id=user_id, remote_url=remote_url)
                session.add(photo)
                await session.commit()
                return photo

    async def get(self, photo_id: int) -> models.Photo:
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(models.Photo).where(models.Photo.id == photo_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

    async def get_all_photos(self, user_id: int) -> list[models.Photo]:
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(models.Photo).where(models.Photo.user_id == user_id)
                result = await session.execute(stmt)
                return list(result.scalars().all())
