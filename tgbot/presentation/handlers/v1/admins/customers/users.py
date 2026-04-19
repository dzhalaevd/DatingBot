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
from keyboards.admin.inline.customers import (
    manipulation_callback,
    user_blocking_keyboard,
    user_manipulation,
)
from keyboards.admin.inline.reply_menu import (
    admin_cancel_keyboard,
)
from loader import (
    dp,
)
from utils.db_api import (
    db_commands,
)


@dp.message_handler(IsAdmin(), commands="users", state="*")
@dp.message_handler(IsAdmin(), text="🫂 Пользователи", state="*")
async def command_start(message: Message, state: FSMContext):
    await state.reset_state()
    text = "<u>🫂 Пользователи</u>"
    await message.answer(text, reply_markup=await user_manipulation())


@dp.callback_query_handler(text="db:search_user")
async def search_users(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "<b>🔍 Введите @username или telegram id: </b>",
        reply_markup=await admin_cancel_keyboard(),
    )
    await state.set_state("search_user")


@dp.message_handler(IsAdmin(), state="search_user")
async def search_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        user = await db_commands.select_user(int(message.text))
    else:
        username = message.text[1:] if message.text[0] == "@" else message.text
        user = await db_commands.select_user_username(username)

    if user:
        text = (
            f"<b>ℹ️ Пользователь: </b><code>{user.telegram_id}</code>\n\n"
            f"<b>👤 Полное имя: </b><code>{user.varname}</code>\n"
            f"<b>🚹 Юзернейм: </b><code>{user.username}</code>\n"
            f"<b>📅 Дата регистрации в боте: </b><code>{user.created_at.date()}</code>\n"
        )

        await message.answer_photo(
            photo=user.photo_id,
            caption=text,
            reply_markup=await user_blocking_keyboard(
                user_id=user.telegram_id, is_banned=user.is_banned
            ),
        )

    else:
        await message.answer(
            "🔍 Пользователь не найден!", reply_markup=await user_manipulation()
        )
    await state.reset_state()


@dp.callback_query_handler(
    IsAdmin(), manipulation_callback.filter(action=["ban", "unban"])
)
async def ban_user_handler(call: CallbackQuery, callback_data: dict):
    user_id = int(callback_data.get("value"))
    action = callback_data.get("action")

    is_banned = action == "ban"
    await db_commands.update_user_data(telegram_id=user_id, is_banned=is_banned)
    reply_markup = await user_blocking_keyboard(user_id=user_id, is_banned=is_banned)
    await call.message.edit_reply_markup(reply_markup=reply_markup)
