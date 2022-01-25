from fastapi import APIRouter

router = APIRouter(tags=['Server Connection'])


@router.get(path='/ping', response_model=str)
def check_server_connection() -> str:
    """
    Returns a string to indicate the server is responding.

    Returns:
    - str: The string "pong".
    """

    return 'pong'
