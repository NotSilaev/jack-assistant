from config import settings

from database.tables.users import getUser
from database.tables.permissions import getAccessLevelPermissions

from api.telegram import TelegramAPI

from aiogram.types import Message, CallbackQuery

import functools


def sendTelegramMessage(chat_id: int, message_text: str) -> None:
    telegram_api = TelegramAPI(settings.TELEGRAM_BOT_TOKEN)
    telegram_api.sendRequest(
        request_method="POST",
        api_method="sendMessage",
        parameters={
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "Markdown",
        },
    )


def access_checker(required_permissions: tuple[str] = None): 
    "Checks the user's access permissions to the function."

    def container(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            event: Message | CallbackQuery = args[0]
            user_id = event.from_user.id
            
            user: dict | None = getUser(user_id)

            # Check user existance
            if not user:
                message_text = (
                    "*🧑🏼‍🔧 Бот предназначен для клиентов автосервиса «JackCars»*\n\n"
                    + "Вы можете обратиться к свободному сервисному консультанту \
                       в любом из наших сервисов для подключения к системе."
                )
                return sendTelegramMessage(user_id, message_text)

            # Check user permissions
            if required_permissions:
                if not hasUserAccess(user_id, required_permissions):
                    message_text = "*🚫 У Вас недостаточно прав для доступа к данному разделу*"
                    return sendTelegramMessage(user_id, message_text)

            await func(*args, **kwargs)

        return wrapper
    return container


def hasUserAccess(user_id: int, required_permissions: tuple) -> bool:
    user: dict | None = getUser(user_id)

    if not user:
        return False

    user_access_level_id: int = user['access_level_id']
    user_permissions = [
        permission['name'] for permission in getAccessLevelPermissions(user_access_level_id)
    ]
    for permission in required_permissions:
        if permission not in user_permissions:
            return False
    
    return True
