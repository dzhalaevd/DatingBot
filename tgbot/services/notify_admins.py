from abc import (
    ABC,
    abstractmethod,
)

import aiogram
from aiogram import (
    Dispatcher,
)
import aiogram.utils.exceptions
from aiogram.utils.exceptions import (
    ChatNotFound,
)

from data.config import (
    load_config,
)
from loader import (
    _,
    bot,
    logger,
)


class BaseNotification(ABC):
    @abstractmethod
    def send(self, *args):
        pass


class AdminNotification(BaseNotification):
    def __init__(self, dp: Dispatcher):
        self.dp = dp

    async def send(self) -> None:
        logger.info(_("Оповещение администрации..."))
        for admin in load_config().tg_bot.admin_ids:
            try:
                await bot.send_message(
                    admin, _("Бот был успешно запущен"), disable_notification=True
                )
            except ChatNotFound:
                logger.debug("Чат с админом не найден")


class ErrorNotification(BaseNotification):
    def __init__(self, error_message: Exception):
        self.__error_message = error_message

    async def send(self) -> None:
        text = (
            f"❗ Error During Operation ❗\n"
            f"{self.__error_message}\n\n❗"
            f" The bot will restart automatically."
        )
        for user_id in load_config().tg_bot.admin_ids:
            try:
                await bot.send_message(user_id, text)
            except (aiogram.exceptions.BotBlocked, aiogram.exceptions.ChatNotFound):
                continue
