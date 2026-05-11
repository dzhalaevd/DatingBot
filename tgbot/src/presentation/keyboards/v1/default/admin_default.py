from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def admin_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    mailing = KeyboardButton(text=_("Рассылка"))
    message_by_id = KeyboardButton(text=_("Сообщение по id"))
    count_people_and_chat = KeyboardButton(text=_("Посчитать людей и чаты"))
    monitoring = KeyboardButton(text=_("Мониторинг"))
    set_up_technical_works = KeyboardButton(text=_("Тех.Работа"))
    markup.row(mailing, message_by_id)
    markup.row(count_people_and_chat, monitoring)
    markup.add(set_up_technical_works)
    return markup
