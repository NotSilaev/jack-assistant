import sys
sys.path.append("../") # src/

from handlers.forms.add_feedback_request_form import start_add_feedback_request_form

from exceptions import exceptions_catcher
from access import access_checker
from utils import respondEvent, getUUIDStringFromCallData

from database.tables.feedback_requests import (
    getFeedbackRequest, 
    setFeedbackRequestEmployeeUserID, 
    setFeedbackRequestCompleted
)
from database.tables.users import getUser
from database.tables.contact_methods import getContactMethod

from aiogram import Router, F
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router(name=__name__)


@router.callback_query(F.data == "add_feedback_request")
@exceptions_catcher()
@access_checker(required_permissions=['add_feedback_request'])
async def add_feedback_request(event: CallbackQuery, state: FSMContext) -> None:
    await start_add_feedback_request_form(event, state)
    
    
@router.callback_query(F.data.startswith("take_feedback_request"))
@exceptions_catcher()
@access_checker(required_permissions=['take_feedback_request'])
async def take_feedback_request(event: CallbackQuery, state: FSMContext) -> None:
    feedback_request_id: str = getUUIDStringFromCallData(call_data=event.data)
    feedback_request: dict | None = getFeedbackRequest(feedback_request_id)

    if not feedback_request:
        return await respondEvent(event, text='*❌ Запрос на обратную связь не найден*', parse_mode="Markdown")

    if feedback_request['employee_user_id']:
        return await respondEvent(event, text='*❌ Запрос уже принят другим сотрудником*', parse_mode="Markdown")

    customer_user_id: int = feedback_request['customer_user_id']
    contact_method_id: int = feedback_request['contact_method_id']
    description: str = feedback_request['description']

    if not customer_user_id:
        return await respondEvent(event, text='*❌ Клиент оставивший запрос не найден*', parse_mode="Markdown")

    customer_phone: str = getUser(customer_user_id)['phone']

    employee_user_id: int = event.from_user.id
    setFeedbackRequestEmployeeUserID(
        feedback_request_id, 
        employee_user_id
    )

    contact_method_title: str = getContactMethod(contact_method_id)['title'].title()

    message_text = (
        "*📥 Запрос на обратную связь принят*\n\n"
        + f"📲 Телефон клиента: `{customer_phone}`\n"
        + f"💭 Выбранный способ связи: *{contact_method_title}*\n"
        + (f"📝 Описание вопроса: *{description}*" if description else "")
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Отметить выполненным", 
        callback_data=f"complete_feedback_request-{feedback_request_id}"
    )

    await respondEvent(
        event,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data.startswith("complete_feedback_request"))
@exceptions_catcher()
@access_checker(required_permissions=['take_feedback_request'])
async def complete_feedback_request(event: CallbackQuery, state: FSMContext) -> None:
    feedback_request_id: str = getUUIDStringFromCallData(call_data=event.data)
    feedback_request: dict | None = getFeedbackRequest(feedback_request_id)

    if not feedback_request:
        return await respondEvent(event, text='*❌ Запрос на обратную связь не найден*', parse_mode="Markdown")

    employee_user_id: int = event.from_user.id
    if feedback_request['employee_user_id'] != employee_user_id:
        return await respondEvent(event, text='*❌ Запрос обрабатывается другим сотрудником*', parse_mode="Markdown")

    setFeedbackRequestCompleted(feedback_request_id)

    await respondEvent(
        event,
        text="*✅ Запрос на обратную связь отмечен как выполненный*",
        parse_mode="Markdown"
    )
