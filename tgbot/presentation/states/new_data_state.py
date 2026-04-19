from aiogram.dispatcher.filters.state import (
    State,
    StatesGroup,
)


class NewData(StatesGroup):
    sex = State()
    commentary = State()
    name = State()
    need_partner_sex = State()
    age = State()
    city = State()
    nationality = State()
    education = State()
    town = State()
    car = State()
    own_home = State()
    hobbies = State()
    child = State()
    marital = State()
    photo = State()
