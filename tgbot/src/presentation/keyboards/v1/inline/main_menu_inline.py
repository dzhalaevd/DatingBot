from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from data.config import (
    load_config,
)
from utils.db_api import (
    db_commands,
)


def start_keyboard(obj: CallbackQuery | Message | int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    try:
        user_db = await db_commands.select_user(telegram_id=obj.from_user.id)
    except AttributeError:
        user_db = await db_commands.select_user(telegram_id=obj)
    status = user_db.status
    support_ids = load_config().tg_bot.support_ids[0]
    registration = InlineKeyboardButton(text=_("➕ Регистрация"), callback_data="registration")
    language = InlineKeyboardButton(text=_("🌐 Язык"), callback_data="language_reg")
    my_profile = InlineKeyboardButton(text=_("👤 Моя анкета"), callback_data="my_profile")
    filters = InlineKeyboardButton(text=_("⚙️ Фильтры"), callback_data="filters")
    view_ques = InlineKeyboardButton(text=_("💌 Найти пару"), callback_data="find_ques")
    meetings = InlineKeyboardButton(text=_("🗓️ Афиша"), callback_data="meetings")
    support = InlineKeyboardButton(text=_("🆘 Поддержка"), callback_data="support")
    information = InlineKeyboardButton(text=_("ℹ️ Информация"), callback_data="information")
    if not status:
        markup.row(registration)
        markup.row(support, information)
        markup.row(language)
    else:
        markup.row(my_profile)
        markup.row(view_ques, meetings)
        markup.row(information, filters)
        try:
            if support_ids != obj.from_user.id:
                markup.row(support)
        except AttributeError:
            if support_ids != obj:
                markup.row(support)
    return markup
