from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
)

from aiogram.dispatcher.middlewares import (
    BaseMiddleware,
)
from aiogram.types.base import (
    TelegramObject,
)
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        super(SchedulerMiddleware, self).__init__()
        self.scheduler = scheduler

    def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        data["appscheduler"] = self.scheduler
        return handler(event, data)
