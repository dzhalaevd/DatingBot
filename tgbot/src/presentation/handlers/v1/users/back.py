from abc import (
    ABC,
    abstractmethod,
)

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from functions.main_app.auxiliary_tools import (
    delete_message,
    display_profile,
    information_menu,
    registration_menu,
)
from handlers.users.event import (
    view_meetings_handler,
    view_own_event,
)
from keyboards.inline.admin_inline import (
    unban_user_keyboard,
)
from keyboards.inline.filters_inline import (
    filters_keyboard,
)
from keyboards.inline.menu_profile_inline import (
    get_profile_keyboard,
)
from loader import (
    _,
    dp,
)
from utils.db_api import (
    db_commands,
)


class Command(ABC):
    @abstractmethod
    async def execute(self, call: CallbackQuery, state: FSMContext) -> None:
        pass


class OpenMenuCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        await registration_menu(obj=call)


class BackToProfileMenuCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        telegram_id = call.from_user.id
        await delete_message(call.message)
        user_db = await db_commands.select_user(telegram_id=telegram_id)
        markup = await get_profile_keyboard(verification=user_db.verification)
        await display_profile(call, markup)


class UnbanMenuCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        await call.message.edit_text(
            _("Вы забанены!"), reply_markup=await unban_user_keyboard()
        )


class BackToFiltersMenuCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        await call.message.edit_text(
            text=_("Вы вернулись в меню фильтров"),
            reply_markup=await filters_keyboard(),
        )


class BackToGuideMenuCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        await information_menu(call)


class BackToEventProfileCommand(Command):
    async def execute(self, call: CallbackQuery, **kwargs) -> None:
        await view_own_event(call)


class EventProfileBackCommand(Command):
    async def execute(self, call: CallbackQuery, state: FSMContext) -> None:
        await state.finish()
        await delete_message(call.message)
        await view_meetings_handler(call)


menu_commands = {
    "back_with_delete": OpenMenuCommand(),
    "back_to_reg_menu": OpenMenuCommand(),
    "back_to_profile_menu": BackToProfileMenuCommand(),
    "unban_menu": UnbanMenuCommand(),
    "back_to_filter_menu": BackToFiltersMenuCommand(),
    "back_to_info_menu": BackToGuideMenuCommand(),
    "go_out": EventProfileBackCommand(),
    "event_menu": EventProfileBackCommand(),
    "back_to_event_profile": BackToEventProfileCommand(),
    "registration:stopped": OpenMenuCommand(),
}


@dp.callback_query_handler(lambda call: call.data in menu_commands.keys(), state="*")
async def handle_menu_action(call: CallbackQuery, state: FSMContext) -> None:
    menu_action = call.data
    command = menu_commands[menu_action]
    await state.reset_state()
    try:
        await command.execute(
            call,
        )
    except TypeError:
        await command.execute(call, state)
