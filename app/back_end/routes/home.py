from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from ..constants import DIRPATH_FRONT_END

router = APIRouter()


@router.get(path='/', response_class=HTMLResponse)
def home_page() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: The static webpage at /front-end/index.html
    """

    return FileResponse(DIRPATH_FRONT_END / 'index.html')
