from collections.abc import Awaitable, Callable
from typing import (
    Any,
)

from aiogram.types import (
    TelegramObject,
)

Handler = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]
