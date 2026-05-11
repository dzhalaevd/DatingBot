from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)




def start_monitoring_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    confirm_sending = InlineKeyboardButton(
        text=_("Подтвердить отправку"), callback_data="confirm_send_monitoring"
    )
    markup.add(confirm_sending)
    return markup


def tech_works_keyboard(tech_works: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    set_up_tech_work = InlineKeyboardButton(
        text=_("Включить"), callback_data="set_up_tech_work"
    )
    disable_technical_work = InlineKeyboardButton(
        text=_("Выключить"), callback_data="disable_tech_work"
    )
    if tech_works:
        markup.add(disable_technical_work)
        return markup
    else:
        markup.add(set_up_tech_work)
        return markup


def unban_user_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    unban_button = InlineKeyboardButton(_("Разблокировать"), callback_data="unban")
    markup.add(unban_button)
    return markup
