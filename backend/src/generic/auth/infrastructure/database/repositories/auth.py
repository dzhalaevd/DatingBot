import abc
from typing import (
    Any,
    Callable,
)

from sqlalchemy import (
    Result,
    Select,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.application import (
    dto,
)
from src.application.dto import (
    ResetPassword,
)
from src.application.queries import (
    AuthQuery,
)
from src.domain.user import (
    entity,
)
from src.infrastructure.database import (
    models,
)
from src.infrastructure.services.security import (
    HashService,
    JWTService,
)
from src.shared import (
    ex,
)
from src.shared.types import (
    CreateSchemaT,
    ModelT,
    SchemaT,
)


class IAuthStrategy(abc.ABC):
    @abc.abstractmethod
    async def authenticate(
            self,
            session: AsyncSession,
            user_in: SchemaT,
    ) -> tuple[int, SchemaT] | SchemaT:
        pass


class DefaultAuthStrategy(IAuthStrategy):

    @staticmethod
    def _get_query(*args: Any, **kwargs: Any) -> Select[tuple[Any]]:
        username_f = models.User.username == kwargs.get("username")
        if kwargs.get("telegram_id"):
            telegram_id_f = models.User.telegram_id == kwargs.get("telegram_id")
            combined_filter = or_(username_f, telegram_id_f)
        else:
            combined_filter = username_f
        return select(models.User).filter(combined_filter)

    async def authenticate(
            self,
            session: AsyncSession,
            user_in: SchemaT,
    ) -> tuple[int, dto.JWTokens] | dto.JWTokens:
        stmt = self._get_query(**user_in.model_dump())
        result: Result = await session.execute(stmt)
        user: models.User = result.scalar_one_or_none()
        if not user:
            raise ex.UserNotFound()

        if user_in.password and not entity.User.check_password(password=user.password, password_in=user_in.password):
            raise ex.IncorrectPassword()

        access_token = JWTService.create_access_token(uid=str(user.id), fresh=True)
        refresh_token = JWTService.create_refresh_token(uid=str(user.id))
        if user.telegram_id:
            telegram_id = int(str(user.telegram_id))
            return telegram_id, dto.JWTokens(access_token=access_token, refresh_token=refresh_token)
        if user_in.telegram_id:
            user.telegram_id = user_in.telegram_id
            await session.commit()
        return dto.JWTokens(access_token=access_token, refresh_token=refresh_token)


class TelegramAuthStrategy(IAuthStrategy):
    @staticmethod
    def _get_query(**kwargs: Any) -> Select[tuple[Any]]:
        telegram_id = kwargs.get("telegram_id")
        return select(models.User).where(models.User.telegram_id == telegram_id)

    async def authenticate(
            self,
            session: AsyncSession,
            user_in: SchemaT,
            *args: Any,
            **kwargs: Any,
    ) -> dto.JWTokens:
        stmt = self._get_query(telegram_id=user_in.telegram_id)
        result: Result = await session.execute(stmt)
        user: models.User = result.scalar_one_or_none()

        if HashService.verify_signature(**user_in.model_dump()):
            if not user:
                raise ex.UserNotFound()
            else:
                access_token = JWTService.create_access_token(
                    uid=str(user.id), fresh=True
                )
                refresh_token = JWTService.create_refresh_token(uid=str(user.id))
                return dto.JWTokens(access_token=access_token, refresh_token=refresh_token)
        else:
            raise ex.InvalidSignature()


class AuthRepository(AuthQuery):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        super().__init__(session=session_factory, model=models.User)

    async def signup(
            self,
            user_in: CreateSchemaT,
            *args: Any,
            **kwargs: Any
    ) -> ModelT:
        async with self._session_factory() as session:
            stmt = self._get_query(*args, **kwargs)
            result: Result = await session.execute(stmt)
            if result.scalar() is not None:
                raise ex.UserAlreadyExists()
            user = self.model(**user_in.__dict__)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def signin(
            self,
            strategy: IAuthStrategy,
            user_in: SchemaT
    ) -> tuple[int, dto.JWTokens] | dto.JWTokens:
        async with self._session_factory() as session:
            return await strategy.authenticate(user_in=user_in, session=session)

    async def reset_password(self, pk: int, password_in: ResetPassword) -> None:
        async with self._session_factory() as session:
            stmt = self._get_user(id=pk)
            result: Result = await session.execute(stmt)
            user: models.User = result.scalar_one_or_none()
            if not user:
                raise ex.UserNotFound()
            if not HashService.verify_password(password=user.password, hashed_password=password_in.old_password):
                raise ex.IncorrectPassword()
            new_hashed_password = HashService.hash_password(password=password_in.new_password)
            user.password = new_hashed_password
            await session.execute(stmt)
            await session.commit()
