from aiogram.dispatcher.filters import (
    Command,
)
from aiogram.types import (
    Message,
)

from filters.FiltersChat import (
    IsGroup,
)
from filters.IsAdminFilter import (
    IsAdmin,
)
from loader import (
    _,
    dp,
)


@dp.message_handler(IsGroup(), IsAdmin(), Command("start"))
async def start_group_handler(message: Message) -> None:
    await message.answer(
        text=_(
            "<b>Привет, я бот, проекта Que Group, для верификации анкет для знакомств</b>\n\n"
        )
    )
