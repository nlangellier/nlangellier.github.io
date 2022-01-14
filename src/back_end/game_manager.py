import numpy as np

from .constants import NEW_TILE_PROBABILITIES, NEW_TILE_VALUES
from .schemas import Tile, TileCoordinates


class GameManager:

    num_rotations = {'left': 0, 'up': 1, 'right': 2, 'down': 3}

    def __init__(self, rows: int = 4, columns: int = 4) -> None:
        self.rng = np.random.default_rng()

        self.tile_creation_history: list[TileCoordinates] = []
        self.move_history: list[str] = []
        self.score = 0

        self.state = np.zeros(shape=(rows, columns), dtype=np.uint8)
        tile0 = self.create_new_tile()
        tile1 = self.create_new_tile()
        self.initial_tiles = [tile0, tile1]

    @classmethod
    def from_state(cls,
                   state: np.ndarray,
                   tile_creation_history: list[TileCoordinates] | None = None,
                   score: int = 0) -> 'GameManager':
        game_manager = cls()
        game_manager.state = state
        if tile_creation_history is None:
            game_manager.tile_creation_history = []
        else:
            game_manager.tile_creation_history = tile_creation_history
        game_manager.score = score
        return game_manager

    def create_new_tile(self) -> Tile:
        indices_of_empty_cells = np.argwhere(self.state == 0)
        i, j = self.rng.choice(indices_of_empty_cells)
        value: int = self.rng.choice(NEW_TILE_VALUES, p=NEW_TILE_PROBABILITIES)
        self.state[i, j] = value
        self.tile_creation_history.append([i, j])

        return Tile(current_coord=[i, j], next_coord=[i, j],
                    value=value, is_new=True)

    @property
    def rows(self) -> int:
        return self.state.shape[0]

    @property
    def columns(self) -> int:
        return self.state.shape[1]

    def move_is_available(self, direction: str) -> bool:
        rotated_state = np.rot90(self.state, k=self.num_rotations[direction])

        for row in rotated_state:
            trimmed_row = np.trim_zeros(row, trim='b')
            diff_of_adjacent_tiles = np.diff(row[row != 0])
            if (0 in trimmed_row) or (0 in diff_of_adjacent_tiles):
                return True

        return False

    @property
    def is_over(self) -> bool:
        for direction in ['left', 'up', 'right', 'down']:
            if self.move_is_available(direction):
                return False

        return True

    @property
    def available_moves(self) -> list[str]:
        available_moves = []

        for direction in ['left', 'up', 'right', 'down']:
            if self.move_is_available(direction):
                available_moves.append(direction)

        return available_moves

    @staticmethod
    def get_tiles_from_left_shift(state: np.ndarray) -> list[Tile]:
        tiles = []

        for i, row in enumerate(state):
            next_col = 0
            prev_tile: Tile | None = None

            for j, cell_value in enumerate(row):
                if cell_value == 0:
                    continue

                current_tile = Tile(current_coord=[i, j],
                                    next_coord=[i, next_col],
                                    value=cell_value)
                tiles.append(current_tile)

                if prev_tile is None or current_tile.value != prev_tile.value:
                    next_col += 1
                    prev_tile = current_tile

                else:
                    current_tile.next_coord = prev_tile.next_coord
                    prev_tile.merge_with(current_tile)
                    new_tile = Tile.new_from(current_tile)
                    tiles.append(new_tile)
                    prev_tile = None

        return tiles

    def get_tiles_from_right_shift(self, state: np.ndarray) -> list[Tile]:
        flipped_state = np.fliplr(state)
        tiles = self.get_tiles_from_left_shift(flipped_state)
        for tile in tiles:
            i, j = tile.current_coord
            tile.current_coord = (i, self.columns - j - 1)
            i, j = tile.next_coord
            tile.next_coord = (i, self.columns - j - 1)

        return tiles

    def get_tiles_from_up_shift(self, state: np.ndarray) -> list[Tile]:
        transposed_state = np.transpose(state)
        tiles = self.get_tiles_from_left_shift(transposed_state)
        for tile in tiles:
            i, j = tile.current_coord
            tile.current_coord = (j, i)
            i, j = tile.next_coord
            tile.next_coord = (j, i)

        return tiles

    def get_tiles_from_down_shift(self, state: np.ndarray) -> list[Tile]:
        flipped_state = np.flipud(state)
        tiles = self.get_tiles_from_up_shift(flipped_state)
        for tile in tiles:
            i, j = tile.current_coord
            tile.current_coord = (self.rows - i - 1, j)
            i, j = tile.next_coord
            tile.next_coord = (self.rows - i - 1, j)

        return tiles

    def update_state(self, tiles: list[Tile]) -> None:
        new_state = np.zeros_like(self.state)

        for tile in tiles:
            if tile.is_merged:
                continue
            new_state[tile.next_coord] = tile.value

        self.state = new_state

    def move(self, direction: str) -> list[Tile]:
        if self.move_is_available(direction):
            if direction == 'left':
                tiles = self.get_tiles_from_left_shift(self.state)
            elif direction == 'right':
                tiles = self.get_tiles_from_right_shift(self.state)
            elif direction == 'up':
                tiles = self.get_tiles_from_up_shift(self.state)
            elif direction == 'down':
                tiles = self.get_tiles_from_down_shift(self.state)
            else:
                raise ValueError(f'Invalid direction: {direction}')

            self.update_state(tiles)
            self.move_history.append(direction)
            new_tile = self.create_new_tile()
            tiles.append(new_tile)
            return tiles

        raise ValueError(f'{direction} is not an available move.')
