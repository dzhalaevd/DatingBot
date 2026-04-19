from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)




def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    cancel_button = InlineKeyboardButton(
        _("🙅🏻‍♂️ Отменить"), callback_data="admin:cancel"
    )
    markup.add(cancel_button)
    return markup


def settings_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    admins = InlineKeyboardButton(_("👮‍♂️ Админ Состав"), callback_data="admin:admins")
    change_contact = InlineKeyboardButton(
        _("📞 Сменить контакты"), callback_data="admin:change_contacts"
    )
    markup.add(admins, change_contact)

    return markup


def logs_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    upload_users_txt = InlineKeyboardButton(
        _("🗒 Выгрузить юзеров | .txt"), callback_data="owner:backup:users:txt"
    )
    upload_logs = InlineKeyboardButton(
        _("🗒 Выгрузить конфиги и логи"), callback_data="owner:backup:configs"
    )
    markup.add(upload_users_txt)
    markup.add(upload_logs)
    return markup
