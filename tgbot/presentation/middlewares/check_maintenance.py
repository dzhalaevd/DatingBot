from typing import (
    NoReturn,
    Union,
)

from aiogram import (
    types,
)
from aiogram.dispatcher.handler import (
    CancelHandler,
)
from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
)

from data.config import (
    load_config,
)
from loader import (
    _,
)
from utils.db_api import (
    db_commands,
)


class IsMaintenance(BaseMiddleware):
    def __init__(self):
        super(IsMaintenance, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        await self.check_tech_works(obj=message)

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.check_tech_works(obj=call)

    @staticmethod
    async def check_tech_works(
            obj: Union[types.CallbackQuery, types.Message]
    ) -> NoReturn:
        text = _("Ведутся технические работы")
        try:
            setting = await db_commands.select_setting_tech_work()
            tech_works = setting.get("technical_works", False)
            if tech_works and obj.from_user.id not in load_config().tg_bot.admin_ids:
                try:
                    await obj.answer(text=text, show_alert=True)
                except TypeError:
                    await obj.answer(text=text)
                raise CancelHandler()
        except AttributeError:
            pass
