from aiogram.dispatcher.filters.state import (
    State,
    StatesGroup,
)


class AdminsActions(StatesGroup):
    add = State()
    delete = State()
