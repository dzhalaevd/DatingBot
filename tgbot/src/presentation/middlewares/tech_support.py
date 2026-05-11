from typing import (
    Any,
)

from aiogram import (
    BaseMiddleware,
)
from aiogram.types import (
    TelegramObject,
)
from bot_types import (
    Handler,
)


class SupportMiddleware(BaseMiddleware):
    async def __call__(self, handler: Handler, event: TelegramObject, data: dict[str, Any]) -> Any:
        pass
        # dispatcher = Dispatcher.get_current()
        # state = dispatcher.current_state(
        #     chat=message.from_user.id, user=message.from_user.id
        # )
        #
        # state_str = str(await state.get_state())
        # if state_str == "in_support":
        #     data = await state.get_data()
        #     second_id = data.get("second_id")
        #     await message.copy_to(second_id)
        #
        #     raise CancelHandler()
