from enum import Enum
from pathlib import Path

DIRPATH_REPO = Path(__file__).parent.parent.parent
DIRPATH_FRONT_END = DIRPATH_REPO / 'src' / 'front_end'
DIRPATH_IMAGES = DIRPATH_REPO / 'images'

MIN_ROWS_COLUMNS = 3
MAX_ROWS_COLUMNS = 6

MAX_USERNAME_LENGTH = 50

NEW_TILE_VALUES = [1, 2]
NEW_TILE_PROBABILITIES = [0.9, 0.1]


class Direction(str, Enum):
    left = 'left'
    up = 'up'
    right = 'right'
    down = 'down'
