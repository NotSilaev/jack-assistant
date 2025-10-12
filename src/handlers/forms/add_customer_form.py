import sys
sys.path.append("../../") # src/

from config import settings
from exceptions import exceptions_catcher
from access import access_checker
from utils import respondEvent, generateQRCode
from database.tables.users import getUser
from tools.users import generateInviteUserLink

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import re


router = Router(name=__name__)


class Customer(StatesGroup):
    phone = State()


async def start_add_customer_form(event: CallbackQuery, state: FSMContext) -> None:
    await customer_phone_state(event, state)


@router.callback_query(F.data == "customer_phone_state")
@exceptions_catcher()
@access_checker(required_permissions=['add_customer'])
async def customer_phone_state(event: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Customer.phone)

    message_text = (
        "*➕ Добавление клиента*\n\n"
        + "📲 Укажите номер телефона клиента"
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отмена", callback_data="start")

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )


@router.message(Customer.phone)
@exceptions_catcher()
@access_checker(required_permissions=['add_customer'])
async def task_title_process(event: Message, state: FSMContext) -> None:
    phone_pattern = r"^(\+?\d{1,4}[\s\-]?)?(\(?\d{1,4}\)?[\s\-]?)?[\d\s\-]{5,15}$"
    phone: str = event.text

    if not re.match(phone_pattern, phone):
        await respondEvent(
            event,
            text="*❗ Номер телефона указан некорректно, повторите попытку*",
            parse_mode="Markdown",
        )
        return await customer_phone_state(event, state)

    await state.update_data(phone=phone)
    await add_customer_form_commit(event, state)


@exceptions_catcher()
@access_checker(required_permissions=['add_customer'])
async def add_customer_form_commit(event: CallbackQuery, state: FSMContext) -> None:
    user_id: int = event.from_user.id
    user: dict = getUser(user_id)

    customer_data = await state.get_data()
    access_level_id = 1
    car_service_id = user['car_service_id']
    phone: str = customer_data["phone"]

    invite_customer_link: str = generateInviteUserLink(access_level_id, car_service_id, phone, user_id)

    qr_img_path = generateQRCode(invite_customer_link)
    message_text = (
        "*✅ Пригласительный QR-код создан*\n\n"
        + f"📲 Номер телефона: `{phone}`\n\n"
        + "🤳🏼 Предоставьте QR клиенту, он действителен в течение 1-го часа."
    )

    photo = FSInputFile(qr_img_path)
    await event.answer_photo(
        photo=photo, 
        caption=message_text, 
        parse_mode="Markdown"
    )
    await state.clear()
