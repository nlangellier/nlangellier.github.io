import random
from typing import Union

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory='front-end'),
          name='front-end')


@app.get('/')
def home() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: front-end/index.html
    """

    return FileResponse('front-end/index.html')


@app.get('/hint')
def get_ai_hint(rows: int, columns: int) -> dict[str, Union[str, int]]:
    """
    Retrieves the next move by the AI model as a hint from a given board state.

    Args:
    - **rows** (int): each item must have a name
    - **columns** (int): a long description

    Returns:
    - dict[str, Union[str, int]]: the hint and the rows and columns
    """

    return {'rows': rows,
            'columns': columns,
            'hint': random.choice(['up', 'down', 'left', 'right']),
            'note': 'This feature is not fully implemented. Hint is random'}
