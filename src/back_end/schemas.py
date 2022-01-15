from enum import Enum

from pydantic import BaseModel, Field

from .constants import MAX_ROWS_COLUMNS, MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS

TileCoordinates = list[int]


class Tile(BaseModel):
    current_coord: TileCoordinates = Field(default=...,
                                           description='Current coordinates',
                                           min_items=2, max_items=2,
                                           ge=0, lt=MAX_ROWS_COLUMNS)
    next_coord: TileCoordinates = Field(default=...,
                                        description='Next coordinates',
                                        min_items=2, max_items=2,
                                        ge=0, lt=MAX_ROWS_COLUMNS)
    value: int = Field(default=...,
                       description='Log base 2 of tile text',
                       ge=0)
    is_merged: bool = Field(default=False,
                            description='Whether the tile is merged')
    is_new: bool = Field(default=False,
                         description='Whether the tile is new')

    def merge_with(self, other: 'Tile') -> None:
        self.is_merged = True
        other.is_merged = True

    @classmethod
    def new_from(cls, other: 'Tile') -> 'Tile':
        return cls(current_coord=other.next_coord,
                   next_coord=other.next_coord,
                   value=other.value + 1,
                   is_new=True)


class Direction(str, Enum):
    left = 'left'
    up = 'up'
    right = 'right'
    down = 'down'


class GameStateResponse(BaseModel):
    score: int = Field(default=..., description='Current game score', ge=0)
    tiles: list[Tile] = Field(default=..., description='List of tiles')
    available_moves: list[Direction] = Field(default=...,
                                             description='List of moves')


class NewGameResponse(GameStateResponse):
    uuid: int = Field(default=..., description='Game ID')


class GameState(BaseModel):
    values: list[list[int]] = Field(default=...,
                                    description='The state of the game board',
                                    min_items=MIN_ROWS_COLUMNS,
                                    max_items=MAX_ROWS_COLUMNS,
                                    ge=0)


class GameOverInfo(BaseModel):
    name: str = Field(default='Anonymous',
                      description='The username of the player',
                      max_length=MAX_USERNAME_LENGTH)
    score: int = Field(default=...,
                       description='The final score of the game',
                       ge=0)
    rows: int = Field(default=...,
                      description='Number of rows of the game board',
                      ge=MIN_ROWS_COLUMNS,
                      le=MAX_ROWS_COLUMNS)
    columns: int = Field(default=...,
                         description='Number of columns of the game board',
                         ge=MIN_ROWS_COLUMNS,
                         le=MAX_ROWS_COLUMNS)
