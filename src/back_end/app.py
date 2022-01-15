import logging
import random
from getpass import getpass

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

from .constants import (DIRPATH_FRONT_END, DIRPATH_IMAGES, MAX_ROWS_COLUMNS,
                        MIN_ROWS_COLUMNS, Direction)
from .game_manager import GameManager
from .schemas import GameOverInfo, GameState, MoveResponse, NewGameResponse

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory=DIRPATH_FRONT_END),
          name='front-end')
app.mount(path='/images',
          app=StaticFiles(directory=DIRPATH_IMAGES),
          name='images')

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

active_games: dict[int, GameManager] = {}


@app.get(path='/')
def home() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: front-end/index.html
    """

    return FileResponse(DIRPATH_FRONT_END / 'index.html')


@app.get(path='/new-game', response_model=NewGameResponse)
def new_game(
        rows: int = Query(default=...,
                          description='Number of rows of the game board',
                          ge=MIN_ROWS_COLUMNS,
                          le=MAX_ROWS_COLUMNS),
        columns: int = Query(default=...,
                             description='Number of columns of the game board',
                             ge=MIN_ROWS_COLUMNS,
                             le=MAX_ROWS_COLUMNS)
) -> NewGameResponse:

    uuid = 1
    active_games[uuid] = GameManager.new_game(rows=rows, columns=columns)
    starting_tiles = active_games[uuid].tile_creation_history
    return NewGameResponse(uuid=uuid, startingTiles=starting_tiles)


@app.get(path='/move-tiles', response_model=MoveResponse)
def move_tiles(uuid: int, direction: Direction) -> MoveResponse:
    active_games[uuid].move_tiles(direction)
    active_games[uuid].create_new_tile()
    return MoveResponse(score=active_games[uuid].score,
                        nextTile=active_games[uuid].tile_creation_history[-1])


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

    db.leaderBoard.insert_one(game_over_info.dict())


@app.get(path='/leader-board-top-10')
def get_leader_board_top_10(
        rows: int = Query(default=...,
                          description='Number of rows of the game board',
                          ge=MIN_ROWS_COLUMNS,
                          le=MAX_ROWS_COLUMNS),
        columns: int = Query(default=...,
                             description='Number of columns of the game board',
                             ge=MIN_ROWS_COLUMNS,
                             le=MAX_ROWS_COLUMNS)
) -> list[dict[str, str | int]]:
    """
    Retrieves the top 10 scores and usernames for a given board size.

    Args:
    - **rows** (int): Number of rows of the game board.
    - **columns** (int): Number of columns of the game board.

    Returns:
    - list[dict[str, str | int]]: List of dictionaries containing the names and
        scores of the leader board.
    """

    query_result = db.leaderBoard.aggregate(
        pipeline=[{'$match': {'rows': rows, 'columns': columns}},
                  {'$sort': {'score': -1}},
                  {'$limit': 10},
                  {'$project': {'_id': False, 'name': True, 'score': True}}]
    )
    return list(query_result)
