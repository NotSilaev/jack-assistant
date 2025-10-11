from database.tables.invite_links import createInviteLink

import uuid


def generateInviteUserLink(access_level_id: int, car_service_id: int, phone: str) -> str:
    invite_link_id = str(uuid.uuid4())
    createInviteLink(invite_link_id, access_level_id, car_service_id, phone)
    invite_link = f"https://t.me/JackCarsBot?start={invite_link_id}"
    return invite_link
