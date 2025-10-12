import sys
sys.path.append("../../") # src/

from config import settings
from exceptions import exceptions_catcher
from access import access_checker
from utils import respondEvent
from tools.users import sendFeedbackRequestToEmployees

from database.tables.car_services import getCarServices, getCarService
from database.tables.contact_methods import getContactMethods, getContactMethod
from database.tables.feedback_requests import createFeedbackRequest

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import re


router = Router(name=__name__)


class FeedbackRequest(StatesGroup):
    car_service_id = State()
    contact_method_id = State()
    description = State()


async def start_add_feedback_request_form(event: CallbackQuery, state: FSMContext) -> None:
    await feedback_request_car_service_id_state(event, state)


@router.callback_query(F.data == "feedback_request_car_service_id_state")
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_car_service_id_state(event: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FeedbackRequest.car_service_id)

    message_text = (
        "*📲 Запрос обратной связи*\n\n"
        + "🚗 Выберите автосервис в который хотите обратиться"
    )

    car_services: list = getCarServices()

    keyboard = InlineKeyboardBuilder()
    for car_service in car_services:
        keyboard.button(text=car_service['title'].title(), callback_data=str(car_service['id']))
    keyboard.button(text="❌ Отмена", callback_data="start")
    keyboard.adjust(len(car_services), 1)

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(FeedbackRequest.car_service_id)
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_car_service_id_process(event: CallbackQuery, state: FSMContext) -> None:
    car_service_id: int = event.data
    await state.update_data(car_service_id=car_service_id)
    await feedback_request_contact_method_id_state(event, state)


@router.callback_query(F.data == "feedback_request_contact_method_id_state")
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_contact_method_id_state(event: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FeedbackRequest.contact_method_id)

    feedback_request_data: dict = await state.get_data()
    car_service_id: int = feedback_request_data['car_service_id']
    car_service_title: str = getCarService(car_service_id)['title'].title()

    message_text = (
        "*📲 Запрос обратной связи*\n\n"
        + f"🚗 Автосервис «JackCars»: *{car_service_title}*\n\n"
        + "💭 Выберите предпочтительный способ связи"
    )

    contact_methods: list = getContactMethods()

    keyboard = InlineKeyboardBuilder()
    for contact_method in contact_methods:
        keyboard.button(text=contact_method['title'].title(), callback_data=str(contact_method['id']))
    keyboard.button(text="⬅️ Назад", callback_data="feedback_request_car_service_id_state")
    keyboard.button(text="❌ Отмена", callback_data="start")
    keyboard.adjust(len(contact_methods), 2)

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(FeedbackRequest.contact_method_id)
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_contact_method_id_process(event: CallbackQuery, state: FSMContext) -> None:
    contact_method_id: int = event.data
    await state.update_data(contact_method_id=contact_method_id)
    await feedback_request_description_state(event, state)
    
    
@router.callback_query(F.data == "feedback_request_description_state")
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_description_state(event: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FeedbackRequest.description)

    feedback_request_data: dict = await state.get_data()
    car_service_id: int = feedback_request_data['car_service_id']
    contact_method_id: int = feedback_request_data['contact_method_id']

    car_service_title: str = getCarService(car_service_id)['title'].title()
    contact_method_title: str = getContactMethod(contact_method_id)['title'].title()

    message_text = (
        "*📲 Запрос обратной связи*\n\n"
        + f"🚗 Автосервис «JackCars»: *{car_service_title}*\n"
        + f"💭 Способ связи: *{contact_method_title}\n\n*"
        + "📝 Кратко опишите свой вопрос или пропустите данный шаг."
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="↪️ Пропустить", callback_data="feedback_request_form_commit")
    keyboard.button(text="⬅️ Назад", callback_data="feedback_request_contact_method_id_state")
    keyboard.button(text="❌ Отмена", callback_data="start")
    keyboard.adjust(1, 2)

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )


@router.message(FeedbackRequest.description)
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_description_process(event: Message, state: FSMContext) -> None:
    description: str = event.text
    await state.update_data(description=description)
    await feedback_request_form_commit(event, state)


@router.callback_query(F.data.startswith('feedback_request_form_commit'))
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def feedback_request_form_commit(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)

    feedback_request_data: dict = await state.get_data()
    car_service_id: int = feedback_request_data['car_service_id']
    contact_method_id: int = feedback_request_data['contact_method_id']
    customer_user_id: int = event.from_user.id

    try:
        description: str = feedback_request_data['description']
        description_text = description
    except KeyError:
        description = None
        description_text = '✖️'

    car_service_title: str = getCarService(car_service_id)['title'].title()
    contact_method_title: str = getContactMethod(contact_method_id)['title'].title()

    is_form_committed = False
    if isinstance(event, CallbackQuery):
        try:
            if event.data.split('-')[1] == 'committed':
                is_form_committed = True
        except IndexError:
            pass

    keyboard = InlineKeyboardBuilder()

    if not is_form_committed:
        message_text = (
            "*📲 Запрос обратной связи*\n\n"
            + f"🚗 Автосервис «JackCars»: *{car_service_title}*\n"
            + f"💭 Способ связи: *{contact_method_title}\n*"
            + f"📝 Описание вопроса: *{description_text}*"
        )

        keyboard.button(text="✉️ Отправить запрос", callback_data="feedback_request_form_commit-committed")
        keyboard.button(text="⬅️ Назад", callback_data="feedback_request_description_state")
        keyboard.button(text="❌ Отмена", callback_data="start")
        keyboard.adjust(1, 2)        
        
    else:
        feedback_request_id: str = createFeedbackRequest(
            car_service_id, 
            contact_method_id, 
            customer_user_id, 
            description
        )
        sendFeedbackRequestToEmployees(feedback_request_id)

        message_text = (
            "*✅ Запрос обратной связи отправлен*\n\n"
            + f"🚗 Автосервис «JackCars»: *{car_service_title}*\n"
            + f"💭 Способ связи: *{contact_method_title}\n*"
            + f"📝 Описание вопроса: *{description_text}*\n\n"
            + f"👨🏼‍💻 Скоро с Вами свяжется наш менеджер."
        )
        keyboard.button(text="🏠 В меню", callback_data="start")

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )
