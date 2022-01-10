import logging
import random
from getpass import getpass

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory='front-end'),
          name='front-end')

logger = logging.getLogger(name='uvicorn.error')

username = input('MongoDB username: ')
password = getpass(prompt='MongoDB password: ')
mongo_client = MongoClient(host='localhost',
                           port=27017,
                           username=username,
                           password=password,
                           authSource='admin',
                           authMechanism='SCRAM-SHA-256')
db = mongo_client['2048Infinite']


class GameState(BaseModel):
    values: list[list[int]]


class GameOverInfo(BaseModel):
    name: str = 'Anonymous'
    score: int
    rows: int
    columns: int


@app.get(path='/')
def home() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: front-end/index.html
    """

    return FileResponse('front-end/index.html')


@app.post(path='/hint')
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

    game_state = game_state.dict()['values']
    logger.info(f'{game_state = }')
    return {'hint': random.choice(['up', 'down', 'left', 'right']),
            'note': 'This feature is not yet implemented. The hint is random.'}


@app.post(path='/add-score')
def add_score_to_db(game_over_info: GameOverInfo) -> None:
    """
    Updates the MongoDB database with the information provided.

    Args:
    - **game_over_info** (GameOverInfo): Class with name (str), score (int),
        rows (rows), and columns (int) attributes.
    """

    result = db.leaderBoard.insert_one(game_over_info.dict())
    logger.info(result.inserted_id)
