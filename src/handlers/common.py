import sys
sys.path.append("../") # src/

from access import access_checker
from exceptions import exceptions_catcher
from utils import respondEvent, makeGreetingMessage, getUserName

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(F.data == "start")
@router.message(F.text & (~F.text.startswith("/")))
@exceptions_catcher()
@access_checker()
async def start(event: Message | CallbackQuery) -> None:
    user: User = event.from_user
    user_name: str = getUserName(user=user)

    greeting: str = makeGreetingMessage(timezone_code='Europe/Volgograd')

    message_text = (
        f"*{greeting}*, {user_name}\n\n"
        + "🧑🏼‍🔧 Чем я могу Вам помочь?"
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Hello, World!", callback_data="#")

    await respondEvent(
        event,
        text=message_text, 
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup(),
    )
