from aiogram.utils.exceptions import (
    CantDemoteChatCreator,
    CantParseEntities,
    InvalidQueryID,
    MessageCantBeDeleted,
    MessageNotModified,
    MessageTextIsEmpty,
    MessageToDeleteNotFound,
    RetryAfter,
    TelegramAPIError,
    Unauthorized,
)
from loader import (
    dp,
)


@dp.errors_handler()
async def errors_handler(update, exception):
    if (
        isinstance(exception, CantDemoteChatCreator)
        or isinstance(exception, MessageNotModified)
        or isinstance(exception, MessageCantBeDeleted)
        or isinstance(exception, MessageToDeleteNotFound)
        or isinstance(exception, MessageTextIsEmpty)
        or isinstance(exception, Unauthorized)
        or isinstance(exception, InvalidQueryID)
        or isinstance(exception, TelegramAPIError)
        or isinstance(exception, RetryAfter)
        or isinstance(exception, CantParseEntities)
    ):
        return True
