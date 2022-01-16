import numpy as np

from .constants import NEW_TILE
from .schemas import Tile


class GameManager:

    _num_rotations = {'left': 0, 'up': 1, 'right': 2, 'down': 3}

    def __init__(self, rows: int = 4, columns: int = 4) -> None:
        self._rng = np.random.default_rng()

        self.tile_creation_history: list[Tile] = []
        self.move_history: list[str] = []
        self.score = 0

        self._state = np.zeros(shape=(rows, columns), dtype=np.uint8)
        self.create_new_tile()
        self.create_new_tile()

    @classmethod
    def new_game(cls, rows: int = 4, columns: int = 4) -> 'GameManager':
        return cls(rows=rows, columns=columns)

    @property
    def rows(self):
        return self._state.shape[0]

    @property
    def columns(self):
        return self._state.shape[1]

    def create_new_tile(self) -> None:
        indices_of_empty_cells = np.argwhere(self._state == 0)
        i, j = self._rng.choice(indices_of_empty_cells)
        value = self._rng.choice(NEW_TILE['values'],
                                 p=NEW_TILE['probabilities'])
        self._state[i, j] = value

        new_tile = Tile(row=i, column=j, value=value)
        self.tile_creation_history.append(new_tile)

    def _move_is_available(self, direction: str) -> bool:
        rotated_state = np.rot90(self._state, k=self._num_rotations[direction])

        for row in rotated_state:
            trimmed_row = np.trim_zeros(row, trim='b')
            diff_of_adjacent_tiles = np.diff(row[row != 0])
            if (0 in trimmed_row) or (0 in diff_of_adjacent_tiles):
                return True

        return False

    def _move_tiles_left(self) -> None:

        for i, row in enumerate(self._state):
            j = 0
            prev_tile_value: int | None = None

            for cell_value in row:
                if cell_value == 0:
                    continue

                if prev_tile_value is None or cell_value != prev_tile_value:
                    self._state[i, j] = cell_value
                    prev_tile_value = cell_value
                    j += 1
                else:
                    self._state[i, j - 1] = cell_value + 1
                    prev_tile_value = None
                    self.score += 2**(cell_value + 1)

            if j < self._state.shape[1]:
                self._state[i, j:] = 0

    def move_tiles(self, direction: str) -> None:
        if not self._move_is_available(direction):
            return

        if direction == 'down':
            self._state = np.flipud(self._state)
        if direction in ['up', 'down']:
            self._state = np.transpose(self._state)
        if direction == 'right':
            self._state = np.fliplr(self._state)

        self._move_tiles_left()

        if direction == 'right':
            self._state = np.fliplr(self._state)
        if direction in ['up', 'down']:
            self._state = np.transpose(self._state)
        if direction == 'down':
            self._state = np.flipud(self._state)

        self.move_history.append(direction)
