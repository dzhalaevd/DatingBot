import random
from typing import (
    Optional,
    Union,
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import (
    CallbackData,
)

from data.config import (
    load_config,
)
from loader import (
    _,
    dp,
)

support_callback = CallbackData("ask_support", "messages", "user_id", "as_user")
cancel_support_callback = CallbackData("cancel_support", "user_id")


def check_support_available(support_id) -> int | None:
    state = dp.current_state(chat=support_id, user=support_id)
    state_str = str(await state.get_state())
    if state_str == "in_support":
        return
    else:
        return support_id


def get_support_manager() -> int | None:
    random.shuffle(load_config().tg_bot.support_ids)
    for support_id in load_config().tg_bot.support_ids:
        support_id = await check_support_available(support_id)
        if support_id:
            return support_id
    else:
        return


def support_keyboard(messages, user_id=None) -> bool | InlineKeyboardMarkup:
    if user_id:
        contact_id = int(user_id)
        as_user = "no"
        text = _("Ответить пользователю")

    else:
        contact_id = await get_support_manager()
        as_user = "yes"
        if messages == "many" and contact_id is None:
            return False

        text = _("Написать оператору")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=text,
            callback_data=support_callback.new(
                messages=messages, user_id=contact_id, as_user=as_user
            ),
        )
    )

    if messages == "many":
        keyboard.add(
            InlineKeyboardButton(
                text=_("Завершить сеанс"),
                callback_data=cancel_support_callback.new(user_id=contact_id),
            )
        )
    return keyboard


def cancel_support(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Завершить сеанс"),
                    callback_data=cancel_support_callback.new(user_id=user_id),
                )
            ]
        ]
    )
