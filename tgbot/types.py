from typing import (
    Any,
    Awaitable,
    Callable,
)

from aiogram.types import (
    TelegramObject,
)

Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]
