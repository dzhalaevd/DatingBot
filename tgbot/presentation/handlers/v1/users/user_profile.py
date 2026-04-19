from aiogram.types import (
    CallbackQuery,
)

from functions.main_app.auxiliary_tools import (
    display_profile,
)
from handlers.users.back import (
    delete_message,
)
from keyboards.inline.menu_profile_inline import (
    get_profile_keyboard,
)
from loader import (
    _,
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.callback_query_handler(text="my_profile")
async def my_profile_menu(call: CallbackQuery) -> None:
    telegram_id = call.from_user.id
    await delete_message(call.message)
    user_db = await db_commands.select_user(telegram_id=telegram_id)
    markup = await get_profile_keyboard(verification=user_db.verification)
    await display_profile(call, markup)


@dp.callback_query_handler(text="disable")
async def disable_profile(call: CallbackQuery) -> None:
    await db_commands.update_user_data(telegram_id=call.from_user.id, status=False)
    await delete_message(call.message)
    await call.message.answer(_("Ваша анкета удалена!\nЯ надеюсь вы кого-нибудь нашли"))
