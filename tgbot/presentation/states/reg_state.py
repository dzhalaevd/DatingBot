from aiogram.dispatcher.filters.state import (
    State,
    StatesGroup,
)


class RegData(StatesGroup):
    sex = State()
    commentary = State()
    name = State()
    need_partner_sex = State()
    age = State()
    nationality = State()
    education = State()
    town = State()
    car = State()
    own_home = State()
    hobbies = State()
    child = State()
    marital = State()
    photo = State()
