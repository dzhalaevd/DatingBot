from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    Message,
)

from filters.IsAdminFilter import (
    IsAdmin,
)
from keyboards.admin.main_menu import (
    admin_keyboard,
)
from keyboards.inline.admin_inline import (
    tech_works_keyboard,
)
from loader import (
    _,
    dp,
)
from utils.db_api import (
    db_commands,
)
from utils.statistics import (
    get_statistics,
)


@dp.message_handler(IsAdmin(), commands="admin", state="*")
async def command_start(message: Message, state: FSMContext):
    await state.finish()
    text = await get_statistics(message)
    markup = await admin_keyboard()
    await message.answer(text=text, reply_markup=markup)


@dp.message_handler(IsAdmin(), text="🛑 Тех.Работа")
async def tech_works_menu(message: Message) -> None:
    settings = await db_commands.select_setting(message.from_user.id)
    tech_works = settings.technical_works

    await message.answer(
        text=_("Чтобы включить/выключить технические работы, нажмите на кнопку ниже"),
        reply_markup=await tech_works_keyboard(tech_works=tech_works),
    )


@dp.callback_query_handler(text="set_up_tech_work")
async def set_up_tech_works(call: CallbackQuery) -> None:
    await db_commands.update_setting(
        telegram_id=call.from_user.id, technical_works=True
    )
    await call.message.edit_text(text=_("Технические работы включены"))


@dp.callback_query_handler(text="disable_tech_work")
async def turn_off_tech_works(call: CallbackQuery) -> None:
    await db_commands.update_setting(
        telegram_id=call.from_user.id, technical_works=False
    )
    await call.message.edit_text(text=_("Технические работы выключены"))
