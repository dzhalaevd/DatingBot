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

from keyboards.inline.admin_inline import (
    unban_user_keyboard,
)
from loader import (
    _,
)
from utils.db_api import (
    db_commands,
)


class BanMiddleware(BaseMiddleware):
    def __init__(self):
        super(BanMiddleware, self).__init__()

    @staticmethod
    async def is_banned(user):
        try:
            return user.is_banned
        except AttributeError:
            return False

    async def on_process_message(self, message: types.Message, data: dict) -> None:
        await self.check_ban_user(obj=message)

    async def on_process_callback_query(
            self, call: types.CallbackQuery, data: dict
    ) -> None:
        user = await db_commands.select_user(telegram_id=call.from_user.id)
        if (user is not None and await self.is_banned(user=user)) and (
                call.data != "unban"
                and call.data != "unban_menu"
                and call.data != "yoomoney:check_payment"
                and call.data != "cancel_payment"
                and call.data != "yoomoney"
        ):
            await self.check_ban_user(obj=call)

    async def check_ban_user(
            self, obj: Union[types.CallbackQuery, types.Message]
    ) -> NoReturn:
        user = await db_commands.select_user(telegram_id=obj.from_user.id)

        text = _("😢 Вы заблокированы!")
        markup = await unban_user_keyboard()
        if await self.is_banned(user=user):
            try:
                await obj.answer(text=text, reply_markup=markup)
            except TypeError:
                await obj.message.answer(text=text, reply_markup=markup)
            raise CancelHandler()
