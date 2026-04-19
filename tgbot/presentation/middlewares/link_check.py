import asyncio
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
from keyboards.inline.necessary_links_inline import (
    necessary_links_keyboard,
)
from loader import (
    _,
    bot,
)
from utils.db_api import (
    db_commands,
)


class LinkCheckMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict) -> None:
        if isinstance(message.chat.type, types.ChatType):
            await self._check_links_and_handle(message.from_user.id, obj=message)

    async def on_process_callback_query(
            self, call: types.CallbackQuery, data: dict
    ) -> None:
        await self._check_links_and_handle(call.from_user.id, obj=call)

    @staticmethod
    async def _check_links_and_handle(
            user_id: int, obj: Union[types.CallbackQuery, types.Message]
    ) -> NoReturn:
        links_db = await db_commands.select_all_links()
        subscribed_links = set()

        async def check_subscription(link_id):
            check = await bot.get_chat_member(chat_id=link_id, user_id=user_id)
            return check.status != "left"

        for link in links_db:
            if await check_subscription(link["telegram_link_id"]):
                subscribed_links.add(link["telegram_link_id"])
        text, markup = _(
            "Вы подписались не на все каналы! Чтобы продолжить пользоваться ботом, "
            "подпишитесь! Ссылки ниже: "
        ), await necessary_links_keyboard(
            telegram_id=user_id,
            links_db=links_db,
        )
        if (
                len(subscribed_links) != len(links_db)
                and obj.from_user.id not in load_config().tg_bot.admin_ids
        ):
            try:
                await obj.answer(text=text, reply_markup=markup)
            except TypeError:
                await obj.message.answer(text=text, reply_markup=markup)
            await asyncio.sleep(1)
            raise CancelHandler()
