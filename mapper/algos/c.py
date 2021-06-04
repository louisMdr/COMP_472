from typing import Dict

from mapper.core.map import Map
from mapper.core.node import Node
from mapper.core.edge import Edge, DiagonalEdge
from mapper.core.tile import Tile, Quarantine, Vaccine, PlayGround
from mapper.core.pqueue import PriorityQueue
from mapper.algos.base import HeuristicAStar, InfoContainer


class RoleCAlgo(HeuristicAStar):
    """

    Implement A* heuristic search for Role C

    H(N) = avg edge cost - 2 + (moves in x direction + moves in y direction to closest goal node)

    """
    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()

    def accepted_tile_type(self):
        return Quarantine

    def __update_start(self):
        # make sure to always start on the top right if the start point is inside a tile somewhere
        if isinstance(self.start_node.col_idx, float) and isinstance(self.start_node.row_idx, float):
            new_row_idx = int(self.start_node.row_idx)
            new_col_idx = int(self.start_node.col_idx) + 1
            self.start_node = self.map.get_node(new_row_idx, new_col_idx)

    def __create_d_map(self):
        """ creates distance to goal for each node """
        goal_map = {}
        # collect all goal nodes
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                if node.borders_tile_of_type(Quarantine):
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
        self.__create_d_map()
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        closed_list = []
        while not self.queue.empty():
            node_info = self.queue.dequeue()
            # add the node to the path, to keep track of all nodes visited along the path
            node_info.path.append(node_info.node)
            # add the node to the closed list, so that we avoid cycles
            closed_list.append(node_info.node.get_name())
            if node_info.node.borders_tile_of_type(Quarantine):
                # role C wants to get to a Quarantine tile
                # if the node is located on the corner of a tile that is of a goal type
                # then the search was a success
                success_info = node_info
                break

            for edge in node_info.node.edges:
                other_node = edge.get_other_node(node_info.node)
                if (
                    # prevent cycle
                    other_node.get_name() in closed_list or
                    # role C can't go down diagonal edges
                    isinstance(edge, DiagonalEdge) or
                    # role C can't go down straight edges that have playgrounds on both sides
                    (
                        (edge.tile_one is not None and isinstance(edge.tile_one.tile_type, PlayGround)) and
                        (edge.tile_two is not None and isinstance(edge.tile_two.tile_type, PlayGround))
                    )
                ):
                    # disregard edge that matches one of these invalid conditions
                    continue
                # calculate f(n)
                priority = self.__calculate_f(other_node, edge, node_info.cost)
                # add the other node along this path to the priority queue
                self.queue.queue(
                    priority,
                    InfoContainer(other_node, node_info.path + [edge], node_info.cost + self.__edge_cost(edge))
                )
        # all paths exhausted
        if success_info is None:
            print('\n NO PATH FOUND')
        else:
            # success, print the path and the cost
            nodes = [node.get_name() for node in success_info.path if isinstance(node, Node)]
            print(f'\n PATH FOUND:\n   Path: {" --> ".join(nodes)}\n   Cost: {success_info.cost}')

    def __calculate_f(self, node: Node, edge: Edge, current_cost: float) -> float:
        g_n = current_cost + self.__edge_cost(edge)
        h_n = self.__calculate_h(node)
        # f(n) = g(n) + h(n)
        return g_n + h_n

    def __edge_cost(self, edge: Edge) -> float:
        # cost of edge depends on tiles, and if it's diagonal or not
        if isinstance(edge, DiagonalEdge):
            return self.__tile_cost(edge.crossing)
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2

    def __tile_cost(self, tile: Tile) -> int:
        # edge cost defined in assignment instructions
        if isinstance(tile.tile_type, Vaccine):
            return 2
        elif isinstance(tile.tile_type, PlayGround):
            return 3
        elif isinstance(tile.tile_type, Quarantine):
            return 0
        else:
            return 1

    def __calculate_h(self, node: Node) -> float:
        # H(N) = avg edge cost - 2 + (moves in x direction + moves in y direction to closest goal node)
        avg_cost = sum([self.__edge_cost(edge) for edge in node.edges]) / len(node.edges)
        return avg_cost - 2 + self.d_map[node.get_name()]

