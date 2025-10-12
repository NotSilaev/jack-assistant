import sys
sys.path.append("../../") # src/

from database.main import execute, fetch
from utils import getCurrentDateTime

from datetime import datetime
import uuid


def createFeedbackRequest(
    car_service_id: int,
    contact_method_id: int,
    customer_user_id: int,
    description: str,
) -> str:
    feedback_request_id = str(uuid.uuid4())
    created_at: datetime = getCurrentDateTime()

    stmt = """
        INSERT INTO feedback_requests
        (id, car_service_id, contact_method_id, customer_user_id, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (feedback_request_id, car_service_id, contact_method_id, customer_user_id, description, created_at)

    execute(stmt, params)

    return feedback_request_id


def getFeedbackRequest(feedback_request_id: int) -> dict | None:
    query = """
        SELECT 
            id, 
            car_service_id, 
            contact_method_id, 
            customer_user_id, 
            employee_user_id,
            description, 
            is_completed, 
            created_at
        FROM feedback_requests
        WHERE id = %s
    """
    params = (feedback_request_id, )

    response: list = fetch(query, params, fetch_type='one', as_dict=True)

    try:
        feedback_request: dict = response[0]
    except IndexError:
        feedback_request = None

    return feedback_request


def setFeedbackRequestEmployeeUserID(feedback_request_id: int, employee_user_id: int) -> None:
    stmt = '''
        UPDATE feedback_requests
        SET employee_user_id = %s
        WHERE id = %s
    '''
    params = (employee_user_id, feedback_request_id)
    execute(stmt, params)


def setFeedbackRequestCompleted(feedback_request_id: int) -> None:
    stmt = '''
        UPDATE feedback_requests
        SET is_completed = TRUE
        WHERE id = %s
    '''
    params = (feedback_request_id, )
    execute(stmt, params)
