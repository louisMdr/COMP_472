

class Edge:
    """

    Base class representing a connection between two nodes

    """
    def __init__(self):
        pass


class DiagonalEdge(Edge):
    """

    Class representing an edge that crosses a tile diagonally

    """
    def __init__(self, node_one, node_two, tile):
        super().__init__()
        self.crossing = tile
        self.node_one = node_one
        self.node_two = node_two


class StraightEdge(Edge):
    """

    Class representing an edge that runs along the edge of two tiles

    """
    def __init__(self, node_one, node_two, tile_one, tile_two):
        super().__init__()
        self.node_one = node_one
        self.node_two = node_two
        self.tile_one = tile_one
        self.tile_two = tile_two

