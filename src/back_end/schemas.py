from enum import Enum

from pydantic import BaseModel, Field

from .constants import (LEADER_BOARD_LENGTH, MAX_ROWS_COLUMNS,
                        MAX_USERNAME_LENGTH, NEW_TILE, UUID_LENGTH)


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
                                      min_items=len(NEW_TILE['values']),
                                      max_items=len(NEW_TILE['values']))


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
