from aiofiles import (
    os,
)
from aiogram.types import (
    CallbackQuery,
    InputFile,
    Message,
)

from filters.IsAdminFilter import (
    IsAdmin,
)
from functions.main_app.auxiliary_tools import (
    backup_configs,
    dump_users_to_file,
)
from handlers.users.back import (
    delete_message,
)
from keyboards.admin.inline.reply_menu import (
    logs_keyboard,
)
from loader import (
    dp,
)


@dp.message_handler(IsAdmin(), commands="logs", state="*")
@dp.message_handler(IsAdmin(), text="🗒 Логи", state="*")
async def command_start(message: Message):
    await message.answer("<u>🗒 Логи</u>", reply_markup=await logs_keyboard())


@dp.callback_query_handler(IsAdmin(), text="owner:backup:users:txt")
async def backup_users_handler(call: CallbackQuery):
    path = await dump_users_to_file()
    await delete_message(call.message)
    await call.message.answer_document(
        document=InputFile(path), caption="<b>🗒 Выгрузка пользователей в .txt</b>"
    )
    await os.remove(path)


@dp.callback_query_handler(IsAdmin(), text="owner:backup:configs")
async def backup_configs_handler(call: CallbackQuery):
    path = await backup_configs()
    await delete_message(call.message)
    await call.message.answer_document(
        InputFile(path), caption="<b>🗒 Выгрузка конфигов</b>"
    )
    await os.remove(path)
