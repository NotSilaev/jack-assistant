from config import settings

from database.tables.users import createUser, getUser
from database.tables.permissions import getAccessLevelPermissions
from database.tables.invite_links import getInviteLink, increaseInviteLinkActivations

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


def checkUserInvitationLink(user_id: int, start_text: str) -> bool:
    """
    Checks the user's invitation link and creates it if it is valid.

    Returns `True` if the user was created, `False` if not.
    """

    try:
        invite_link_id: str = start_text.split()[1]
    except IndexError:
        return

    invite_link: dict = getInviteLink(invite_link_id)
    if not invite_link:
        return False
    
    activations: int = invite_link['activations']
    max_activations: int = invite_link['max_activations']

    if activations >= max_activations:
        return False

    createUser(
        user_id=user_id,
        access_level_id=invite_link['access_level_id'],
        car_service_id=invite_link['car_service_id'],
        phone=invite_link['phone'] if invite_link['phone'] else None
    )
    increaseInviteLinkActivations(invite_link_id)

    return True


def access_checker(required_permissions: tuple[str] = None): 
    "Checks the user's access permissions to the function."

    def container(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            event: Message | CallbackQuery = args[0]
            user_id = event.from_user.id
            
            user: dict | None = getUser(user_id)

            if 'state' in kwargs.keys():
                state = kwargs['state']
            else:
                state = None

            # Check user existance
            if not user:
                if state: await state.clear()
                is_user_created = False

                if isinstance(event, Message) and event.text.startswith('/start'):
                    is_user_created = checkUserInvitationLink(user_id=user_id, start_text=event.text)

                if is_user_created:
                    message_text = (
                        "*👋 Рад Вас видеть!*\n\n"
                        + "🚀 Ассистент активирован."
                    )
                else:
                    message_text = (
                        "*🧑🏼‍🔧 Бот предназначен для клиентов автосервиса «JackCars»*\n\n"
                        + "Вы можете обратиться к свободному сервисному консультанту \
                        в любом из наших сервисов для подключения к системе."
                    )
                return sendTelegramMessage(user_id, message_text)

            # Check user permissions
            if required_permissions:
                if not hasUserAccess(user_id, required_permissions):
                    if state: await state.clear()
                    message_text = "*🚫 У Вас недостаточно прав для доступа к данному разделу*"
                    return sendTelegramMessage(user_id, message_text)

            await func(*args, **kwargs)

        return wrapper
    return container
