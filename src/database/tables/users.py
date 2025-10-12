import sys
sys.path.append("../../") # src/

from database.main import execute, fetch
from utils import getCurrentDateTime

from datetime import datetime


def createUser(user_id: int, access_level_id: int, car_service_id: int, phone: str) -> int:
    created_at: datetime = getCurrentDateTime()

    stmt = """
        INSERT INTO users
        (id, access_level_id, car_service_id, phone, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (user_id, access_level_id, car_service_id, phone, created_at)

    execute(stmt, params)

    return user_id


def getUser(user_id: int) -> dict | None:
    query = """
        SELECT id, access_level_id, car_service_id, phone, created_at
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


def getEmployeesByCarService(car_service_id: int) -> list:
    employee_access_level_id = 2

    query = """
        SELECT id, access_level_id, car_service_id, created_at
        FROM users
        WHERE access_level_id = %s AND car_service_id = %s
    """
    params = (employee_access_level_id, car_service_id)

    car_service_employees: list = fetch(query, params, fetch_type='all', as_dict=True)

    return car_service_employees
