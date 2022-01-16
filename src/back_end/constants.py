import string
from pathlib import Path

DIRPATH_REPO = Path(__file__).parent.parent.parent
DIRPATH_FRONT_END = DIRPATH_REPO / 'src' / 'front_end'
DIRPATH_IMAGES = DIRPATH_REPO / 'images'

MIN_ROWS_COLUMNS = 3
MAX_ROWS_COLUMNS = 6

MAX_USERNAME_LENGTH = 50

LEADER_BOARD_LENGTH = 10

NEW_TILE = {'values': [1, 2], 'probabilities': [0.9, 0.1]}

UUID_ALPHABET = string.ascii_letters + string.digits
UUID_LENGTH = 40
