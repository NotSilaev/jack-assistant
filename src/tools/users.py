from database.tables.invite_links import createInviteLink
from database.tables.feedback_requests import getFeedbackRequest
from database.tables.contact_methods import getContactMethod
from database.tables.users import getEmployeesByCarService

from config import settings
from api.telegram import TelegramAPI

import uuid
import json


def generateInviteUserLink(access_level_id: int, car_service_id: int, phone: str, employee_user_id: int) -> str:
    invite_link_id = str(uuid.uuid4())
    createInviteLink(invite_link_id, access_level_id, car_service_id, phone, employee_user_id)
    invite_link = f"https://t.me/JackCarsBot?start={invite_link_id}"
    return invite_link


def sendFeedbackRequestToEmployees(feedback_request_id: int) -> None:
    feedback_request: dict | None = getFeedbackRequest(feedback_request_id)
    if not feedback_request:
        return

    car_service_id: int = feedback_request['car_service_id']
    contact_method_id: int = feedback_request['car_service_id']
    contact_method_title: str = getContactMethod(contact_method_id)['title'].title()
    description: str = feedback_request['description']

    message_text = (
        "*🔔 Получен запрос на обратную связь*\n\n"
        + f"💭 Способ связи: {contact_method_title}"
        + (description if description else "")
    )

    keyboard = json.dumps({
        "inline_keyboard": [[{
            "text": "📥 Принять запрос",
            "callback_data": f"take_feedback_request-{feedback_request_id}"
        }]]
    })

    telegram_api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)

    car_service_employees: list = getEmployeesByCarService(car_service_id)
    for employee in car_service_employees:
        employee_user_id: int = employee['id']
        telegram_api.sendRequest(
            request_method="POST",
            api_method="sendMessage",
            parameters={
                "chat_id": employee_user_id,
                "text": message_text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard,
            },
        )
