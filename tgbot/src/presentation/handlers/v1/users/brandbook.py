from aiogram.types import (
    CallbackQuery,
)

from functions.main_app.auxiliary_tools import (
    handle_guide_callback,
    information_menu,
    send_photo_with_caption,
)
from keyboards.inline.back_inline import (
    only_back_keyboard,
)
from keyboards.inline.guide_inline import (
    guide_callback,
)
from loader import (
    _,
    dp,
)


@dp.callback_query_handler(text="information")
async def get_information(call: CallbackQuery):
    await information_menu(call)


@dp.callback_query_handler(text="guide")
async def get_guide(call: CallbackQuery) -> None:
    await send_photo_with_caption(
        call=call,
        photo=r"brandbook/1_page.png",
        caption=_("Руководство по боту: \n<b>Страница №1</b>"),
        step=1,
        total_steps=4,
    )


@dp.callback_query_handler(guide_callback.filter(action=["forward", "backward"]))
async def get_forward(call: CallbackQuery, callback_data: dict) -> None:
    await handle_guide_callback(call, callback_data)


@dp.callback_query_handler(text="contacts")
async def contacts_menu(call: CallbackQuery):
    await call.message.edit_text(
        text=(
            "📧 Добро пожаловать в наш раздел контактной информации платформы:\n\n"
            "Наш сайт: В разработке"
        ),
        reply_markup=await only_back_keyboard(menu="information"),
    )
