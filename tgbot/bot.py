import asyncio

from tgbot.config import Config
from tgbot.presentation.handlers.v2 import routers_list
from tgbot.proxy_pool import create_aiogram_session
from tgbot.services import broadcaster
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import (
    MemoryStorage,
)
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisStorage,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

defaults = DefaultBotProperties(
    parse_mode=ParseMode.HTML,
    protect_content=True,
    link_preview_is_disabled=True
)


async def on_startup(bot: Bot, admin_ids: list[int]) -> None:
    await broadcaster.broadcast(bot, admin_ids, "Бот был запущен")


async def on_shutdown(bot: Bot) -> None:
    await bot.session.close()


def register_global_middlewares(dp: Dispatcher, config: Config) -> None:
    """Register global middlewares for the given dispatcher.

    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    """
    middleware_types = []

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def get_storage(config) -> BaseStorage:
    """Return storage based on the provided configuration.

    :param config: The configuration object from the loaded configuration.

    :return: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def create_bot(config: Config) -> Bot:
    session = await create_aiogram_session(config.tg_bot.token)

    return Bot(
        session=session,
        token=config.tg_bot.token,
        default=defaults
    )


def create_dispatcher(config: Config) -> Dispatcher:
    dp = Dispatcher(storage=get_storage(config))

    dp.include_routers(*routers_list)
    register_global_middlewares(dp, config)

    return dp
