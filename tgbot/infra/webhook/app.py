from contextlib import asynccontextmanager

from fastapi import FastAPI

from tgbot.bot import create_bot, create_dispatcher, on_shutdown, on_startup
from tgbot.config import load_config
from tgbot.infra.webhook.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config(".env")
    bot = create_bot(config)
    dp = create_dispatcher(config)

    app.state.config = config
    app.state.bot = bot
    app.state.dp = dp

    await on_startup(bot, config.tg_bot.admin_ids)

    try:
        yield
    finally:
        await on_shutdown(bot)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telegram Bot Webhook",
        lifespan=lifespan,
    )

    app.include_router(router)

    return app


app = create_app()
