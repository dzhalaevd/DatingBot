from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)




def location_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    send_location = KeyboardButton(
        text=_("🗺 Определить автоматически"), request_location=True
    )
    markup.add(send_location)
    return markup
