import logging
import time
from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
    types,
)
from redis.asyncio.client import Redis  # type: ignore

from .exceptions import (
    CancelHandler,
    Throttled,
)
from bot_types import (
    Handler,
)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(
            self,
            r: Redis,
            limit: int = 1,
            key_prefix: str = 'antiflood_',
    ) -> None:
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(r=r)

        super().__init__()

    async def __call__(
            self,
            handler: Handler,
            event: types.Message,
            data: dict[str, Any]
    ) -> Any:

        try:
            await self.on_process_event(event)
        except CancelHandler:
            # Cancel current handler
            return

        try:
            result = await handler(event, data)
        except Exception as e:
            logging.info(e)
            return

        return result

    async def on_process_event(self, event: types.Message) -> Any:
        limit = self.rate_limit
        key = f"{self.prefix}_message"

        try:
            await self.throttle_manager.throttle(key, rate=limit, user_id=event.from_user.id, chat_id=event.chat.id)
        except Throttled as t:
            await self.event_throttled(event, t)
            raise CancelHandler()

    @staticmethod
    async def event_throttled(event: types.Message, throttled: Throttled) -> None:
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 3:
            await event.answer(f'Too many requests.\nTry again in {delta:.2f} seconds.')


class ThrottleManager:
    bucket_keys = [
        "RATE_LIMIT", "DELTA",
        "LAST_CALL", "EXCEEDED_COUNT"
    ]

    def __init__(self, r: Redis):
        self.redis = r

    async def throttle(self, key: str, rate: float, user_id: int, chat_id: int) -> bool:
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}_{chat_id}'

        data = await self.redis.hmget(bucket_name, self.bucket_keys)
        data = {
            k: float(v.decode())
            if isinstance(v, bytes)
            else v
            for k, v in zip(self.bucket_keys, data)
            if v is not None
        }
        called = data.get("LAST_CALL", now)
        delta = now - float(called)
        result = delta >= rate or delta <= 0
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] = int(data["EXCEEDED_COUNT"])
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        await self.redis.hset(bucket_name, mapping=data)

        if not result:
            raise Throttled(
                key=key,
                chat=chat_id,
                user=user_id,
                rate=rate,
                delta=delta,
                called_at=now,
                exceeded_count=data.get("EXCEEDED_COUNT", 0)
            )
        return result
