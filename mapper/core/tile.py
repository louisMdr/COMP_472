from __future__ import annotations
from typing import Optional


class Tile:
    """

    Class representing one of the Grid squares of the Map

    """
    def __init__(self, row_idx: int, col_idx: int, num_in_row: int):
        self.row_idx: int = row_idx
        self.col_idx: int = col_idx
        self.num_in_row: int = num_in_row
        self.num_display_rows: int = 9
        self.display_width: int = 9
        self.tile_type: Optional[TileType] = None

    def set_type(self, tile_type: TileType):
        self.tile_type = tile_type

    def display_size(self) -> int:
        return self.num_display_rows - 1

    def to_str_display(self, iteration: int, include_right: bool = False, name: str = None) -> str:
        if iteration in [0, self.num_display_rows - 1]:
            # top or bottom edge
            return self.__horizontal_bound(name)
        elif int((self.num_display_rows - 1) / 2) == iteration:
            # in the middle, display the idx and the tile-type
            return self.__content_label(include_right)
        else:
            # return empty space
            return self.__fill(include_right)

    def __fill(self, include_right: bool = False):
        row_str = '|' + (self.display_width * ' ')
        row_str = row_str if not include_right else f'{row_str}|'
        return row_str

    def __content_label(self, include_right: bool = False) -> str:
        idx_label = (self.num_in_row * self.row_idx) + self.col_idx + 1
        tile_label = f'-{str(self.tile_type)}' if self.tile_type is not None else ''
        label = f'{idx_label}{tile_label}'
        padding = self.display_width - len(label)
        left_padding = int(padding / 2)
        right_padding = padding - left_padding
        return f'|{left_padding * " "}{label}{right_padding * " "}{"|" if include_right else ""}'

    def __horizontal_bound(self, name: str = None) -> str:
        return '-' * ((self.display_width + 1) - (0 if name is None else len(name)))


class TileTypeFactory:

    @staticmethod
    def validate(tile_type: str) -> bool:
        if tile_type.upper() in ['V', 'Q', 'P']:
            return True
        else:
            return False

    @staticmethod
    def create_type(tile_type: str) -> TileType:
        if tile_type.upper() == 'V':
            class_name = Vaccine
        elif tile_type.upper() == 'Q':
            class_name = Quarantine
        elif tile_type.upper() == 'P':
            class_name = PlayGround
        else:
            raise RuntimeError('Invalid TileType')
        return class_name()


class TileType:
    pass


class Vaccine(TileType):
    def __str__(self):
        return 'V'


class PlayGround(TileType):
    def __str__(self):
        return 'P'


class Quarantine(TileType):
    def __str__(self):
        return 'Q'
