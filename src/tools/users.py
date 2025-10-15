from database.tables.invite_links import createInviteLink

import uuid


def generateInviteUserLink(access_level_id: int, car_service_id: int, phone: str, employee_user_id: int) -> str:
    invite_link_id = str(uuid.uuid4())
    createInviteLink(invite_link_id, access_level_id, car_service_id, phone, employee_user_id)
    invite_link = f"https://t.me/JackCarsBot?start={invite_link_id}"
    return invite_link
