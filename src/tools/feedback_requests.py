from database.tables.feedback_requests import getFeedbackRequest, getUnprocessedFeedbackRequests
from database.tables.contact_methods import getContactMethod
from database.tables.users import getUsersByAccessLevelAndCarService
from database.tables.car_services import getCarServices

from config import settings
from api.telegram import TelegramAPI
from utils import getCurrentDateTime

import json
from datetime import datetime


def sendFeedbackRequestToEmployees(feedback_request_id: int) -> None:
    feedback_request: dict | None = getFeedbackRequest(feedback_request_id)
    if not feedback_request:
        return

    car_service_id: int = feedback_request["car_service_id"]
    contact_method_id: int = feedback_request["car_service_id"]
    contact_method_title: str = getContactMethod(contact_method_id)["title"].title()
    description: str = feedback_request["description"]

    message_text = (
        "*🔔 Получен запрос на обратную связь*\n\n"
        + f"💭 Способ связи: {contact_method_title}\n"
        + (f"📝 Описание вопроса: *{description}*" if description else "")
    )

    keyboard = json.dumps({
        "inline_keyboard": [[{
            "text": "📥 Принять запрос",
            "callback_data": f"take_feedback_request-{feedback_request_id}"
        }]]
    })

    telegram_api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)

    employee_access_level = 2
    car_service_employees: list = getUsersByAccessLevelAndCarService(employee_access_level, car_service_id)
    for employee in car_service_employees:
        employee_user_id: int = employee["id"]
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


def checkUnprocessedFeedbackRequests() -> None:
    current_datetime: datetime = getCurrentDateTime(timezone_code="Europe/Volgograd")
    current_hour = current_datetime.hour
    if current_hour not in range(8, 21):
        return

    car_services: list = getCarServices()
    for car_service in car_services:
        car_service_id = car_service["id"]

        unprocessed_feedback_requests: list = getUnprocessedFeedbackRequests(car_service_id)
        if not unprocessed_feedback_requests:
            return

        message_text = (
            f"‼️ На данный момент имеется *{len(unprocessed_feedback_requests)}* необработанных заявок на обратную связь"
        )

        keyboard = json.dumps({
            "inline_keyboard": [[{
                "text": "🔔 Оповестить сотрудников",
                "callback_data": f"send_unprocessed_feedback_requests_notification-{car_service_id}"
            }]]
        })

        telegram_api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)

        director_access_level = 3
        car_service_directors: list = getUsersByAccessLevelAndCarService(director_access_level, car_service_id)
        for employee in car_service_directors:
            employee_user_id: int = employee["id"]
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

