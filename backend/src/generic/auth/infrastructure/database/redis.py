# https://github.com/redis/redis-py/issues/2249
from typing import (
    Any,
)

from redis.asyncio import (  # type: ignore
    Redis,
    from_url,
)


class RedisConnector:
    def __init__(self, url: str) -> None:
        self.protocol: Redis = from_url(
            url=url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def execute(self, command: str, *args: Any, **kwargs: Any) -> Any:
        return await getattr(self.protocol, command)(*args, **kwargs)


class JTIRedisStorage:
    def __init__(self, redis_connector: RedisConnector) -> None:
        self.protocol = redis_connector
        self.namespace: str = "jwt_blacklist"

    async def add(self, jti: str) -> None:
        blacklist_key = f"{self.namespace}:{jti}"
        await self.protocol.execute("set", blacklist_key, 1)

    async def get(self, jti: str) -> str:
        blacklist_key = f"{self.namespace}:{jti}"
        return await self.protocol.execute("get", blacklist_key)

    async def is_in_blacklist(self, jti: str) -> bool:
        blacklist_key = f"{self.namespace}:{jti}"
        exists = await self.protocol.execute("exists", blacklist_key)
        return bool(exists)

    async def remove(self, user_id: int) -> int:
        blacklist_key = f"{self.namespace}:{user_id}"
        return await self.protocol.execute("delete", blacklist_key)

    async def clear(self, user_id: int, count_size: int = 10) -> int:
        pattern = f"{self.namespace}:{user_id}:*"
        cursor = b"0"
        deleted_count = 0

        while cursor:
            cursor, keys = await self.protocol.execute("scan", cursor, match=pattern, count=count_size)
            deleted_count += await self.protocol.execute("unlink", *keys)

        return deleted_count

    async def get_jti(self, user_id: int, token_type: str) -> list[Any]:
        pattern = f"{user_id}:{token_type}:*"
        cursor = b"0"
        jtis = []

        while cursor:
            cursor, keys = await self.protocol.execute("scan", cursor, match=pattern, count=10)
            jtis.extend(keys)

        return jtis
