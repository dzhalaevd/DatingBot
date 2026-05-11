from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import (
    CallbackData,
)

manipulation_callback = CallbackData("user_callback", "action", "value")


def user_manipulation() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    find_user = InlineKeyboardButton(_("🔍 Найти пользователя"), callback_data="db:search_user")
    markup.add(find_user)
    return markup


def user_blocking_keyboard(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    if is_banned:
        button = InlineKeyboardButton(
            _("🟢 Разблокировать"),
            callback_data=manipulation_callback.new(action="unban", value=f"{user_id}"),
        )
    else:
        button = InlineKeyboardButton(
            _("🚫 Заблокировать"),
            callback_data=manipulation_callback.new(action="ban", value=f"{user_id}"),
        )
    markup.add(button)
    return markup
