from fastapi import APIRouter, Depends, Query
from pymongo import DESCENDING
from pymongo.database import Database

from ...constants import (LEADER_BOARD_LENGTH, MAX_ROWS_COLUMNS,
                          MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS, UUID_LENGTH)
from ...database_client import get_db
from ...schemas import LeaderBoardEntry, LeaderBoardResponse
from .game import active_games

router = APIRouter(prefix='/leader-board', tags=['Leader Board'])


@router.get(path='/', response_model=LeaderBoardResponse)
def get_leader_board(
        rows: int = Query(default=...,
                          description='Number of rows of the game board',
                          ge=MIN_ROWS_COLUMNS,
                          le=MAX_ROWS_COLUMNS),
        columns: int = Query(default=...,
                             description='Number of columns of the game board',
                             ge=MIN_ROWS_COLUMNS,
                             le=MAX_ROWS_COLUMNS),
        db: Database = Depends(get_db)
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

    query_result = db.games.find(
        filter={'rows': rows, 'columns': columns},
        sort=[('score', DESCENDING)],
        limit=LEADER_BOARD_LENGTH,
        projection={'_id': False, 'name': True, 'score': True}
    )
    leaders = [LeaderBoardEntry(**leader) for leader in query_result]
    return LeaderBoardResponse(leaders=leaders)


@router.post(path='/', response_model=None)
def post_game_to_leader_board(
        uuid: str = Query(default=...,
                          description='Game ID',
                          min_length=UUID_LENGTH,
                          max_length=UUID_LENGTH),
        name: str = Query(default='Anonymous',
                          description='Player name',
                          max_length=MAX_USERNAME_LENGTH),
        db: Database = Depends(get_db)
) -> None:
    """
    Updates the leader board database with the final game state from a game ID.

    Args:
    - **uuid** (str): The game ID.
    - **name** (str): The player name.
    """

    if uuid not in active_games:
        raise ValueError(f'Game {uuid} is not an active game.')
    if db.games.count_documents({'_id': uuid}, limit=1) > 0:
        active_games.pop(uuid)
        raise ValueError(f'Game {uuid} already exists in the database.')

    game = active_games[uuid]

    tile_creation_history = []
    for sequence_id, tile in enumerate(game.tile_creation_history):
        tile_creation_history.append({'tileSequenceID': sequence_id,
                                      'row': tile.row,
                                      'column': tile.column,
                                      'value': tile.value,
                                      'gameID': uuid})

    move_history = []
    for sequence_id, direction in enumerate(game.move_history):
        move_history.append({'moveSequenceID': sequence_id,
                             'direction': direction,
                             'gameID': uuid})

    db.games.insert_one({'_id': uuid,
                         'name': name,
                         'score': game.score,
                         'rows': game.rows,
                         'columns': game.columns})
    db.tileCreationHistory.insert_many(tile_creation_history)
    db.moveHistory.insert_many(move_history)

    active_games.pop(uuid)
