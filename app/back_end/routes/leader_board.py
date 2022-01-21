from fastapi import APIRouter, Query
from pymongo import DESCENDING

from ..constants import (LEADER_BOARD_LENGTH, MAX_ROWS_COLUMNS,
                         MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS, UUID_LENGTH)
from ..database_client import db
from ..schemas import LeaderBoardEntry, LeaderBoardResponse
from .game import active_games

router = APIRouter()


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


@router.post(path='/leader-board', response_model=None)
def post_game_to_leader_board(
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
