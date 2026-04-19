import aiogram
from aiogram import (
    types,
)
from aiogram.dispatcher.filters.builtin import (
    CommandStart,
)
from aiogram.types import (
    CallbackQuery,
)
from aiogram.utils.exceptions import (
    BadRequest,
)

from filters import (
    IsPrivate,
)
from functions.main_app.auxiliary_tools import (
    check_user_in_db,
    delete_message,
    registration_menu,
)
from keyboards.inline.language_inline import (
    language_keyboard,
)
from loader import (
    _,
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.message_handler(IsPrivate(), CommandStart())
async def register_user(message: types.Message) -> None:
    username = message.from_user.username if message.from_user.username else ""
    telegram_id = message.from_user.id
    await check_user_in_db(message=message, username=username, telegram_id=telegram_id)
    try:
        await registration_menu(message)
    except TypeError:
        await message.answer(
            text=_("Вам необходимо зарегистрировать агента(ов) тех поддержки")
        )


@dp.callback_query_handler(text="start_menu")
async def start_menu(call: CallbackQuery) -> None:
    try:
        await registration_menu(call)
    except TypeError:
        await call.message.answer(_("Вас нет в базе данной"))


async def choice_language(call: CallbackQuery, menu: str) -> None:
    try:
        await call.message.edit_text(
            text=_("Выберите язык"), reply_markup=await language_keyboard(menu)
        )
    except BadRequest:
        await delete_message(call.message)
        await call.message.answer(
            text=_("Выберите язык"), reply_markup=await language_keyboard(menu)
        )


async def change_language(call: CallbackQuery, language: str) -> None:
    telegram_id = call.from_user.id
    try:
        await db_commands.update_user_data(telegram_id=telegram_id, language=language)

        await call.message.edit_text(
            text=_("Язык был успешно изменен. Введите команду /start", locale=language)
        )
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        await call.message.edit_text(
            text=_(
                "Произошла какая-то ошибка. Введите команду /start и попробуйте еще раз"
            )
        )


language_codes = {
    "Russian": "ru",
    "Deutsch": "de",
    "English": "en",
    "Indonesian": "in",
}

language_menus = {
    "language_reg": "registration",
    "language_info": "information",
}


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable,PyShadowingNames
def register_callbacks(callback_dict, callback_function):
    for callback_text, value in callback_dict.items():
        dp.callback_query_handler(text=callback_text)(
            lambda call, value=value: callback_function(call, value)
        )


register_callbacks(language_codes, change_language)
register_callbacks(language_menus, choice_language)
