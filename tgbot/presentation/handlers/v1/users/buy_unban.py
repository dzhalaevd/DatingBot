import uuid

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from data.config import (
    load_config,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.payments_inline import (
    payment_menu_keyboard,
    yoomoney_keyboard,
)
from loader import (
    _,
    dp,
    wallet,
)
from utils.db_api import (
    db_commands,
)
from utils.yoomoney.types import (
    PaymentSource,
)


@dp.callback_query_handler(text="unban")
async def get_payment_menu(call: CallbackQuery) -> None:
    await call.message.edit_text(
        text=_(
            "<b>💳 Сейчас вам нужно выбрать способ оплаты</b>\n\n"
            "├Стоимость разблокировки - <b>99₽</b>\n"
            "├Оплата обычно приходить в течение 1-3 минут\n"
            "├Если у вас нет Yoomoney или нет возможности\n"
            "├оплатить, напишите агенту поддержки"
        ),
        reply_markup=await payment_menu_keyboard(),
    )


@dp.callback_query_handler(text="yoomoney")
async def get_payment(call: CallbackQuery, state: FSMContext) -> None:
    payment_form = await wallet.create_payment_form(
        amount_rub=2,
        unique_label=uuid.uuid4().hex,
        payment_source=PaymentSource.YOOMONEY_WALLET,
        success_redirect_url=load_config().misc.redirect_url,
    )

    await call.message.edit_text(
        text=_("После оплаты нажмите <b>🔄 Проверить оплату</b>"),
        reply_markup=await yoomoney_keyboard(url=payment_form.link_for_customer),
    )

    await state.set_state("payment")
    await state.update_data(
        {"label": payment_form.payment_label, "form": payment_form.link_for_customer}
    )


@dp.callback_query_handler(text="yoomoney:check_payment", state="payment")
async def check_payment(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    payment_is_completed: bool = await wallet.check_payment_on_successful(
        label=data.get("label")
    )
    markup = await start_keyboard(obj=call)
    if payment_is_completed:
        await call.message.edit_text(
            text=_("Поздравляем! Вы были разрабанены"), reply_markup=markup
        )
        await db_commands.update_user_data(
            telegram_id=call.from_user.id, is_banned=False
        )
        await state.reset_state()
    else:
        await call.message.edit_text(
            text=_(
                "Оплата не прошла! Подождите минут 10,"
                " а затем еще раз попробуйте нажать кнопку ниже"
            ),
            reply_markup=await yoomoney_keyboard(url=data.get("form")),
        )
