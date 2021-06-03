from __future__ import annotations
from typing import List, Union, Optional, Type

from mapper.core.edge import Edge, DiagonalEdge


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

    def get_user_point_in_tile_label(self, divisor: int) -> Union[str, None]:
        for edge in self.edges:
            if (
                isinstance(edge, DiagonalEdge) and
                edge.get_other_node(self).name in ['START', 'END'] and
                edge.get_other_node(self).is_inside_tile(self.col_idx, self.row_idx, divisor)
            ):
                return edge.get_other_node(self).name
        return None

    def is_inside_tile(self, x: Union[int, float], y: Union[int, float], divisor: int) -> bool:
        diag_x, diag_y = x + 1, y + 1
        node_x, node_y = self.col_idx / divisor, self.row_idx / divisor
        return (
            # make sure the node calling this is a node in the grid
            (isinstance(x, int) and isinstance(y, int)) and
            # make sure this node is not on a grid square
            not (isinstance(self.col_idx, int) and isinstance(self.row_idx, int)) and
            x < node_x < diag_x and
            y < node_y < diag_y
        )

    def get_user_point_label_on_axis(self, vertical_axis: bool, divisor: int) -> Union[str, None]:
        for edge in self.edges:
            if (
                not isinstance(edge, DiagonalEdge) and
                edge.get_other_node(self).name in ['START', 'END'] and
                edge.edge_matches_axis_divisor(self, vertical_axis, divisor)
            ):
                return edge.get_other_node(self).name
        return None

    def get_other_node_on_axis(self, below: bool, vertical: bool, right: bool) -> Union[Edge, None]:
        for edge in self.edges:
            if (
                # must be straight edge on axis
                not isinstance(edge, DiagonalEdge) and
                edge.edge_matches_axis(self, vertical, include_other=True) and
                (
                    # conditions if trying to find a specific vertical edge
                    (
                        vertical and
                        (
                            (below and edge.get_other_node(self).row_idx < self.row_idx) or
                            (not below and edge.get_other_node(self).row_idx > self.row_idx)
                        )
                    ) or
                    # conditions if trying to find a specific horizontal edge
                    (
                        not vertical and
                        (
                            (right and edge.get_other_node(self).col_idx < self.col_idx) or
                            (not right and edge.get_other_node(self).col_idx > self.col_idx)
                        )
                    )
                )
            ):
                return edge
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

    def borders_tile_of_type(self, tile_type: Type) -> bool:
        for edge in self.edges:
            if isinstance(edge, DiagonalEdge) and isinstance(edge.crossing.tile_type, tile_type):
                return True
        return False
