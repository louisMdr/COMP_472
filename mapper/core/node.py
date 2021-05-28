from typing import List, Union, Optional

from mapper.core.edge import Edge


class Node:
    """

    Class representing a node in the Graph of the map

    """
    SEQ_INT = 0

    def __init__(self, row_idx: int, col_idx: int, row_total: int, name: str = None):
        self.row_idx: int = row_idx
        self.col_idx: int = col_idx
        self.row_total: int = row_total
        if name is None:
            self.name: str = self.create_name(row_idx, col_idx, row_total)
        else:
            self.name = name
        self.edges: List[Edge] = []
        self.old_name: Optional[str] = None

    @staticmethod
    def reset():
        Node.SEQ_INT = 0

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def get_user_point_label_on_axis(self, vertical_axis: bool, divisor: int) -> Union[str, None]:
        for edge in self.edges:
            if edge.get_other_node(self).name in ['START', 'END'] and edge.edge_matches_axis_divisor(self, vertical_axis, divisor):
                return edge.get_other_node(self).name
        return None

    @staticmethod
    def create_name(row_idx: int, col_idx: int, row_total: int) -> str:
        # the name is a sequential character code A, B, C .. AAB ... BAD ...
        seq_int = Node.SEQ_INT
        Node.SEQ_INT += 1
        num_extra = int(seq_int / 26)
        extra_char = chr(num_extra + 64) if num_extra != 0 else ''
        char = chr((seq_int % 26) + 65)
        name = f'{extra_char}{char}'
        return name

    def revert_name(self):
        self.name = self.old_name
        self.old_name = None

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.old_name = self.name
        self.name = name


    def remove_edge_by_idx(self, idx: int):
        self.edges.pop(idx)
