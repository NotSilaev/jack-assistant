import sys
sys.path.append("../../") # src/

from database.main import fetch


def getUser(user_id: int) -> dict:
    query = """
        SELECT id, access_level_id, car_service_id, created_at
        FROM users
        WHERE id = %s
    """
    params = (user_id, )

    response: list = fetch(query, params, fetch_type='one', as_dict=True)

    try:
        user: dict = response[0]
    except IndexError:
        user = None

    return user
