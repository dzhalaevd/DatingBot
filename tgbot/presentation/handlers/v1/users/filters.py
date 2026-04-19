import asyncio
import re

from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)
from aiogram.utils.exceptions import (
    BadRequest,
)

from functions.main_app.auxiliary_tools import (
    choice_gender,
    show_dating_filters,
)
from functions.main_app.determin_location import (
    FiltersStrategy,
    Location,
)
from handlers.users.back import (
    delete_message,
)
from keyboards.inline.change_data_profile_inline import (
    gender_keyboard,
)
from keyboards.inline.filters_inline import (
    event_filters_keyboard,
    filters_keyboard,
)
from loader import (
    _,
    dp,
)
from tgbot.utils.YandexMap import (
    NothingFound,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="filters")
async def get_filters(call: CallbackQuery) -> None:
    try:
        await call.message.edit_text(
            text=_("Вы перешли в раздел с фильтрами"),
            reply_markup=await filters_keyboard(),
        )
    except BadRequest:
        await delete_message(message=call.message)
        await call.message.answer(
            text=_("Вы перешли в раздел с фильтрами"),
            reply_markup=await filters_keyboard(),
        )


@dp.callback_query_handler(text="dating_filters")
async def get_dating_filters(call: CallbackQuery) -> None:
    await show_dating_filters(obj=call)


@dp.callback_query_handler(text="user_age_period")
async def desired_age(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(text=_("Напишите минимальный возраст"))
    await state.set_state("age_period")


@dp.message_handler(state="age_period")
async def desired_min_age_state(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_min=int_messages
    )
    await message.answer(_("Теперь введите максимальный возраст"))
    await state.reset_state()
    await state.set_state("max_age_period")


@dp.message_handler(state="max_age_period")
async def desired_max_age_state(message: types.Message, state: FSMContext) -> None:
    messages = message.text
    int_message = re.findall("[0-9]+", messages)
    int_messages = "".join(int_message)
    await db_commands.update_user_data(
        telegram_id=message.from_user.id, need_partner_age_max=int_messages
    )
    await state.finish()
    await show_dating_filters(obj=message)


@dp.callback_query_handler(text="user_need_gender")
async def desired_max_range(call: CallbackQuery, state: FSMContext) -> None:
    markup = await gender_keyboard(
        m_gender=_("👱🏻‍♂️ Парня"), f_gender=_("👱🏻‍♀️ Девушку")
    )
    await call.message.edit_text(
        _("Выберите, кого вы хотите найти:"), reply_markup=markup
    )
    await state.set_state("gender")


@dp.callback_query_handler(state="gender")
async def desired_gender(call: CallbackQuery, state: FSMContext) -> None:
    await choice_gender(call)
    await call.message.edit_text(_("Данные сохранены"))
    await asyncio.sleep(1)
    await show_dating_filters(obj=call)
    await state.finish()


@dp.callback_query_handler(text="needs_city")
async def user_city_filter(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(_("Напишите город вашего будущего партнера"))
    await state.set_state("city")


@dp.callback_query_handler(text="yes_all_good", state="set_city_event")
@dp.callback_query_handler(text="yes_all_good", state="city")
async def get_hobbies(call: CallbackQuery, state: FSMContext) -> None:
    await asyncio.sleep(1)
    await call.message.edit_text(_("Данные сохранены"))
    await asyncio.sleep(2)
    if await state.get_state() == "city":
        await show_dating_filters(obj=call)
    else:
        await get_event_filters(call)

    await state.finish()


@dp.callback_query_handler(text="event_filters")
async def get_event_filters(call: CallbackQuery) -> None:
    await call.message.edit_text(
        _("Вы перешли в меню настроек фильтров для мероприятий"),
        reply_markup=await event_filters_keyboard(),
    )


@dp.callback_query_handler(text="city_event")
async def set_city_by_filter(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        _("Напишите город, в котором бы хотели сходить куда-нибудь")
    )
    await state.set_state("set_city_event")


@dp.message_handler(state="city")
async def user_city_filter_state(message: types.Message) -> None:
    try:
        loc = await Location(message=message, strategy=FiltersStrategy)
        await loc.det_loc()

    except NothingFound:
        await message.answer(_("Произошла ошибка, попробуйте еще раз"))
        return
