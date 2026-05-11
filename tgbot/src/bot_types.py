from typing import (
    Any,
)

from collections.abc import Awaitable, Callable

from aiogram.types import (
    TelegramObject,
)

Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]
