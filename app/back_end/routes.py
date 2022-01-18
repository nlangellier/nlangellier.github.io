import random
from getpass import getpass

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from pymongo import DESCENDING, MongoClient

from .constants import (DIRPATH_FRONT_END, LEADER_BOARD_LENGTH,
                        MAX_ROWS_COLUMNS, MAX_USERNAME_LENGTH,
                        MIN_ROWS_COLUMNS, UUID_LENGTH)
from .game_manager import GameManager
from .id_generator import generate_uuid
from .models import (Direction, LeaderBoardEntry, LeaderBoardResponse,
                     LoadGameResponse, MoveResponse, NewGameResponse)

router = APIRouter()

username = input('MongoDB username: ')
password = getpass(prompt='MongoDB password: ')
mongo_client = MongoClient(host='localhost',
                           port=27017,
                           username=username,
                           password=password,
                           authSource='admin',
                           authMechanism='SCRAM-SHA-256')
db = mongo_client['2048Infinite']

active_games: dict[str, GameManager] = {}


@router.get(path='/')
def home_page() -> FileResponse:
    """
    Loads the 2048 Infinite home page.

    Returns:
    - FileResponse: The static webpage at front-end/index.html
    """

    return FileResponse(DIRPATH_FRONT_END / 'index.html')


@router.get(path='/leader-board', response_model=LeaderBoardResponse)
def get_leader_board(
        rows: int = Query(default=...,
                          description='Number of rows of the game board',
                          ge=MIN_ROWS_COLUMNS,
                          le=MAX_ROWS_COLUMNS),
        columns: int = Query(default=...,
                             description='Number of columns of the game board',
                             ge=MIN_ROWS_COLUMNS,
                             le=MAX_ROWS_COLUMNS)
) -> LeaderBoardResponse:
    """
    Retrieves the top scores and usernames for a given board size.

    Args:
    - **rows** (int): Number of rows of the game board.
    - **columns** (int): Number of columns of the game board.

    Returns:
    - LeaderBoardResponse: List of dictionaries containing the names and scores
        of the leader board.
    """

    query_result = db.leaderBoard.find(
        filter={'rows': rows, 'columns': columns},
        sort=[('score', DESCENDING)],
        limit=LEADER_BOARD_LENGTH,
        projection={'_id': False, 'name': True, 'score': True}
    )
    leaders = [LeaderBoardEntry(**leader) for leader in query_result]
    return LeaderBoardResponse(leaders=leaders)


@router.get(path='/new-game', response_model=NewGameResponse)
def start_new_game(
        rows: int = Query(default=...,
                          description='Number of rows of the game board',
                          ge=MIN_ROWS_COLUMNS,
                          le=MAX_ROWS_COLUMNS),
        columns: int = Query(default=...,
                             description='Number of columns of the game board',
                             ge=MIN_ROWS_COLUMNS,
                             le=MAX_ROWS_COLUMNS)
) -> NewGameResponse:
    """
    Starts a new game of 2048 Infinite.

    Args:
    - **rows** (int): Number of rows of the game board.
    - **columns** (int): Number of columns of the game board.

    Returns:
    - NewGameResponse: A dictionary containing the game ID and a list of the
        starting tiles with their initial positions and values.
    """

    uuid = generate_uuid()
    active_games[uuid] = GameManager.new_game(rows=rows, columns=columns)
    starting_tiles = active_games[uuid].tile_creation_history
    return NewGameResponse(uuid=uuid, startingTiles=starting_tiles)


@router.get(path='/load-game', response_model=LoadGameResponse)
def load_game(
    uuid: str = Query(default=...,
                      description='Game ID',
                      min_length=UUID_LENGTH,
                      max_length=UUID_LENGTH)
) -> LoadGameResponse:
    """
    Loads a game history from the database with a given game ID.

    Args:
    - **uuid** (str): The game ID.

    Returns:
    - LoadGameResponse: A dictionary with the number of rows and columns as
        well as the tile creation history and the player move history.
    """

    if uuid in active_games:
        raise ValueError(f'Game {uuid} is already an active game.')

    query_result = db.leaderBoard.find_one(
        filter={'_id': uuid},
        projection={'_id': False, 'rows': True, 'columns': True,
                    'tileCreationHistory': True, 'moveHistory': True}
    )

    if query_result is None:
        raise ValueError(f'Game {uuid} not found.')

    load_game_response = LoadGameResponse(**query_result)

    active_games[uuid] = GameManager.load_game(
        rows=load_game_response.rows,
        columns=load_game_response.columns,
        tile_creation_history=load_game_response.tileCreationHistory,
        move_history=load_game_response.moveHistory
    )

    return load_game_response


@router.get(path='/move-tiles', response_model=MoveResponse)
def move_tiles(
        uuid: str = Query(default=...,
                          description='Game ID',
                          min_length=UUID_LENGTH,
                          max_length=UUID_LENGTH),
        direction: Direction = Query(default=...,
                                     description='Direction to move tiles')
) -> MoveResponse:
    """
    Moves the tiles in the given direction and returns the next tile.

    Args:
    - **uuid** (str): The game ID.
    - **direction** (Direction): The direction to move the tiles. One of
        {"left", "up", "right", "down"}.

    Returns:
    - MoveResponse: A dictionary containing the position and value of the next
        tile.
    """

    if uuid not in active_games:
        raise ValueError(f'Game {uuid} is not an active game.')

    active_games[uuid].move_tiles(direction)
    active_games[uuid].create_new_tile()
    return MoveResponse(nextTile=active_games[uuid].tile_creation_history[-1])


@router.get(path='/hint', response_model=Direction)
def get_hint(
        uuid: str = Query(default=...,
                          description='Game ID',
                          min_length=UUID_LENGTH,
                          max_length=UUID_LENGTH)
) -> Direction:
    """
    Computes the next move the AI model would take from the current game state.

    Args:
    - **uuid** (str): The game ID.

    Returns:
    - Direction: The next move the AI model would take. One of {"left", "up",
        "right", "down"}.
    """

    if uuid not in active_games:
        raise ValueError(f'Game {uuid} is not an active game.')

    return random.choice(list(Direction))


@router.post(path='/game-over', response_model=None)
def add_game_to_database(
        uuid: str = Query(default=...,
                          description='Game ID',
                          min_length=UUID_LENGTH,
                          max_length=UUID_LENGTH),
        name: str = Query(default='Anonymous',
                          description='Player name',
                          max_length=MAX_USERNAME_LENGTH)
) -> None:
    """
    Updates the leader board database with the final game state from a game ID.

    Args:
    - **uuid** (str): The game ID.
    - **name** (str): The player name.
    """

    if uuid not in active_games:
        raise ValueError(f'Game {uuid} is not an active game.')
    if db.leaderBoard.count_documents({'_id': uuid}, limit=1) > 0:
        active_games.pop(uuid)
        raise ValueError(f'Game {uuid} already exists in the database.')

    tile_creation_history = [tile.dict() for tile in
                             active_games[uuid].tile_creation_history]

    db.leaderBoard.insert_one(
        {'_id': uuid,
         'name': name,
         'score': active_games[uuid].score,
         'rows': active_games[uuid].rows,
         'columns': active_games[uuid].columns,
         'tileCreationHistory': tile_creation_history,
         'moveHistory': active_games[uuid].move_history}
    )

    active_games.pop(uuid)
