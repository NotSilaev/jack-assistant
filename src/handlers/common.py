import sys
sys.path.append("../") # src/

from exceptions import exceptions_catcher
from access import access_checker, hasUserAccess
from utils import respondEvent, makeGreetingMessage, getUserName

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


router = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(F.data == "start")
@router.message(F.text & (~F.text.startswith("/")), StateFilter(None))
@exceptions_catcher()
@access_checker()
async def start(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    user: User = event.from_user
    user_id: int = user.id
    user_name: str = getUserName(user=user)

    greeting: str = makeGreetingMessage(timezone_code="Europe/Volgograd")

    message_text = (
        f"*{greeting}*, {user_name}\n\n"
        + "🧑🏼‍🔧 Чем я могу Вам помочь?"
    )

    keyboard = InlineKeyboardBuilder()
    if hasUserAccess(user_id, required_permissions=["add_customer"]):
        keyboard.button(text="➕ Добавить клиента", callback_data="add_customer")
    if hasUserAccess(user_id, required_permissions=["add_feedback_request"]):
        keyboard.button(text="📲 Запросить обратную связь", callback_data="add_feedback_request")    
    keyboard.adjust(1)

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )
