import random

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from functions.event.extra_features import (
    create_form,
    get_next_registration,
)
from loader import (
    _,
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="my_appointment")
async def get_event_list(call: CallbackQuery, state: FSMContext) -> None:
    try:
        telegram_id = call.from_user.id
        event_list = await get_next_registration(call.from_user.id)
        random_event = random.choice(event_list)
        await create_form(
            form_owner=random_event, chat_id=telegram_id, call=call, view=False
        )
        await state.set_state("cancel_record")
    except IndexError:
        await call.answer(
            _("На данный момент вы никуда не записались"), show_alert=True
        )


@dp.callback_query_handler(
    lambda call: call.data.split("-")[0] == "cancel", state="cancel_record"
)
async def list_poster_reaction(call: CallbackQuery, state: FSMContext) -> None:
    call_data = call.data.split("-")

    if call_data[0] == "cancel":
        await db_commands.remove_events_from_user(call.from_user.id, call_data[1])
        await get_event_list(call, state)
