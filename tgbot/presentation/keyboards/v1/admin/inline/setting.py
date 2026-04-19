from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)




def add_admins_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    add = InlineKeyboardButton(_("*️⃣ Добавить"), callback_data="admin:admins:add")
    delete = InlineKeyboardButton(_("❌ Удалить"), callback_data="admin:admins:delete")
    back = InlineKeyboardButton(_("◀️ Назад"), callback_data="admin:settings")
    markup.add(add, delete)
    markup.add(back)
    return markup
