import sys
sys.path.append("../") # src/

from utils import respondEvent

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart


router = Router(name=__name__)


@router.message(CommandStart())
@router.callback_query(F.data == "start")
@router.message(F.text & (~F.text.startswith("/")))
async def start(event: Message | CallbackQuery) -> None:
    await respondEvent(event, text="Hello, World!")
