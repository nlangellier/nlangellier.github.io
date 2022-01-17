from enum import Enum

from pydantic import BaseModel, Field

from .constants import (LEADER_BOARD_LENGTH, MAX_ROWS_COLUMNS,
                        MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS, NEW_TILE,
                        NUM_STARTING_TILES, UUID_LENGTH)


class Direction(str, Enum):
    left = 'left'
    up = 'up'
    right = 'right'
    down = 'down'


class Tile(BaseModel):
    row: int = Field(default=...,
                     description='Tile row coordinate',
                     ge=0, lt=MAX_ROWS_COLUMNS)
    column: int = Field(default=...,
                        description='Tile row coordinate',
                        ge=0, lt=MAX_ROWS_COLUMNS)
    value: int = Field(default=...,
                       description='Log base 2 of tile text',
                       ge=1)


class NewGameResponse(BaseModel):
    uuid: str = Field(default=...,
                      description='Game ID',
                      min_length=UUID_LENGTH,
                      max_length=UUID_LENGTH)
    startingTiles: list[Tile] = Field(default=...,
                                      description='List of starting tiles',
                                      min_items=NUM_STARTING_TILES,
                                      max_items=NUM_STARTING_TILES)


class LoadGameResponse(BaseModel):
    rows: int = Field(default=...,
                      description='Number of rows of the game board',
                      ge=MIN_ROWS_COLUMNS,
                      le=MAX_ROWS_COLUMNS)
    columns: int = Field(default=...,
                         description='Number of columns of the game board',
                         ge=MIN_ROWS_COLUMNS,
                         le=MAX_ROWS_COLUMNS)
    tileCreationHistory: list[Tile] = Field(default=...,
                                            description='List of tiles',
                                            min_items=NUM_STARTING_TILES)
    moveHistory: list[Direction] = Field(default=...,
                                         description='List of player moves')


class MoveResponse(BaseModel):
    nextTile: Tile = Field(default=..., description='Next tile after move')


class LeaderBoardEntry(BaseModel):
    name: str = Field(default=...,
                      description='Name of player',
                      max_length=MAX_USERNAME_LENGTH)
    score: int = Field(default=..., description='Final score of game', ge=0)


class LeaderBoardResponse(BaseModel):
    leaders: list[LeaderBoardEntry] = Field(default=...,
                                            description='List of leaders',
                                            min_items=0,
                                            max_items=LEADER_BOARD_LENGTH)
