from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from functions.event.extra_features import (
    add_events_to_user,
    check_event_date,
    create_form,
    get_next_random_event_id,
)
from keyboards.inline.poster_inline import (
    poster_keyboard,
)
from loader import (
    _,
    bot,
    dp,
)


@dp.callback_query_handler(text="view_poster")
async def view_poster_handler(call: CallbackQuery, state: FSMContext) -> None:
    telegram_id = call.from_user.id
    try:
        random_event = await get_next_random_event_id(telegram_id)
        await check_event_date(random_event)
        await create_form(form_owner=random_event, chat_id=telegram_id, call=call)
        await state.set_state("finding_event")
    except ValueError:
        await bot.edit_message_reply_markup(
            chat_id=telegram_id, message_id=call.message.message_id, reply_markup=None
        )
        await call.message.answer(
            _("На данный момент вы просмотрели все существующие анкеты"),
            reply_markup=await poster_keyboard(obj=call),
        )
        await state.reset_state()
    await state.reset_state()


@dp.callback_query_handler(
    lambda call: call.data.split("_")[0] == "answer", state="finding_event"
)
async def list_poster_reaction(call: CallbackQuery, state: FSMContext) -> None:
    call_data = call.data.split("-")

    if call_data[0] == "answer_notinteresting":
        await view_poster_handler(call, state)
    elif call_data[0] == "answer_imgoing":
        await add_events_to_user(call, event_id=int(call_data[1]))
        await view_poster_handler(call, state)
    elif call_data[0] == "answer_stopped_view":
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=await poster_keyboard(obj=call),
        )
        text = _(
            "Рад был помочь, {fullname}!\n" "Надеюсь, ты нашел кого-то благодаря мне"
        ).format(fullname=call.from_user.full_name)
        await call.answer(text)
        await state.reset_state(with_data=False)
