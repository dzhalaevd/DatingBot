from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)




def information_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    guide = InlineKeyboardButton(text=_("📚 Брендбук"), callback_data="guide")
    contacts = InlineKeyboardButton(text=_("📞 Контакты"), callback_data="contacts")
    language = InlineKeyboardButton(text=_("🌐 Язык"), callback_data="language_info")
    back_to_menu = InlineKeyboardButton(
        text=_("⏪️ Вернуться в меню"), callback_data="start_menu"
    )
    markup.add(language)
    markup.row(guide, contacts)
    markup.add(back_to_menu)
    return markup
