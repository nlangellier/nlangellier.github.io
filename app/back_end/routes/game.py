import random

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from ..constants import MAX_ROWS_COLUMNS, MIN_ROWS_COLUMNS, UUID_LENGTH
from ..database_client import get_db
from ..game_manager import GameManager
from ..id_generator import generate_uuid
from ..schemas import (Direction, LoadGameResponse, MoveResponse,
                       NewGameResponse)

router = APIRouter()

active_games: dict[str, GameManager] = {}


@router.get(path='/game/new', response_model=NewGameResponse)
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


@router.get(path='/game/load', response_model=LoadGameResponse)
def load_game(
    uuid: str = Query(default=...,
                      description='Game ID',
                      min_length=UUID_LENGTH,
                      max_length=UUID_LENGTH),
    db: Database = Depends(get_db)
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


@router.get(path='/game/move-tiles', response_model=MoveResponse)
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


@router.get(path='/game/hint', response_model=Direction)
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
