from enum import Enum

from pydantic import BaseModel, Field

from .constants import MAX_ROWS_COLUMNS


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
    uuid: int = Field(default=..., description='Game ID')
    startingTiles: list[Tile] = Field(default=...,
                                      description='List of starting tiles',
                                      min_items=2, max_items=2)


class MoveResponse(BaseModel):
    nextTile: Tile = Field(default=..., description='Next tile after move')


class LeaderBoardEntry(BaseModel):
    name: str = Field(default=..., description='Name of player', max_length=50)
    score: int = Field(default=..., description='Final score of game', ge=0)


class LeaderBoardResponse(BaseModel):
    leaders: list[LeaderBoardEntry] = Field(default=...,
                                            description='List of leaders',
                                            min_items=0, max_items=10)
