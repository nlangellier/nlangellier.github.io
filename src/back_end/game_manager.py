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

    def move_tiles_left(self) -> None:

        for i, row in enumerate(self.state):
            j = 0
            prev_tile_value: int | None = None

            for cell_value in row:
                if cell_value == 0:
                    continue

                if prev_tile_value is None or cell_value != prev_tile_value:
                    self.state[i, j] = cell_value
                    prev_tile_value = cell_value
                    j += 1
                else:
                    self.state[i, j - 1] = cell_value + 1
                    prev_tile_value = None
                    self.score += 2**(cell_value + 1)

            if j < self.state.shape[1]:
                self.state[i, j:] = 0

    def move_tiles(self, direction: str) -> None:
        if not self.move_is_available(direction):
            return

        if direction == 'down':
            self.state = np.flipud(self.state)
        if direction in ['up', 'down']:
            self.state = np.transpose(self.state)
        if direction == 'right':
            self.state = np.fliplr(self.state)

        self.move_tiles_left()

        if direction == 'right':
            self.state = np.fliplr(self.state)
        if direction in ['up', 'down']:
            self.state = np.transpose(self.state)
        if direction == 'down':
            self.state = np.flipud(self.state)

        self.move_history.append(direction)
