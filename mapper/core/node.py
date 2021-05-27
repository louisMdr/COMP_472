from typing import List

from mapper.core.edge import Edge


class Node:
    """

    Class representing a node in the Graph of the map

    """
    def __init__(self, row_idx: int, col_idx: int, row_total: int):
        self.row_idx: int = row_idx
        self.col_idx: int = col_idx
        self.name: str = self.create_name(row_idx, col_idx, row_total)
        self.edges: List[Edge] = []

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    @staticmethod
    def create_name(row_idx: int, col_idx: int, row_total: int) -> str:
        # the name is a sequential character code A, B, C .. AAB ... BAD ...
        seq_int = (row_idx * row_total) + col_idx
        num_extra = int(seq_int / 26)
        extra_char = chr(num_extra + 64) if num_extra != 0 else ''
        char = chr((seq_int % 26) + 65)
        name = f'{extra_char}{char}'
        return name

    def get_name(self) -> str:
        return self.name
