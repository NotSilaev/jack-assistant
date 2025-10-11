import sys
sys.path.append("../../") # src/

from database.main import fetch


def getAccessLevelPermissions(access_level_id: int) -> list:
    query = """
        SELECT p.id, p.name
        FROM access_levels_permissions alp
        JOIN permissions p
            ON alp.permission_id = p.id
        WHERE alp.access_level_id = %s
    """
    params = (access_level_id, )

    permissions: list = fetch(query, params, fetch_type='all', as_dict=True)

    return permissions
