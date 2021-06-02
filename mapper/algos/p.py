from typing import Dict

from mapper.core.map import Map
from mapper.core.node import Node
from mapper.core.edge import Edge, DiagonalEdge
from mapper.core.tile import Tile, Quarantine, Vaccine, PlayGround
from mapper.core.pqueue import PriorityQueue
from mapper.algos.base import HeuristicAStar


class RolePAlgo(HeuristicAStar):
    """

    Implement A* heuristic search for Role P

    """
    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()

    def __update_start(self):
        if isinstance(self.start_node.col_idx, float) and isinstance(self.start_node.row_idx, float):

            print('START node is inside a grid')
            if (self.start_node.col_idx - int(self.start_node.col_idx )) <0.5:
                horiz_move = "left"
            else:
                horiz_move = "right"
            if (self.start_node.row_idx - int(self.start_node.row_idx)) <0.5:
                vert_move = "up"
            else:
                vert_move = "down"

          #  print('\nMoving ' + horiz_move + ' to x coordinate: ' + (int(self.start_node.col_idx) + 1)
          #       + ' at a cost of: ' + )
          #  print('\nMoving ' + vert_move + ' to y coordinate: ' + int(self.start_node.row_idx))
          #       + ' at a cost of: ' + )
            new_row_idx = int(self.start_node.row_idx)
            new_col_idx = int(self.start_node.col_idx) + 1
            self.start_node = self.map.get_node(new_row_idx, new_col_idx)

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
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        closed_list = []
        while not self.queue.empty():
            node_info = self.queue.dequeue()
            node_info.path.append(node_info.node)
            closed_list.append(node_info.node.get_name())
            if node_info.node.borders_tile_of_type(Quarantine):
                success_info = node_info
                break

            for edge in node_info.node.edges:
                other_node = edge.get_other_node(node_info.node)
                if (
                    other_node.get_name() in closed_list or
                    # role P can't go down diagonal edges
                    isinstance(edge, DiagonalEdge) or
                    # role P can't go down straight edges that touch a Quarantine site on either side
                    (
                        (edge.tile_one is not None and isinstance(edge.tile_one.tile_type, Quarantine)) or
                        (edge.tile_two is not None and isinstance(edge.tile_two.tile_type, Quarantine))
                    )
                ):
                    continue
                priority = self.__calculate_f(other_node, edge, node_info.cost)
                self.queue.queue(
                    priority,
                    InfoContainer(other_node, node_info.path + [edge], node_info.cost + self.__edge_cost(edge))
                )
        if success_info is None:
            print('\n NO PATH FOUND')
        else:
            nodes = [node.get_name() for node in success_info.path if isinstance(node, Node)]
            print(f'\n PATH FOUND:\n   Path: {" --> ".join(nodes)}\n   Cost: {success_info.cost}')

    def __calculate_f(self, node: Node, edge: Edge, current_cost: float) -> float:
        g_n = current_cost + self.__edge_cost(edge)
        h_n = self.__calculate_h(node)
        return g_n + h_n

    def __edge_cost(self, edge: Edge) -> float:
        if isinstance(edge, DiagonalEdge):
            return self.__tile_cost(edge.crossing)
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2

    def __tile_cost(self, tile: Tile) -> int:
        if isinstance(tile.tile_type, Vaccine):
            return 2
        elif isinstance(tile.tile_type, PlayGround):
            return 0
        elif isinstance(tile.tile_type, Quarantine):
            return float('inf')
        else:
            return 1

    def __calculate_h(self, node: Node) -> float:
        min_cost = min([self.__edge_cost(edge) for edge in node.edges])
        if min_cost == float('inf'):
            print('No path found: Search path stuck in an infinite path cost. Terminating program.')
            exit()
        return min_cost - 1 + self.d_map[node.get_name()]


class InfoContainer:
    """ Helper data class for search """
    def __init__(self, node: Node, path_to: list, cost: int = 0):
        self.node: Node = node
        self.path: list = path_to
        self.cost: int = cost

