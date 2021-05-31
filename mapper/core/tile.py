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
        self.label: Optional[str] = None

    def set_type(self, tile_type: TileType):
        self.tile_type = tile_type

    def display_size(self) -> int:
        return self.num_display_rows - 1

    def to_str_display(self,
                       iteration: int,
                       include_right: bool = False,
                       name: str = None,
                       horizontal_label: str = None,
                       left_vertical_label: str = None,
                       right_vertical_label: str = None,
                       leftmost: bool = False,
                       middle_label: str = None) -> str:
        if iteration in [0, self.num_display_rows - 1]:
            # top or bottom edge
            return self.__horizontal_bound(name, horizontal_label=horizontal_label)
        elif int((self.num_display_rows - 1) / 2) == iteration:
            # in the middle, display the idx and the tile-type
            return self.__content_label(include_right)
        elif int((self.num_display_rows - 1) / 2) - 1 == iteration:
            # return empty space
            return self.__fill(
                include_right,
                middle_label=middle_label
            )
        else:
            # return empty space
            return self.__fill(
                include_right,
                left_vertical_label=left_vertical_label,
                right_vertical_label=right_vertical_label,
                leftmost=leftmost
            )

    def __fill(self,
               include_right: bool = False,
               left_vertical_label: str = None,
               right_vertical_label: str = None,
               leftmost: bool = False,
               middle_label: str = None) -> str:
        """
        Creates string representing an inner row of the tile that is not topmost, bottommost, or middle
        """
        if middle_label is not None:
            dw = self.display_width - len(middle_label)
            left_pad = int(dw / 2)
            right_pad = dw - left_pad
            right_char = '' if not include_right else '|'
            return f'|{" " * left_pad}{middle_label}{" " * right_pad}{right_char}'
        else:
            left_characters = '|' if left_vertical_label is None else left_vertical_label
            if left_vertical_label is None:
                dw = self.display_width
            elif left_vertical_label is not None and leftmost:
                dw = self.display_width - len(left_vertical_label) + 1
            else:
                dw = self.display_width - int(len(left_vertical_label) / 2)
            row_str = dw * ' '
            right_characters = '' if not include_right else ('|' if right_vertical_label is None else right_vertical_label)
            return f'{left_characters}{row_str}{right_characters}'

    def __content_label(self, include_right: bool = False) -> str:
        """
        Creates representation of the middle row of a tile
        """
        idx_label = (self.num_in_row * self.row_idx) + self.col_idx + 1
        tile_label = f'-{str(self.tile_type)}' if self.tile_type is not None else ''
        self.label = f'{idx_label}{tile_label}'
        padding = self.display_width - len(self.label)
        left_padding = int(padding / 2)
        right_padding = padding - left_padding
        return f'|{left_padding * " "}{self.label}{right_padding * " "}{"|" if include_right else ""}'

    def __horizontal_bound(self, name: str = None, horizontal_label: str = None) -> str:
        """
        Creates topmost and bottommost rows of a tile
        """
        total_len = (self.display_width + 1) - (0 if name is None else len(name))
        if horizontal_label is None:
            return '-' * total_len
        else:
            pad_len = total_len - len(horizontal_label)
            left_pad_len = int(pad_len / 2)
            right_pad_len = pad_len - left_pad_len
            return f'{"-" * left_pad_len}{horizontal_label}{"-" * right_pad_len}'


class TileTypeFactory:
    """
    Creates a child class of TileType
    """
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
