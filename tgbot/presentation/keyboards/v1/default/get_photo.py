from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)




def get_photo_from_profile() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    send_photo = KeyboardButton(text=_("Взять из профиля"))
    markup.add(send_photo)
    return markup
