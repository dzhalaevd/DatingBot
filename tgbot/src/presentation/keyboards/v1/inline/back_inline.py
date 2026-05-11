from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def only_back_keyboard(menu: str = "start_menu") -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton(text=_("⏪️ Вернуться в меню"), callback_data=menu)
    markup.add(back)
    return markup
