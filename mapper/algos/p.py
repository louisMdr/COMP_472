from typing import Dict, Optional

from mapper.core.map import Map
from mapper.core.node import Node
from mapper.core.edge import Edge, DiagonalEdge
from mapper.core.tile import Tile, Quarantine, Vaccine, PlayGround
from mapper.core.pqueue import PriorityQueue
from mapper.algos.base import HeuristicAStar, InfoContainer


class RolePAlgo(HeuristicAStar):
    """

    Implement A* heuristic search for Role P

    H(N) = min(of all edge costs) - 1 + (moves in x direction + moves in y direction to closest goal node)
    Reasoning: we cannot do an average of the costs since one edge or more could hold an infinite cost value,
               but in order to make the heuristic informed, for each node, we still consider its best edge.
               That way, a node that connects to edges of values (1.5, 2.5, 3) will be preferred, over an edge that
               connects to edges of values (2, 2, 2.5). We then substract 1 and add  # moves (on x, y) away from goal
    """

    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()
        self.middle_label: Optional[str] = None

    def accepted_tile_type(self):
        return PlayGround

    def __create_d_map(self):
        """ creates distance to goal for each node """
        goal_map = {}
        # collect all goal nodes
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                if node.borders_tile_of_type(PlayGround):
                    goal_map[node.get_name()] = (i, j)
        # calculate distance to closest goal node for each node
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                distances = [
                    abs(i - y) + abs(j - x)
                    for node_name, (y, x) in goal_map.items()
                ]
                self.d_map[node.get_name()] = min(distances)

    def search(self):
        """

        Performs the search

        """
        def search_helper():
            """

            Inner function so that the first node can populate the queue twice,
                first with paths that are diagonal:

                ^                   ^
                |                   |
                 ------ START ------
                |                   |
                v                   v

                second with paths that are horizontal:

                  <------- ------->
                          |
                        START
                          |
                  <------- ------->

            The non-START nodes just do it regularly (once)

            """
            for edge in node_info.node.edges:
                other_node = edge.get_other_node(node_info.node)
                if (
                    other_node.get_name() in closed_list or
                    # role P can't go down diagonal edges (except if its the first node and the node is inside a tile)
                    (
                        isinstance(edge, DiagonalEdge) and
                        not self.__is_first_and_inside(node_info.node, node_info.cost)
                    )
                ):
                    continue
                if node_info.node.get_name() == 'START':
                    priority = self.__calculate_f(other_node, edge, node_info.cost, current_node=node_info.node, vertical=vertical)
                else:
                    priority = self.__calculate_f(other_node, edge, node_info.cost)
                # infinite edges should not be explored
                if abs(priority) == float('inf'):
                    msg = "WARNING: infinite cost detected on {} {}--> {}".format(
                        node_info.node.get_name(),
                        '' if node_info.cost > 0 or self.middle_label is None else f'--> {self.__extra_label_str()} ',
                        other_node.get_name()
                    )
                    print(msg)
                    continue
                cur_cost = self.__edge_cost(edge, node_info.cost, node_info.node, vertical)
                add_next = [edge] if node_info.cost > 0 or self.middle_label is None else [self.__extra_label_str(), edge]
                self.queue.queue(
                    priority,
                    InfoContainer(other_node, node_info.path + add_next, node_info.cost + cur_cost)
                )

        self.__create_d_map()
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        closed_list = []
        while not self.queue.empty():
            node_info = self.queue.dequeue()
            node_info.path.append(node_info.node)
            closed_list.append(node_info.node.get_name())
            if node_info.node.borders_tile_of_type(PlayGround):
                success_info = node_info
                break

            if node_info.node.get_name() == 'START' and self.__is_first_and_inside(node_info.node, node_info.cost):
                # start node that is inside a tile goes twice
                for vertical in [True, False]:
                    search_helper()
            else:
                # regular nodes go once (including start node not inside the tile)
                vertical = False
                search_helper()

        if success_info is None:
            print('\n NO PATH FOUND')
        else:
            nodes = [
                (node.get_name() if isinstance(node, Node) else node)
                for node in success_info.path if isinstance(node, Node) or isinstance(node, str)
            ]
            print(f'\n PATH FOUND:\n   Path: {" --> ".join(nodes)}\n   Cost: {success_info.cost}')

    def __extra_label_str(self) -> Optional[str]:
        label = self.middle_label
        self.middle_label = None
        return label

    def __calculate_f(self, node: Node, edge: Edge, current_cost: float, current_node: Node = None, vertical: bool = False) -> float:
        if current_node is None:
            g_n = current_cost + self.__edge_cost(edge, current_cost, node, vertical)
        else:
            g_n = current_cost + self.__edge_cost(edge, current_cost, current_node, vertical)
        h_n = self.__calculate_h(node, current_cost, vertical)
        return g_n + h_n

    def __cost_of_node_in_tile(self, middle_node: Node, edge: Edge, vertical: bool) -> float:
        target_node = edge.get_other_node(middle_node)
        # have to determine if this was left or right, up or down
        x_axis = "right" if middle_node.col_idx < target_node.col_idx else "left"
        # y-axis is inverted
        y_axis = "down" if middle_node.row_idx < target_node.row_idx else "up"
        # have to get straight edge
        target_vertical = target_node.get_other_node_on_axis(y_axis == 'down', vertical, x_axis == 'right')
        self.middle_label = f'{x_axis} --> {y_axis}' if vertical else f'{y_axis} --> {x_axis}'
        # cost of walking inside tile + cost of walking along vertical edge
        return self.__tile_cost(edge.crossing) + self.__edge_cost(target_vertical, 0, target_node, vertical)

    def __node_is_in_tile(self, node: Node) -> bool:
        return isinstance(node.col_idx, float) and isinstance(node.row_idx, float)

    def __is_first_and_inside(self, node: Node, cost: float) -> bool:
        return (
            (
                (isinstance(cost, int) and cost == 0) or
                (isinstance(cost, float) and cost.is_integer() and int(cost) == 0)
            ) and
            self.__node_is_in_tile(node)
        )

    def __edge_cost(self, edge: Edge, cost: float, node: Node, vertical: bool) -> float:
        if self.__is_first_and_inside(node, cost):
            # have to do something special to calculate first cost
            # if the start value is inside
            return self.__cost_of_node_in_tile(node, edge, vertical)
        # cost of edge depends on tiles, and if it's diagonal or not
        elif isinstance(edge, DiagonalEdge):
            return self.__tile_cost(edge.crossing)
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2

    def __tile_cost(self, tile: Tile) -> float:
        if isinstance(tile.tile_type, Vaccine):
            return 2
        elif isinstance(tile.tile_type, PlayGround):
            return 0
        elif isinstance(tile.tile_type, Quarantine):
            return float('inf')
        else:
            return 1

    def __calculate_h(self, node: Node, current_cost: float, vertical: bool) -> float:
        min_cost = min([self.__edge_cost(edge, current_cost, node, vertical) for edge in node.edges])
        return min_cost - 1 + self.d_map[node.get_name()]

