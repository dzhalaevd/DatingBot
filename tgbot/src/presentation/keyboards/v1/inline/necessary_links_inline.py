from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def necessary_links_keyboard(telegram_id, links_db):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in links_db:
        btn = InlineKeyboardButton(text=i["title"], url=i["link"])
        markup.add(btn)
    return markup
