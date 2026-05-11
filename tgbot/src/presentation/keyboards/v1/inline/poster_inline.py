from typing import (
    Union,
)

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


from utils.db_api import (
    db_commands,
)


def poster_keyboard(obj: Message | CallbackQuery) -> InlineKeyboardMarkup:
    user = await db_commands.select_user_meetings(telegram_id=obj.from_user.id)
    is_admin = user.is_admin
    is_verification = user.verification_status
    moderation_process = user.moderation_process
    markup = InlineKeyboardMarkup(row_width=1)
    create_poster = InlineKeyboardButton(
        text=_("✍️Создать афишу"), callback_data="create_poster"
    )
    view_poster = InlineKeyboardButton(
        text=_("🎭 Смотреть афиши"), callback_data="view_poster"
    )
    my_appointment = InlineKeyboardButton(
        text=_("📝 Мои записи"), callback_data="my_appointment"
    )
    my_event = InlineKeyboardButton(text=_("📃 Моё событие"), callback_data="my_event")
    back = InlineKeyboardButton(
        text=_("⏪️ Вернуться в меню"), callback_data="start_menu"
    )

    if is_verification and is_admin and not moderation_process:
        markup_items = [my_event, view_poster, my_appointment, back]
    else:
        markup_items = [create_poster, view_poster, my_appointment, back]

    markup.add(*markup_items)
    return markup


def event_settings_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    change_data = InlineKeyboardButton(
        text=_("✍️ Изменить"), callback_data="change_event_data"
    )
    back = InlineKeyboardButton(
        text=_("⏪️ Вернуться в меню"), callback_data="event_menu"
    )
    markup.row(change_data)
    markup.add(back)
    return markup


def change_datas_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    title = InlineKeyboardButton(text=_("Название"), callback_data="change_title")
    description = InlineKeyboardButton(
        text=_("Описание"), callback_data="change_description"
    )
    back = InlineKeyboardButton(
        text=_("⏪️ Вернуться в меню"), callback_data="back_to_event_profile"
    )
    markup.row(title, description)
    markup.add(back)
    return markup


def create_moderate_ik(telegram_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    accept = InlineKeyboardButton(
        _("✅ Одобрить"), callback_data=f"moderate_accept-{telegram_id}"
    )
    reject = InlineKeyboardButton(
        _("❌ Отклонить"), callback_data=f"moderate_decline-{telegram_id}"
    )
    markup.row(accept, reject)
    return markup


def view_event_keyboard(telegram_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    meet = InlineKeyboardButton(
        _("Пойду!"), callback_data=f"answer_imgoing-{telegram_id}"
    )
    not_interested = InlineKeyboardButton(
        _("Не интересно"), callback_data=f"answer_notinteresting-{telegram_id}"
    )
    stopped = InlineKeyboardButton(
        text=_("⏪️ Остановить"), callback_data="answer_stopped_view"
    )
    markup.row(meet, not_interested)
    markup.add(stopped)
    return markup


def cancel_event_keyboard(telegram_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    backed_out = InlineKeyboardButton(
        _("❌ Отменить запись"), callback_data=f"cancel-{telegram_id}"
    )
    stopped = InlineKeyboardButton(_("⏪️ Остановить"), callback_data="go_out")
    markup.add(backed_out)
    markup.add(stopped)
    return markup


def cancel_registration_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    stopped = InlineKeyboardButton(
        _("⏪️ Остановить"), callback_data="cancel_registration"
    )
    markup.add(stopped)
    return markup
