import sys
sys.path.append("../") # src/

from handlers.forms.add_customer_form import start_add_customer_form

from exceptions import exceptions_catcher
from access import access_checker
from utils import respondEvent

from aiogram import Router, F
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext


router = Router(name=__name__)


@router.callback_query(F.data == "add_customer")
@exceptions_catcher()
@access_checker(required_permissions=['add_customer'])
async def add_customer(event: CallbackQuery, state: FSMContext) -> None:
    await start_add_customer_form(event, state)
