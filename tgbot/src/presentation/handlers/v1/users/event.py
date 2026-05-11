import datetime

from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    ContentType,
    Message,
)
from aiogram.utils.exceptions import (
    BadRequest,
    MessageNotModified,
    MessageToEditNotFound,
)
from django.db import (
    DataError,
)

from data.config import (
    load_config,
)
from functions.event.extra_features import (
    check_event_date,
)
from functions.event.templates_messages import (
    ME,
)
from functions.main_app.determin_location import (
    EventStrategy,
    Location,
)
from keyboards.inline.calendar import (
    SimpleCalendar,
    calendar_callback,
    search_cb,
)
from keyboards.inline.poster_inline import (
    cancel_registration_keyboard,
    poster_keyboard,
)
from loader import (
    _,
    bot,
    dp,
    logger,
)
from utils.YandexMap import (
    NothingFound,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="meetings")
async def view_meetings_handler(call: CallbackQuery) -> None:
    markup = await poster_keyboard(obj=call)
    try:
        await check_event_date(call.from_user.id)
    except TypeError:
        pass
    text = _("Вы перешли в меню афиш")
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except MessageToEditNotFound:
        await call.message.answer(text, reply_markup=markup)
    except BadRequest:
        await call.message.answer(text, reply_markup=markup)


@dp.callback_query_handler(text="create_poster")
async def registrate_poster_name(call: CallbackQuery, state: FSMContext) -> None:
    user = await db_commands.select_user_meetings(telegram_id=call.from_user.id)
    moderation_process = user.moderation_process
    markup = await poster_keyboard(obj=call)

    if not moderation_process:
        await call.message.edit_text(
            text=_("Введите название мероприятие"),
            reply_markup=await cancel_registration_keyboard(),
        )
        await state.set_state("register_handler_name")
    else:
        try:
            await call.message.edit_text(
                text=_(
                    "Вы уже создали мероприятие, которое проходит модерацию."
                    " Дождитесь проверки, пожалуйста"
                ),
                reply_markup=markup,
            )
        except MessageNotModified:
            await call.answer(
                text=_(
                    "Прочитайте сообщение и не нажимайте на кнопку,"
                    " пока ваше мероприятие не пройдет модерацию"
                ),
                show_alert=True,
            )


@dp.message_handler(state="register_handler_name")
async def simple_calendar(message: Message) -> None:
    try:
        await db_commands.update_user_meetings_data(
            telegram_id=message.from_user.id, event_name=message.text
        )
        await message.answer(
            text=_("Пожалуйста, выберите дату: "),
            reply_markup=await SimpleCalendar().start_calendar(),
        )
    except DataError:
        await message.answer(
            text=_(
                "Длинна вашего сообщение превышает допустимую.\n" "Попробуйте ещё раз"
            )
        )


@dp.callback_query_handler(calendar_callback.filter(), state="register_handler_name")
async def process_simple_calendar(
        call: CallbackQuery, callback_data, state: FSMContext
) -> None:
    try:
        selected, date = await SimpleCalendar().process_selection(call, callback_data)
        now = datetime.datetime.now()

        if now >= date:
            await call.message.edit_text(
                text=_("Вы не можете проводить мероприятие в прошлом")
            )
            await simple_calendar(call.message)
            return
        if selected:
            await call.message.edit_text(
                text=_("Теперь напишите место проведения"),
                reply_markup=await cancel_registration_keyboard(),
            )
            await db_commands.update_user_meetings_data(
                telegram_id=call.from_user.id, time_event=date.strftime("%d-%m-%Y")
            )
        else:
            return
        await state.set_state("register_handler_place")
    except TypeError as ex:
        logger.error(f"Error in process_simple_calendar. {ex}")


@dp.message_handler(state="register_handler_place")
async def send_city(message: types.Message) -> None:
    try:
        if len(message.text) <= 25:
            loc = await Location(message=message, strategy=EventStrategy)
            await loc.det_loc()
        else:
            await message.answer(
                text=_("Вы ввели слишком длинное название города" "Попробуйте ещё раз.")
            )
            return
    except NothingFound as ex:
        logger.error(f"Error in send_city. {ex}")
        await message.answer(
            text=_(
                "Произошла неизвестная ошибка! Попробуйте еще раз.\n"
                "Вероятнее всего вы ввели город неправильно"
            )
        )


@dp.callback_query_handler(text="yes_all_good", state="register_handler_place")
async def registrate_poster_commentary(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text=_(
            "Хорошо, теперь напишите короткое или длинное описание вашего мероприятия"
        ),
        reply_markup=await cancel_registration_keyboard(),
    )

    await state.set_state("register_handler_commentary")


@dp.message_handler(state="register_handler_commentary")
async def registrate_poster(message: Message, state: FSMContext) -> None:
    try:
        await db_commands.update_user_meetings_data(
            telegram_id=message.from_user.id, commentary=message.text
        )
        await message.answer(
            text=_("И напоследок, пришлите постер вашего мероприятия"),
            reply_markup=await cancel_registration_keyboard(),
        )
    except DataError as ex:
        logger.error(f"Error in registrate_poster_commentary {ex}")
        await message.answer(
            text=_("Ваше сообщение слишком длинное." "Попробуйте написать короче")
        )

    await state.set_state("register_handler_poster")


@dp.message_handler(content_types=ContentType.PHOTO, state="register_handler_poster")
async def finish_registration(message: Message, state: FSMContext) -> None:
    user = await db_commands.select_user_meetings(telegram_id=message.from_user.id)
    photo_id = message.photo[-1].file_id
    markup = await poster_keyboard(obj=message)
    await db_commands.update_user_meetings_data(
        telegram_id=message.from_user.id, photo_id=photo_id
    )
    await message.answer(text=_("Фото принято"))

    await state.finish()

    document = {
        "telegram_id": message.from_user.id,
        "title": user.event_name,
        "date": user.time_event,
        "place": user.venue,
        "description": user.commentary,
        "photo_id": photo_id,
    }
    await db_commands.update_user_meetings_data(
        telegram_id=message.from_user.id, moderation_process=True
    )
    await ME.send_event_message(
        text=document,
        bot=bot,
        chat_id=load_config().tg_bot.moderate_chat,
        moderate=True,
    )
    await message.answer(
        text=_("Ваше мероприятие отправлено на модерацию"), reply_markup=markup
    )


@dp.callback_query_handler(text="my_event")
async def view_own_event(call: CallbackQuery) -> None:
    user = await db_commands.select_user_meetings(telegram_id=call.from_user.id)

    document = {
        "title": user.event_name,
        "date": user.time_event,
        "place": user.venue,
        "description": user.commentary,
        "photo_id": user.photo_id,
    }
    await ME.send_event_message(
        text=document, bot=bot, chat_id=call.from_user.id, moderate=False, call=call
    )


@dp.callback_query_handler(
    search_cb.filter(action=["cancel"]), state="register_handler_name"
)
@dp.callback_query_handler(text="cancel_registration", state="register_handler_name")
@dp.callback_query_handler(text="cancel_registration", state="register_handler_poster")
@dp.callback_query_handler(text="cancel_registration", state="register_handler_place")
@dp.callback_query_handler(
    text="cancel_registration", state="register_handler_commentary"
)
async def cancel_register_poster_name(call: CallbackQuery, state: FSMContext) -> None:
    await state.reset_state()
    await view_meetings_handler(call)
