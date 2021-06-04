from typing import Dict, List, Union, Tuple, Type

from mapper.core.node import Node
from mapper.core.tile import Tile, TileTypeFactory
from mapper.core.edge import Edge, DiagonalEdge, StraightEdge


class Map:
    """

    Class representing the Covid MAP

    """
    TILE_WIDTH: int = 1

    def __init__(self, num_columns: int, num_rows: int):
        self.num_columns: int = num_columns
        self.num_rows: int = num_rows
        # 2D map grid, with just the squares
        self.map_grid: List[List[Tile]] = [[Tile(i, j, num_columns) for j in range(num_columns)] for i in range(num_rows)]
        # keep track of nodes in a map for easy lookup
        self._node_lookup: Dict[str, Node] = {}
        # keep track of edges to not duplicate
        self._all_edges: List[Edge] = []
        # keep track of all endpoint things created by user
        self._user_created: List[Union[Edge, Node]] = []
        # keep track of all grid related things that get removed a user creates a point
        self._grid_storage: List[Union[Edge, Node]] = []
        # 2D map grid with just the nodes (to make it easier to connect them)
        Node.reset()
        self._node_grid: List[List[Node]] = [
            [self.__create_new_node(i, j) for j in range(num_columns + 1)]
            for i in range(num_rows + 1)
        ]
        # the graph, starting from the top-left node
        self.graph: Node = self._node_grid[0][0]
        self.counts = {
            'V': 0,
            'P': 0,
            'Q': 0,
            'U': self.num_rows * self.num_columns
        }
        # connect all the nodes
        self.__connect()

    def get_counts(self) -> Tuple[int, int, int, int]:
        return self.counts['V'], self.counts['P'], self.counts['Q'], self.counts['U']

    def valid_map_for_role(self, tile_type: Type) -> bool:
        for row in self.map_grid:
            for tile in row:
                if isinstance(tile.tile_type, tile_type):
                    return True
        return False

    def has_start(self) -> bool:
        return 'START' in self._node_lookup.keys()

    def lookup_node(self, name: str) -> Node:
        the_node = self._node_lookup.get(name)
        if the_node is None:
            raise RuntimeError(f'No node in map with name {name}')
        return the_node

    def get_node(self, row_idx: int, col_idx: int) -> Node:
        return self._node_grid[row_idx][col_idx]

    def max_x(self):
        return self.num_rows * self.TILE_WIDTH

    def max_y(self):
        return self.num_columns * self.TILE_WIDTH

    def remove_user_points(self):
        """

        Reset the graph to how it appears after the user creates in by selecting R X C
           (i.e. remove user created points)

        """
        def revert_name(node_name: str):
            """ Helper func to reduce duplication """
            existing_node = self._node_lookup.pop(node_name)
            existing_node.revert_name()
            self._node_lookup[existing_node.get_name()] = existing_node

        new_nodes = [elem for elem in self._user_created if isinstance(elem, Node)]
        if len(self._user_created) == 0:
            # user created both nodes on existing nodes
            for name in ['START', 'END']:
                revert_name(name)
        elif len(new_nodes) < 2:
            # user created on node on existing node
            key = 'START' if new_nodes[0].get_name() != 'START' else 'END'
            revert_name(key)
        # revert all things that were user created
        for elem in self._user_created:
            if isinstance(elem, Node):
                # just pop the node from the map
                self._node_lookup.pop(elem.get_name())
            else:
                # remove the edge by removing it from the edge lists of both nodes
                for node in [elem.node_one, elem.node_two]:
                    node_idx = elem.get_other_node_idx(node)
                    node.remove_edge_by_idx(node_idx)
        # revert all things that were put in storage because of user created stuff
        for elem in self._grid_storage:
            # these should only be edges, because nodes just get renamed
            # just add them back to the edge lists
            for node in [elem.node_one, elem.node_two]:
                node.add_edge(elem)
        # reset
        self._user_created = []
        self._grid_storage = []

    def add_point(self, x: float, y: float, name: str):
        """
        cases..... 
            (X, Y) is existing node
            (X, Y) is on an existing edge
            (X, Y) is inside a tile...
        """
        if self.__is_existing_point(x, y):
            self.__replace_existing_node(x, y, name)
        elif self.__is_on_edge(x, y):
            self.__add_on_edge(x, y, name)
        else:
            self.__add_to_tile(x, y, name)

    def __add_to_tile(self, x: float, y: float, name: str):
        # get all nodes
        row_idx = int(y / self.TILE_WIDTH)
        col_idx = int(x / self.TILE_WIDTH)
        top_left_node = self._node_grid[row_idx][col_idx]
        bottom_right_node = self._node_grid[row_idx + 1][col_idx + 1]
        bottom_left_node = self._node_grid[row_idx + 1][col_idx]
        top_right_node = self._node_grid[row_idx][col_idx + 1]
        tile = self.map_grid[row_idx][col_idx]
        downwards_diag, upwards_diag = None, None
        downleft_idx, downright_idx, upleft_idx, upright_idx = None, None, None, None
        # get the diagonal edges
        for i, (node_left, node_right) in enumerate([(top_left_node, bottom_right_node), (bottom_left_node, top_right_node)]):
            for j, edge in enumerate(node_left.edges):
                if edge.edge_matches_both_nodes(node_left, node_right):
                    if i == 0:
                        downwards_diag = edge
                        downleft_idx = j
                        downright_idx = edge.get_other_node_idx(node_right)
                    else:
                        upwards_diag = edge
                        upleft_idx = j
                        upright_idx = edge.get_other_node_idx(node_right)
                    self._grid_storage.append(edge)
                    break
        # remove the long diagonal edges from all tiles
        top_left_node.remove_edge_by_idx(downleft_idx)
        bottom_right_node.remove_edge_by_idx(downright_idx)
        top_right_node.remove_edge_by_idx(upright_idx)
        bottom_left_node.remove_edge_by_idx(upleft_idx)
        # create new
        new_node = Node(y, x, None, name)
        top_left_edge = DiagonalEdge(top_left_node, new_node, tile)
        bottom_left_edge = DiagonalEdge(bottom_left_node, new_node, tile)
        bottom_right_edge = DiagonalEdge(new_node, bottom_right_node, tile)
        top_right_edge = DiagonalEdge(new_node, top_right_node, tile)
        # add all new edges to new node
        new_node.add_edge(top_left_edge)
        new_node.add_edge(bottom_left_edge)
        new_node.add_edge(bottom_right_edge)
        new_node.add_edge(top_right_edge)
        # add each edge to the specific existing node
        bottom_left_node.add_edge(bottom_left_edge)
        bottom_right_node.add_edge(bottom_right_edge)
        top_left_node.add_edge(top_left_edge)
        top_right_node.add_edge(top_right_edge)
        # store the new stuff
        self._node_lookup[new_node.get_name()] = new_node
        self._user_created.extend([new_node, bottom_left_edge, bottom_right_edge, top_right_edge, top_left_edge])

    def __add_on_edge(self, x: float, y: float, name: str):
        # have to find the edge that has a node on the same axis, and is higher in idx
        row_idx = int(int(y) / self.TILE_WIDTH)
        col_idx = int(int(x) / self.TILE_WIDTH)
        if x.is_integer() and (x % self.TILE_WIDTH) == 0:
            # its on a vertical edge...
            vertical_axis = True
            x = int(x)
        else:
            # its on a horizontal edge
            vertical_axis = False
            y = int(y)
        origin_node = self._node_grid[row_idx][col_idx]
        origin_idx, edge, terminal_node, terminal_idx = None, None, None, None
        for origin_idx, existing_edge in enumerate(origin_node.edges):
            if existing_edge.edge_matches_axis(origin_node, vertical_axis):
                edge = existing_edge
                terminal_node = existing_edge.get_other_node(origin_node)
                terminal_idx = existing_edge.get_other_node_idx(terminal_node)
                break
        # have to split the edge, create a new Node, create two edges
        origin_node.remove_edge_by_idx(origin_idx)
        terminal_node.remove_edge_by_idx(terminal_idx)
        self._grid_storage.append(edge)
        new_node = Node(y, x, None, name)
        new_edge_one = StraightEdge(origin_node, new_node, edge.tile_one, edge.tile_two)
        new_edge_two = StraightEdge(new_node, terminal_node, edge.tile_one, edge.tile_two)
        new_node.add_edge(new_edge_one)
        new_node.add_edge(new_edge_two)
        origin_node.add_edge(new_edge_one)
        terminal_node.add_edge(new_edge_two)
        self._node_lookup[new_node.get_name()] = new_node
        self._user_created.extend([new_node, new_edge_one, new_edge_two])

    def __is_on_edge(self, x: float, y: float) -> bool:
        return (
            (x.is_integer() and (x % self.TILE_WIDTH) == 0) or
            (y.is_integer() and (y % self.TILE_WIDTH) == 0)
        )

    def __replace_existing_node(self, x: float, y: float, name: str):
        row_idx = int(int(y) / self.TILE_WIDTH)
        col_idx = int(int(x) / self.TILE_WIDTH)
        existing_node = self._node_grid[row_idx][col_idx]
        # have to replace ALL of its edges with the new guy
        # or simply rename it.... but have to remember it was renamed???
        #    maybe that's as simple as, if there are no user created things,
        #    then you know it was replacing an existing node
        self._node_lookup.pop(existing_node.get_name())
        existing_node.set_name(name)
        self._node_lookup[existing_node.get_name()] = existing_node

    def __is_existing_point(self, x: float, y: float) -> bool:
        return (
            (x.is_integer() and (x % self.TILE_WIDTH) == 0) and
            (y.is_integer() and (y % self.TILE_WIDTH) == 0 )
        )

    def validate_coords(self, x: float, y: float) -> bool:
        x_width = self.num_columns * self.TILE_WIDTH
        y_width = self.num_rows * self.TILE_WIDTH
        return (
            0 <= x <= x_width and
            0 <= y <= y_width
        )

    def unit_length(self) -> int:
        return self.TILE_WIDTH

    def update_tile(self, tile_index: int, tile_type: str):
        """
        Changes the tile type of the given index
        """
        row_index, col_index = self.__translate_index(tile_index)
        existing_type = self.map_grid[row_index][col_index].tile_type
        existing_type_key = 'U' if existing_type is None else existing_type.__class__.__name__[0]
        self.counts[existing_type_key] -= 1
        self.counts[tile_type.upper()] += 1
        self.map_grid[row_index][col_index].set_type(TileTypeFactory.create_type(tile_type))

    def validate_index(self, tile_index: int) -> bool:
        """
        Validates an tile is in the grid
        """
        row_index, col_index = self.__translate_index(tile_index)
        return (
            -1 < row_index < self.num_rows and
            -1 < col_index < self.num_columns
        )

    def __translate_index(self, tile_index: int) -> Tuple[int, int]:
        """
        Turns a user entered tile_index into a 2D index
        """
        row_index = int((tile_index - 1) / self.num_columns)
        col_index = (tile_index - 1) % self.num_columns
        return row_index, col_index

    def __create_new_node(self, row_idx: int, col_idx: int) -> Node:
        """
        Creates a new node, making sure to add it to the lookup map by name
        """
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
                    next_node = self._node_grid[row_idx - 1][col_idx + 1]
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
        """
        Creates an appropriate edge based on the args, also updates each nodes edges
        """
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
        # for printing awkwardly positioned user points:
        # if counter = 0 --> check along top edge, using top left node, check vertical axis
        # if counter = 3 AND MAX GRID COL --> check along right edge
        # if counter = 3 --> check left edge
        # if bottom edge, check bottom edge
        # if counter = 0 --> check if node has diagonal edge with float coords (user created point in middle of tile)

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
                    # see if there is a user-defined point along bottom edge
                    bottom_edge_label = node.get_user_point_label_on_axis(vertical_axis=False, divisor=self.TILE_WIDTH)
                    collected_strs[cur_row_idx] += self.map_grid[row_idx - 1][col_idx].to_str_display(
                        tile_size,
                        name=node_name,
                        horizontal_label=bottom_edge_label
                    )
                else:
                    # inside the grid
                    incrementer, counter = 0, 0
                    middle_label = None
                    for idx in range(tile_size):
                        cur_row_idx += incrementer
                        if counter == 0:
                            # see if there is user-defined point along top edge of tile
                            top_edge_user_label = node.get_user_point_label_on_axis(vertical_axis=False, divisor=self.TILE_WIDTH)
                            middle_label = node.get_user_point_in_tile_label(self.TILE_WIDTH)
                        else:
                            top_edge_user_label = None
                        if counter == 3:
                            # see if there is user-defined point along the left edge of the tile
                            left_edge_user_label = node.get_user_point_label_on_axis(vertical_axis=True, divisor=self.TILE_WIDTH)
                            if left_edge_user_label is not None:
                                to_sub = int(len(left_edge_user_label) / 2)
                                # make space on left to centre the label
                                collected_strs[cur_row_idx] = collected_strs[cur_row_idx][0: -to_sub]
                        else:
                            left_edge_user_label = None
                        incrementer = incrementer if incrementer != 0 else 1
                        if self.__max_grid_col(col_idx):
                            if counter == 3:
                                # see if there is a user-defined point along the right edge of the tile
                                next_node = self._node_grid[row_idx][col_idx + 1]
                                right_vertical_label = next_node.get_user_point_label_on_axis(
                                    vertical_axis=True,
                                    divisor=self.TILE_WIDTH
                                )
                            else:
                                right_vertical_label = None
                            # last tile in the row, add the | on the right side
                            collected_strs[cur_row_idx] += self.map_grid[row_idx][col_idx].to_str_display(
                                idx,
                                include_right=True,
                                name=node_name,
                                horizontal_label=top_edge_user_label,
                                left_vertical_label=left_edge_user_label,
                                right_vertical_label=right_vertical_label,
                                leftmost=col_idx == 0,
                                middle_label=middle_label
                            )
                        else:
                            # inside the grid
                            collected_strs[cur_row_idx] += self.map_grid[row_idx][col_idx].to_str_display(
                                idx,
                                name=node_name,
                                horizontal_label=top_edge_user_label,
                                left_vertical_label=left_edge_user_label,
                                leftmost=col_idx == 0,
                                middle_label=middle_label
                            )
                        counter += 1
        # finished, print
        print('\n'.join(collected_strs))

    def get_node_grid(self) -> List[List[Node]]:
        return self._node_grid
