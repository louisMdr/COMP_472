from typing import Dict, List, Union, Tuple

from mapper.core.node import Node
from mapper.core.tile import Tile, TileTypeFactory
from mapper.core.edge import Edge, DiagonalEdge, StraightEdge


class Map:
    """

    Class representing the Covid MAP

    """

    def __init__(self, num_columns: int, num_rows: int):
        self.num_columns: int = num_columns
        self.num_rows: int = num_rows
        # 2D map grid, with just the squares
        self.map_grid: list = [[Tile(i, j, num_columns) for j in range(num_columns)] for i in range(num_rows)]
        # keep track of nodes in a map for easy lookup
        self._node_lookup: Dict[str, Node] = {}
        # keep track of edges to not duplicate
        self._all_edges: List[Edge] = []
        # keep track of all endpoint things created by user
        self._user_created: List[Union[Edge, Node]] = []
        # 2D map grid with just the nodes (to make it easier to connect them)
        self._node_grid: list = [
            [self.__create_new_node(i, j) for j in range(num_columns + 1)]
            for i in range(num_rows + 1)
        ]
        # the graph, starting from the top-left node
        self.graph: Node = self._node_grid[0][0]
        # connect all the nodes
        self.__connect()

    def update_tile(self, tile_index: int, tile_type: str):
        """
        Changes the tile type of the given index
        """
        row_index, col_index = self.__translate_index(tile_index)
        self.map_grid[row_index][col_index].set_type(TileTypeFactory.create_type(tile_type))

    def validate_index(self, tile_index: int) -> bool:
        row_index, col_index = self.__translate_index(tile_index)
        return (
            -1 < row_index < self.num_rows and
            -1 < col_index < self.num_columns
        )

    def __translate_index(self, tile_index: int) -> Tuple[int, int]:
        row_index = int((tile_index - 1) / self.num_columns)
        col_index = (tile_index - 1) % self.num_columns
        return row_index, col_index

    def __create_new_node(self, row_idx: int, col_idx: int) -> Node:
        new_node = Node(row_idx, col_idx, self.num_columns)
        self._node_lookup[new_node.get_name()] = new_node
        return new_node

    def __connect(self):
        """
        Connects all nodes in the graph together, using the appropriate edge, with the appropriate tiles
        based on where they are in the grid
        """
        for row_idx, row in enumerate(self._node_grid):
            for col_idx, node in enumerate(row):
                if not self.__max_node_row(row_idx):
                    # connect vertical edge
                    next_node = self._node_grid[row_idx + 1][col_idx]
                    if col_idx == 0:
                        # left edge has no left tile
                        left_tile = None
                        right_tile = self.map_grid[row_idx][col_idx]
                    elif self.__max_node_col(col_idx):
                        # right edge has no right tile
                        left_tile = self.map_grid[row_idx][col_idx - 1]
                        right_tile = None
                    else:
                        left_tile = self.map_grid[row_idx][col_idx - 1]
                        right_tile = self.map_grid[row_idx][col_idx]
                    self.__create_edge(node, next_node, left_tile, right_tile, accept_none=True)

                if not self.__max_node_col(col_idx):
                    # create horizontal edge
                    next_node = self._node_grid[row_idx][col_idx + 1]
                    if row_idx == 0:
                        # top edge has no top tile
                        top_tile = None
                        bottom_tile = self.map_grid[row_idx][col_idx]
                    elif self.__max_node_row(row_idx):
                        # bottom edge has no bottom tile
                        top_tile = self.map_grid[row_idx - 1][col_idx]
                        bottom_tile = None
                    else:
                        # somewhere inside
                        top_tile = self.map_grid[row_idx][col_idx]
                        bottom_tile = self.map_grid[row_idx - 1][col_idx]
                    self.__create_edge(node, next_node, top_tile, bottom_tile, accept_none=True)

                if not self.__max_node_col(col_idx) and not self.__max_node_row(row_idx):
                    # connect diagonal down
                    # make sure this is not along right or bottom edge
                    next_node = self._node_grid[row_idx + 1][col_idx + 1]
                    crossing_tile = self.map_grid[row_idx][col_idx]
                    self.__create_edge(node, next_node, crossing_tile, accept_none=False)

                if row_idx != 0 and not self.__max_node_col(col_idx):
                    # connect diagonal up
                    # make sure this is not along top or right edge
                    next_node = self._node_grid[row_idx - 1][col_idx - 1]
                    crossing_tile = self.map_grid[row_idx - 1][col_idx]
                    self.__create_edge(node, next_node, crossing_tile, accept_none=False)

    def __max_node_col(self, col_idx: int) -> bool:
        return col_idx == self.num_columns

    def __max_node_row(self, row_idx: int) -> bool:
        return row_idx == self.num_rows

    def __max_grid_col(self, col_idx: int) -> bool:
        return col_idx == self.num_columns - 1

    def __max_grid_row(self, row_idx: int) -> bool:
        return row_idx == self.num_rows - 1

    def __create_edge(self,
                      node_one: Node,
                      node_two: Node,
                      tile_one: Tile,
                      tile_two: Tile = None,
                      accept_none: bool = True):
        if tile_two is not None or accept_none:
            # regular straight edge
            edge = StraightEdge(node_one, node_two, tile_one, tile_two)
        else:
            # diagonal edge
            edge = DiagonalEdge(node_one, node_two, tile_one)
        self._all_edges.append(edge)
        if node_one is not None:
            node_one.add_edge(edge)
        if node_two is not None:
            node_two.add_edge(edge)
        return edge

    def str_display(self):
        """
        Prints the map to console
        """
        # assume uniform grid
        tile_size = self.map_grid[0][0].display_size()
        collected_strs = ['' for _ in self.map_grid for _ in range(tile_size)]
        collected_strs.append('')
        for row_idx, row in enumerate(self._node_grid):
            for col_idx, node in enumerate(row):
                cur_row_idx = row_idx * tile_size
                # add the node names in the corner of the grid
                node_name = node.get_name()
                collected_strs[cur_row_idx] += node_name
                if self.__max_node_col(col_idx):
                    # on the right outer edge
                    continue
                if self.__max_node_row(row_idx):
                    # on the bottom edge, only need to fill in the nodes and the bottom edge
                    if self.__max_grid_col(col_idx):
                        # last tile in the row, add the | on the right side
                        collected_strs[cur_row_idx] += self.map_grid[row_idx - 1][col_idx].to_str_display(tile_size, name=node_name)
                    else:
                        # inside the grid
                        collected_strs[cur_row_idx] += self.map_grid[row_idx - 1][col_idx].to_str_display(tile_size, name=node_name)
                else:
                    # inside the grid
                    incrementer = 0
                    for idx in range(tile_size):
                        cur_row_idx += incrementer
                        incrementer = incrementer if incrementer != 0 else 1
                        if self.__max_grid_col(col_idx):
                            # last tile in the row, add the | on the right side
                            collected_strs[cur_row_idx] += self.map_grid[row_idx][col_idx].to_str_display(idx, include_right=True)
                        else:
                            # inside the grid
                            collected_strs[cur_row_idx] += self.map_grid[row_idx][col_idx].to_str_display(idx, name=node_name)
        # finished, print
        print('\n'.join(collected_strs))
