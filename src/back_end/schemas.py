from pydantic import BaseModel, Field

from .constants import MAX_ROWS_COLUMNS, MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS


class Tile(BaseModel):
    coordinates: list[int] = Field(default=...,
                                   description='Tile coordinates',
                                   min_items=2, max_items=2,
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
    score: int = Field(default=..., description='Current game score', ge=0)
    nextTile: Tile = Field(default=..., description='New tile after move')


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
