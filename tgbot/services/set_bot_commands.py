import logging

from aiogram import (
    Bot,
    types,
)


async def set_user_commands(
        bot: Bot, user_id: int, commands: list[types.BotCommand]
) -> None:
    try:
        await bot.set_my_commands(
            commands=commands, scope=types.BotCommandScopeChat(chat_id=user_id)
        )
    except Exception as ex:
        logging.error(f"{user_id}: Commands are not installed. {ex}")


async def set_default_commands(bot: Bot, admin_ids: list[int]) -> None:
    default_commands = [
        types.BotCommand(command="start", description="🟢 Запустить бота"),
    ]

    await bot.set_my_commands(default_commands, scope=types.BotCommandScopeDefault())
