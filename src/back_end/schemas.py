from pydantic import BaseModel, Field

from .constants import MAX_ROWS_COLUMNS, MAX_USERNAME_LENGTH, MIN_ROWS_COLUMNS

TileCoordinates = tuple[int, int]


class Tile(BaseModel):
    current_coord: TileCoordinates
    next_coord: TileCoordinates
    value: int
    is_merged: bool = False
    is_new: int = False

    def merge_with(self, other: 'Tile') -> None:
        self.is_merged = True
        other.is_merged = True

    @classmethod
    def new_from(cls, other: 'Tile') -> 'Tile':
        return cls(current_coord=other.next_coord,
                   next_coord=other.next_coord,
                   value=other.value + 1,
                   is_new=True)


class GameState(BaseModel):
    values: list[list[int]] = Field(default=None,
                                    description='The state of the game board',
                                    min_items=MIN_ROWS_COLUMNS,
                                    max_items=MAX_ROWS_COLUMNS,
                                    ge=0)


class GameOverInfo(BaseModel):
    name: str = Field(default='Anonymous',
                      description='The username of the player',
                      max_length=MAX_USERNAME_LENGTH)
    score: int = Field(default=None,
                       description='The final score of the game',
                       ge=0)
    rows: int = Field(default=None,
                      description='Number of rows of the game board',
                      ge=MIN_ROWS_COLUMNS,
                      le=MAX_ROWS_COLUMNS)
    columns: int = Field(default=None,
                         description='Number of columns of the game board',
                         ge=MIN_ROWS_COLUMNS,
                         le=MAX_ROWS_COLUMNS)
