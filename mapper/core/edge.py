

class Edge:
    """

    Base class representing a connection between two nodes

    """
    def __init__(self, node_one, node_two):
        self.node_one = node_one
        self.node_two = node_two

    def edge_matches_node(self, node) -> bool:
        # checks if the passed node is part of this edge
        return (
            node.name == self.node_one.name or
            node.name == self.node_two.name
        )

    def edge_matches_axis_divisor(self, node, vertical_axis: bool, divisor: int) -> bool:
        # checks if the passed node is on the same axis as the desired axis
        other_node = self.node_one if self.node_one.name != node.name else self.node_two
        divided_col = int(other_node.col_idx / divisor)
        divided_row = int(other_node.row_idx / divisor)
        return (
            (
                vertical_axis and
                divided_col == node.col_idx and
                node.row_idx < other_node.row_idx / divisor < node.row_idx + 1
            ) or
            (
                not vertical_axis and
                divided_row == node.row_idx and
                node.col_idx < other_node.col_idx / divisor < node.col_idx + 1
            )
        )

    def edge_matches_axis(self, node, vertical_axis: bool) -> bool:
        # checks if the passed node is on the same axis as the desired axis
        other_node = self.node_one if self.node_one.name != node.name else self.node_two
        return (
            (vertical_axis and other_node.col_idx == node.col_idx and node.row_idx + 1 == other_node.row_idx) or
            (not vertical_axis and other_node.row_idx == node.row_idx and node.col_idx + 1 == other_node.col_idx)
        )

    def get_other_node(self, node):
        return self.node_one if node.name != self.node_one.name else self.node_two

    def get_other_node_idx(self, node) -> int:
        invalid_idx = -1
        for idx, edge in enumerate(node.edges):
            if (
                type(edge) is type(self) and
                edge.node_one.name == self.node_one.name and
                edge.node_two.name == self.node_two.name
            ):
                return idx
        return invalid_idx

    def edge_matches_both_nodes(self, node_one, node_two):
        return (
            (self.node_one.name == node_one.name and node_two.name == self.node_two.name) or
            (self.node_one.name == node_two.name and self.node_two.name == node_one.name)
        )


class DiagonalEdge(Edge):
    """

    Class representing an edge that crosses a tile diagonally

    """
    def __init__(self, node_one, node_two, tile):
        super().__init__(node_one, node_two)
        self.crossing = tile


class StraightEdge(Edge):
    """

    Class representing an edge that runs along the edge of two tiles

    """
    def __init__(self, node_one, node_two, tile_one, tile_two):
        super().__init__(node_one, node_two)
        self.tile_one = tile_one
        self.tile_two = tile_two

