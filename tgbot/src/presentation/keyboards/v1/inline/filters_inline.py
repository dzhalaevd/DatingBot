from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    event_filters = InlineKeyboardButton(text=_("🎉 Мероприятия"), callback_data="event_filters")
    dating_filters = InlineKeyboardButton(text=_("❤️ Знакомства"), callback_data="dating_filters")
    back = InlineKeyboardButton(text=_("⏪️ Назад"), callback_data="back_with_delete")
    markup.row(event_filters, dating_filters)
    markup.add(back)
    return markup


def dating_filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    user_need_city = InlineKeyboardButton(text=_("🏙️ Город партнера"), callback_data="needs_city")
    user_age_period = InlineKeyboardButton(text=_("🔞 Возр.диапазон"), callback_data="user_age_period")
    user_need_gender = InlineKeyboardButton(text=_("🚻 Пол партнера"), callback_data="user_need_gender")
    back = InlineKeyboardButton(text=_("⏪️ Назад"), callback_data="back_to_filter_menu")
    markup.add(user_need_city)
    markup.row(user_need_gender, user_age_period)
    markup.add(back)
    return markup


def event_filters_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    city_event = InlineKeyboardButton(text=_("🏙️ Город"), callback_data="city_event")
    back = InlineKeyboardButton(text=_("⏪️ Вернуться в меню"), callback_data="back_to_filter_menu")
    markup.add(city_event)
    markup.add(back)
    return markup
