from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)
from django.db import (
    IntegrityError,
)

from data.config import (
    load_config,
)
from functions.dating import (
    ChooseReportReason,
    DislikeAction,
    DislikeReciprocity,
    GoBackToViewing,
    LikeAction,
    LikeReciprocity,
    SendReport,
    StartFindingFailure,
    StartFindingReachLimit,
    StartFindingSuccess,
    StoppedAction,
)
from functions.dating.get_next_user_func import (
    get_next_user,
)
from functions.main_app.auxiliary_tools import (
    delete_message,
)
from keyboards.inline.questionnaires_inline import (
    action_keyboard,
    action_reciprocity_keyboard,
    action_report_keyboard,
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


@dp.callback_query_handler(text="find_ques")
async def handle_start_finding(call: CallbackQuery, state: FSMContext) -> None:
    telegram_id = call.from_user.id
    user_list = await get_next_user(telegram_id=telegram_id)
    user = await db_commands.select_user(telegram_id=telegram_id)
    limit = user.limit_of_views
    strategy_mapping = {
        "success": StartFindingSuccess(),
        "failure": StartFindingFailure(),
        "reached_limit": StartFindingReachLimit(),
    }
    status_mapping = {
        (True, True): "success",
        (True, False): "reached_limit",
        (False, _): "failure",
    }
    status = status_mapping.get((bool(user_list), limit != 0), "failure")
    strategy = strategy_mapping.get(status)
    await strategy.execute(call=call, state=state)


@dp.callback_query_handler(
    action_report_keyboard.filter(
        action=["adults_only", "drugs", "scam", "another", "cancel_report"],
    ),
)
async def handle_report(
        call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
):
    action = callback_data["action"]
    strategy_mapping = {
        "adults_only": SendReport(),
        "drugs": SendReport(),
        "scam": SendReport(),
        "another": SendReport(),
        "cancel_report": GoBackToViewing(),
    }
    strategy = strategy_mapping.get(action)

    await strategy.execute(call, state, callback_data)

    if action != "cancel_report":
        await call.message.answer(text=_("Жалоба успешно отправлена"))
        strategy = GoBackToViewing()
        await strategy.execute(call, state, callback_data)


@dp.callback_query_handler(
    action_keyboard.filter(action=["like", "dislike", "stopped", "report"]),
    state="*",
)
async def handle_action(
        call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
) -> None:
    action = callback_data["action"]
    profile_id = callback_data["target_id"]
    user = await db_commands.select_user_object(telegram_id=call.from_user.id)
    viewed_profile = await db_commands.select_user_object(telegram_id=profile_id)
    if load_config().misc.production:
        try:
            await db_commands.add_profile_to_viewed(
                user=user, viewed_profile=viewed_profile
            )
        except IntegrityError:
            logger.error("Дубликаты профилей")
    else:
        pass
    strategy_mapping = {
        "like": LikeAction(),
        "dislike": DislikeAction(),
        "stopped": StoppedAction(),
        "report": ChooseReportReason(),
    }
    strategy = strategy_mapping.get(action)
    info = await bot.get_me()

    if strategy and user.limit_of_views != 0:
        await strategy.execute(call, state, callback_data)
    elif user.limit_of_views == 0:
        await delete_message(message=call.message)
        await call.message.answer(
            text=_(
                "Слишком много ❤️ за сегодня.\n\n"
                "Пригласи друзей и получи больше ❤️\n\n"
                "https://t.me/{}?start={}"
            ).format(info.username, call.from_user.id)
        )
        await state.reset_state()


@dp.callback_query_handler(
    action_reciprocity_keyboard.filter(
        action=["like_reciprocity", "dislike_reciprocity"]
    )
)
async def handle_reciprocity_action(
        call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
) -> None:
    action = callback_data["action"]
    strategy_mapping = {
        "like_reciprocity": LikeReciprocity(),
        "dislike_reciprocity": DislikeReciprocity(),
    }
    strategy = strategy_mapping.get(action)
    if strategy:
        await strategy.execute(call, state, callback_data)


@dp.callback_query_handler(state="*", text="go_back_to_viewing_ques")
async def handle_go_back_to_viewing(call: CallbackQuery, state: FSMContext) -> None:
    strategy = GoBackToViewing()
    # noinspection PyTypeChecker
    await strategy.execute(call, state, None)
