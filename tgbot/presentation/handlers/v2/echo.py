from aiogram import (
    Router,
    types,
)

echo_router = Router()


@echo_router.message()
async def echo_handler(message: types.Message) -> None:
    text = (
        "Я не понимаю эту команду."
        " Введите /start для дополнительной информации."
    )
    await message.answer(text=text)
