import asyncio

from aiogram import (
    types,
)
from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.markdown import (
    escape_md,
    quote_html,
)

from filters.IsAdminFilter import (
    IsAdmin,
)
from keyboards.admin.inline.mailing import (
    add_buttons_keyboard,
    confirm_with_button_keyboard,
)
from loader import (
    _,
    bot,
    dp,
    logger,
)
from utils.db_api import (
    db_commands,
)


@dp.message_handler(IsAdmin(), content_types=["text"], state="broadcast_get_content")
async def get_text_for_confirm(message: types.Message, state: FSMContext) -> None:
    text = message.md_text
    escape_md(text)
    await bot.send_message(
        chat_id=message.from_user.id,
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=await add_buttons_keyboard(),
    )
    await state.update_data(text=text)
    await state.set_state("broadcast_confirming")


@dp.callback_query_handler(state="broadcast_confirming")
async def broadcast_confirming(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(text=_("Начинаю рассылку!"))
    chats = await db_commands.select_all_users()
    count = 0
    async with state.proxy() as data:
        text = data["text"]
        if call.data == "confirm_send":
            for i in chats:
                try:
                    await bot.send_message(
                        chat_id=i.get("telegram_id"), text=text, parse_mode="MarkdownV2"
                    )
                    count += 1
                    await asyncio.sleep(1)
                except Exception as err:
                    logger.error(
                        _("Сообщение не дошло в чат {chat} Причина: \n{err}").format(
                            err=err, chat=(i.get("telegram_id"))
                        )
                    )

            await call.message.edit_text(
                text=_(
                    "Рассылка проведена успешно! Ее получили: {count} чатов!\n"
                ).format(count=count)
            )
            await state.reset_state(with_data=True)
        elif call.data == "add_buttons":
            await call.message.edit_text(text=_("Пришлите мне название кнопки!"))
            await state.set_state("get_button_name")


@dp.message_handler(IsAdmin(), state="get_button_name")
async def get_button_name(message: types.Message, state: FSMContext) -> None:
    button_name = message.text
    await state.update_data(button_name=button_name)
    await message.reply(
        text=_(
            "Название кнопки принято!" " Теперь отправьте мне ссылку для этой кнопки!"
        )
    )
    await state.set_state("get_button_url")


@dp.message_handler(IsAdmin(), state="get_button_url")
async def get_button_url(message: types.Message, state: FSMContext) -> None:
    button_url = message.text
    await state.update_data(button_url=button_url)
    async with state.proxy() as data:
        text = data["text"]
        button_name = data["button_name"]

    markup = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton(text=button_name, url=button_url)
    markup.add(btn)
    try:
        await message.answer(
            text=_("Вот так будет выглядеть сообщение: \n\n" "{text}\n\n").format(
                text=text
            ),
            reply_markup=markup,
            parse_mode="Markdown",
        )
        await message.answer(
            text=_("Вы подтверждаете отправку?"),
            reply_markup=await confirm_with_button_keyboard(),
        )
        await state.set_state("confirm_with_button_no_photo")
    except Exception as err:
        logger.error(err)
        await message.answer(
            text=_(
                "Произошла ошибка! Скорее всего, неправильно введена ссылка! "
                "Попробуйте еще раз."
            )
        )


@dp.callback_query_handler(state="confirm_with_button_no_photo")
async def confirm_with_button_no_photo(call: CallbackQuery, state: FSMContext) -> None:
    chats = await db_commands.select_all_users()
    count = 0

    async with state.proxy() as data:
        text = data["text"]
        button_name = data["button_name"]
        button_url = data["button_url"]

        markup = InlineKeyboardMarkup(row_width=1)
        btn = InlineKeyboardButton(text=button_name, url=button_url)
        markup.add(btn)
        await call.message.edit_text(text=_("Начинаю рассылку!"))
        for i in chats:
            try:
                await bot.send_message(
                    chat_id=i.get("telegram_id"),
                    reply_markup=markup,
                    text=text,
                    parse_mode="MarkdownV2",
                )
                count += 1
                await asyncio.sleep(1)
            except Exception as err:
                logger.error(
                    _("Сообщение не дошло в чат {chat} Причина: \n{err}").format(
                        err=err, chat=(i.get("telegram_id"))
                    )
                )

            await call.message.edit_text(
                text=_(
                    "Рассылка проведена успешно!" " Ее получили: {count} чатов!\n"
                ).format(count=count)
            )
        await state.reset_state(with_data=True)


@dp.message_handler(IsAdmin(), content_types=["photo"], state="broadcast_get_content")
async def get_photo_for_confirm(message: types.Message, state: FSMContext) -> None:
    text = message.md_text
    escape_md(text)
    quote_html(text)
    photo = message.photo[-1].file_id
    await message.answer_photo(
        caption=_(
            "Вот сообщение: \n\n{text}\n\n Вы подтверждаете отправку? "
            "Или хотите что-то добавить?"
        ).format(text=text),
        photo=photo,
        reply_markup=await add_buttons_keyboard(),
        parse_mode="Markdown",
    )
    await state.update_data(text=text)
    await state.update_data(photo=photo)
    await state.set_state("broadcast_confirming_photo")


@dp.callback_query_handler(state="broadcast_confirming_photo")
async def broadcast_confirming_photo(call: CallbackQuery, state: FSMContext) -> None:
    chats = await db_commands.select_all_users()
    count = 0
    async with state.proxy() as data:
        text = data["text"]
        photo = data["photo"]

        if call.data == "confirm_send":
            await call.message.answer(text="Начинаю рассылку!")
            for i in chats:
                try:
                    await bot.send_photo(
                        chat_id=i.get("telegram_id"),
                        caption=text,
                        photo=photo,
                        parse_mode="MarkdownV2",
                    )
                    count += 1
                    await asyncio.sleep(1)
                except Exception as err:
                    logger.error(
                        _("Сообщение не дошло в чат {chat} Причина: \n{err}").format(
                            err=err, chat=(i.get("telegram_id"))
                        )
                    )

                await call.message.edit_text(
                    text=_(
                        "Рассылка проведена успешно! Ее получили: {count} чатов!\n"
                    ).format(count=count)
                )
            await state.reset_state(with_data=True)
        elif call.data == "add_buttons":
            await call.message.answer(text="Пришлите мне название кнопки!")
            await state.set_state("get_button_name_photo")


@dp.message_handler(IsAdmin(), state="get_button_name_photo")
async def get_button_name_photo(message: types.Message, state: FSMContext) -> None:
    button_name = message.text
    await state.update_data(button_name=button_name)
    await message.reply(
        text="Название кнопки принято! Теперь отправьте мне ссылку для этой кнопки!"
    )
    await state.set_state("get_button_url_photo")


@dp.message_handler(IsAdmin(), state="get_button_url_photo")
async def get_button_url_photo(message: types.Message, state: FSMContext) -> None:
    button_url = message.text
    await state.update_data(button_url=button_url)
    async with state.proxy() as data:
        text = data["text"]
        button_name = data["button_name"]

    markup = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton(text=button_name, url=button_url)
    markup.add(btn)
    try:
        await message.answer(
            text=_("Вот так будет выглядеть сообщение: \n\n" "{text}\n\n").format(
                text=text
            ),
            reply_markup=markup,
            parse_mode="Markdown",
        )
        await message.answer(
            text=_("Вы подтверждаете отправку?"),
            reply_markup=await confirm_with_button_keyboard(),
        )
        await state.set_state("confirm_with_button_photo")
    except Exception as err:
        logger.error(err)
        await message.answer(
            text=_(
                "Произошла ошибка! Скорее всего, неправильно введена ссылка! "
                "Попробуйте еще раз."
            )
        )


@dp.callback_query_handler(state="confirm_with_button_photo")
async def confirm_with_button_photo(call: CallbackQuery, state: FSMContext) -> None:
    chats = await db_commands.select_all_users()
    count = 0

    async with state.proxy() as data:
        text = data["text"]
        photo = data["photo"]
        button_name = data["button_name"]
        button_url = data["button_url"]

        markup = InlineKeyboardMarkup(row_width=1)
        btn = InlineKeyboardButton(text=button_name, url=button_url)
        markup.add(btn)
        await call.message.edit_text(text=_("Начинаю рассылку!"))
        for i in chats:
            try:
                await bot.send_photo(
                    chat_id=i.get("telegram_id"),
                    photo=photo,
                    reply_markup=markup,
                    caption=text,
                    parse_mode="MarkDown",
                )
                count += 1
                await asyncio.sleep(1)
            except Exception as err:
                logger.error(
                    _("Сообщение не дошло в чат {chat} Причина: \n{err}").format(
                        err=err, chat=(i.get("telegram_id"))
                    )
                )

            await call.message.edit_text(
                text=_(
                    "Рассылка проведена успешно! Ее получили: {count} чатов!\n"
                ).format(count=count)
            )
        await state.reset_state(with_data=True)
