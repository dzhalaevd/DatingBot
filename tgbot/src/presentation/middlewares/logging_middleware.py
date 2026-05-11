from aiogram import (
    types,
)
from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
)
from loader import (
    logger,
)


class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        logger.info(message)

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        logger.info(call)
