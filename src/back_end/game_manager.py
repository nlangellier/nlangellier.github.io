import numpy as np

from .constants import NEW_TILE_PROBABILITIES, NEW_TILE_VALUES
from .schemas import Tile


class GameManager:

    num_rotations = {'left': 0, 'up': 1, 'right': 2, 'down': 3}

    def __init__(self, rows: int = 4, columns: int = 4) -> None:
        self.rng = np.random.default_rng()

        self.tile_creation_history: list[Tile] = []
        self.move_history: list[str] = []
        self.score = 0

        self.state = np.zeros(shape=(rows, columns), dtype=np.uint8)
        self.create_new_tile()
        self.create_new_tile()

    @classmethod
    def new_game(cls, rows: int = 4, columns: int = 4) -> 'GameManager':
        return cls(rows=rows, columns=columns)

    def create_new_tile(self) -> None:
        indices_of_empty_cells = np.argwhere(self.state == 0)
        i, j = self.rng.choice(indices_of_empty_cells)
        value: int = self.rng.choice(NEW_TILE_VALUES, p=NEW_TILE_PROBABILITIES)
        self.state[i, j] = value

        new_tile = Tile(coordinates=[i, j], value=value)
        self.tile_creation_history.append(new_tile)

    def move_is_available(self, direction: str) -> bool:
        rotated_state = np.rot90(self.state, k=self.num_rotations[direction])

        for row in rotated_state:
            trimmed_row = np.trim_zeros(row, trim='b')
            diff_of_adjacent_tiles = np.diff(row[row != 0])
            if (0 in trimmed_row) or (0 in diff_of_adjacent_tiles):
                return True

        return False

    def get_state_from_left_shift(self, state: np.ndarray) -> np.ndarray:

        for i, row in enumerate(state):
            j = 0
            prev_tile_value: int | None = None

            for cell_value in row:
                if cell_value == 0:
                    continue

                if prev_tile_value is None or cell_value != prev_tile_value:
                    state[i, j] = cell_value
                    prev_tile_value = cell_value
                    j += 1
                else:
                    state[i, j - 1] = cell_value + 1
                    prev_tile_value = None
                    self.score += 2**(cell_value + 1)

            if j < state.shape[1]:
                state[i, j:] = 0

        return state

    def get_state_from_right_shift(self, state: np.ndarray) -> np.ndarray:
        flipped_state = np.fliplr(state)
        next_flipped_state = self.get_state_from_left_shift(flipped_state)
        return np.fliplr(next_flipped_state)

    def get_state_from_up_shift(self, state: np.ndarray) -> np.ndarray:
        transpose_state = np.transpose(state)
        next_transpose_state = self.get_state_from_left_shift(transpose_state)
        return np.transpose(next_transpose_state)

    def get_state_from_down_shift(self, state: np.ndarray) -> np.ndarray:
        flipped_state = np.flipud(state)
        next_flipped_state = self.get_state_from_up_shift(flipped_state)
        return np.flipud(next_flipped_state)

    def move_tiles(self, direction: str) -> None:
        if not self.move_is_available(direction):
            return

        match direction:
            case 'left':
                self.state = self.get_state_from_left_shift(self.state)
            case 'right':
                self.state = self.get_state_from_right_shift(self.state)
            case 'up':
                self.state = self.get_state_from_up_shift(self.state)
            case 'down':
                self.state = self.get_state_from_down_shift(self.state)

        self.move_history.append(direction)
