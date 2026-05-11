from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import (
    CallbackData,
)

guide_callback = CallbackData("guide_callback", "action", "value")


def create_pagination_keyboard(step: int, total_steps: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    if step > 1:
        backward = InlineKeyboardButton(
            text=_("⏪️ Назад"),
            callback_data=guide_callback.new(action="backward", value=step - 1),
        )
        markup.insert(backward)
    if step < total_steps:
        forward = InlineKeyboardButton(
            text=_("Вперед ➡️"),
            callback_data=guide_callback.new(action="forward", value=step + 1),
        )
        markup.insert(forward)
    back = InlineKeyboardButton(text=_("❌ Закрыть"), callback_data="back_to_info_menu")
    markup.add(back)
    return markup
