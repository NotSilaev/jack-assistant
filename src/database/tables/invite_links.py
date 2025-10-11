import sys
sys.path.append("../../") # src/

from database.main import execute, fetch
from utils import getCurrentDateTime

from datetime import datetime


def createInviteLink(invite_link_id: str, access_level_id: int, car_service_id: int, phone: str) -> str:
    created_at: datetime = getCurrentDateTime()

    stmt = """
        INSERT INTO invite_links
        (id, access_level_id, car_service_id, phone, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (invite_link_id, access_level_id, car_service_id, phone, created_at)

    execute(stmt, params)

    return invite_link_id


def getInviteLink(invite_link_id: int) -> dict | None:
    query = """
        SELECT id, access_level_id, car_service_id, phone, created_at
        FROM invite_links
        WHERE id = %s
    """
    params = (invite_link_id, )

    response: list = fetch(query, params, fetch_type='one', as_dict=True)

    try:
        invite_link: dict = response[0]
    except IndexError:
        invite_link = None

    return invite_link
