import logging
import random
from getpass import getpass

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory='front-end'),
          name='front-end')

logger = logging.getLogger("uvicorn.error")

mongodb_uri = getpass(prompt='MongoDB URI: ')


class GameState(BaseModel):
    values: list[list[int]]


@app.get('/')
def home() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: front-end/index.html
    """

    return FileResponse('front-end/index.html')


@app.post('/hint')
def get_ai_hint(game_state: GameState) -> dict[str, str]:
    """
    Retrieves the next move by the AI model as a hint from a given board state.

    Args:
    - **game_state** (GameState): The board state. The values correspond to the
        base 2 logarithm of the text displayed on the tiles. Empty cells are
        given the value 0.

    Returns:
    - dict[str, str]: The returned hint.
    """

    game_state = game_state.dict()["values"]
    logger.info(f'{game_state = }')
    return {'hint': random.choice(['up', 'down', 'left', 'right']),
            'note': 'This feature is not yet implemented. The hint is random.'}
