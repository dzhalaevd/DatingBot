import pytest
from config import (
    Miscellaneous,
    load_config,
)
from telethon import (
    TelegramClient,
)
from telethon.sessions import (
    StringSession,
)
from telethon.tl.custom import (
    Conversation,
)

cfg = load_config()


@pytest.fixture(scope="session")
def config() -> Miscellaneous:
    return cfg.misc


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def conv(config: Miscellaneous) -> Conversation:
    client = TelegramClient(StringSession(config.session_str), config.api_id, config.api_hash, sequential_updates=True)
    await client.connect()
    async with client.conversation("@TestingDatingbottestbot", timeout=5) as conv:
        yield conv
    await client.disconnect()
