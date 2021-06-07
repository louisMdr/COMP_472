from math import ceil, floor
from typing import Dict

from mapper.core.map import Map
from mapper.core.node import Node
from mapper.core.edge import Edge, DiagonalEdge
from mapper.core.tile import Tile, Quarantine, Vaccine, PlayGround
from mapper.core.pqueue import PriorityQueue
from mapper.algos.base import HeuristicAStar, InfoContainer


class RoleVAlgo(HeuristicAStar):
    """

    Implement A* heuristic search for Role V

    H(N) = sqrt(moves in x direction ^ 2 + moves in y direction ^ 2 to closest goal node)

    """
    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.__update_start()
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()

    def accepted_tile_type(self):
        return Vaccine

    def __update_start(self):
        # make sure to always start on the bottom left if the start point is inside a tile somewhere
        if isinstance(self.start_node.col_idx, float) and isinstance(self.start_node.row_idx, float):
            new_row_idx = ceil(self.start_node.row_idx)
            new_col_idx = floor(self.start_node.col_idx)
            self.start_node = self.map.get_node(new_row_idx, new_col_idx)
            
    # Function that associates the distance between a node to its closest goal node.
    # The goal node is the closest node inside the Vaccine tile. These are stored in a dictionary
    def __create_d_map(self):
        """ creates distance to goal for each node """
        goal_map = {}
        # collect all goal nodes and their coordinates
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                if node.borders_tile_of_type(Vaccine):
                    goal_map[node.get_name()] = (i, j)    
        # calculate euclidian distance to closest goal node from each node
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                distances = [
                    (abs(i - y) ** 2 + abs(j - x) ** 2) ** 0.5
                    for node_name, (x, y) in goal_map.items()
                ]
                self.d_map[node.get_name()] = min(distances)

    #Search function using priority queue that pushes/pops nodes depending on when it's visited and its priority
    def search(self):
        #initialize the node to goal state dictionary
        self.__create_d_map()
        #pop the start node
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        #keep track of the visited nodes
        closed_list = []
        while not self.queue.empty():
          #examine the node with highest priority
            node_info = self.queue.dequeue()
            node_info.path.append(node_info.node)
            #add to closed list
            closed_list.append(node_info.node.get_name())
            #end if goal state reached
            if node_info.node.borders_tile_of_type(Vaccine):
                success_info = node_info
                break
            #goal state not reached
            for edge in node_info.node.edges:
                other_node = edge.get_other_node(node_info.node)
                # ignore nodes that have already been visited
                if(other_node.get_name() in closed_list):
                  continue
                #logic: in the map structure, floating point positions for start aren't removed. So previously placed start points inside the map are ignored (since bottom left is only considered)
                if other_node.get_name() == 'START' and (isinstance(other_node.row_idx, float) or isinstance(other_node.col_idx, float)):
                  continue
                #evaluate f = g + h of node
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
  
    #calculate the function f from start to goal
    def __calculate_f(self, node: Node, edge: Edge, current_cost: float) -> float:
        g_n = current_cost + self.__edge_cost(edge)
        h_n = self.__calculate_h(node)
        return g_n + h_n

    def __edge_cost(self, edge: Edge) -> float:
        if isinstance(edge, DiagonalEdge):
            #finding the list of edges without the diagonals: to get the corner edges for distance
            node_1_edges = edge.node_one.edges
            node_2_edges = edge.node_two.edges
            #loops eliminating diagonal edges
            for i in node_1_edges:
              if isinstance(i, DiagonalEdge):
                node_1_edges.remove(i)
            
            for i in node_2_edges:
              if isinstance(i, DiagonalEdge):
                node_2_edges.remove(i)
            #stores the result of each 2 diagonal costs (max(distance 1, distance 2))
            edge_lst = []

            #finding the common nodes and calculating their cost with respect to the outer edges of the diagonal
            for edge_1 in node_1_edges:
              for edge_2 in node_2_edges:
              #identifying the nodes that are present in both edges (the 2 edges responsible for the diagonal's cost)
                if edge_1.node_one.name == edge_2.node_one.name or edge_1.node_one.name == edge_2.node_two.name or edge_2.node_one.name ==  edge_1.node_two.name or edge_2.node_two.name == edge_1.node_two.name:
                  result = (self.__edge_cost(edge_1) ** 2 + self.__edge_cost(edge_2) ** 2) ** 0.5
                  edge_lst.append(result)

            return max(edge_lst)
        #cases for edges with only one neighbor
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
         #cases for edges with two neighbors
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2

    #based on rules of Role V, the cost for each type of zone
    def __tile_cost(self, tile: Tile) -> int:
        if isinstance(tile.tile_type, Vaccine):
            return 0
        elif isinstance(tile.tile_type, PlayGround):
            return 1
        elif isinstance(tile.tile_type, Quarantine):
            return 3
        else:
            return 2
    #heuristic using euclidian distance:
    #Reasoning: averaging or minimizing costs of surrounding edges may overestimate the remaining cost of the graph traversal. For this, euclidian distance will provide a admissible, consistent estimate with the best path obtained through the queue
    def __calculate_h(self, node: Node) -> float:
        return self.d_map[node.get_name()]
