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
           ==> see below for the reasoning
    """

    # This is the constructor of role P.
    # Role P algorithm will make use of the PQ, distance_map, and (possibly) the middle node of the tile.
    # Role P also inherits the start node (from base.py)
    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()
        self.middle_label: Optional[str] = None

    # goal-state of role P is the closest Playground (in terms of cost)
    def accepted_tile_type(self):
        return PlayGround

    # This function maps the distance between a node and its closest goal node.
    # A goal node is a node that connects to one of the 4 edges of a Playground tile.
    # The function enters this information as a k:v pair in a dictionary, where
    # key is the current node name, and value is the (x,y) coordinates of that closest goal node.
    def __create_d_map(self):
        """ creates distance to goal for each node """
        goal_map = {}
        # First we collect all the goal nodes on the map and store them in a goal_map
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                if node.borders_tile_of_type(PlayGround):
                    goal_map[node.get_name()] = (i, j)
        # Then for every node, we calculate the distance from the current node, to
        # each of those goal nodes in goal_map. Whichever node from goal_map has the
        # least distance (ie: min(distances)), is the closest goal node from curr node
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                distances = [
                    abs(i - y) + abs(j - x)
                    for node_name, (y, x) in goal_map.items()
                ]
                self.d_map[node.get_name()] = min(distances)

    # This is the function for the A*-search algorithm
    # It calls an inner function (search_helper) recursively, which continuously adds nodes
    # to the priority queue, and traverses the search path, until it finds a node that sits on
    # one end of an edge that borders a tile of type Playground.
    def search(self):
        """

        Performs the search

        """
        # This function populates the queue with the adjacent nodes of the current node
        # We made it an inner function of search because search(self) will call it recursively
        # and check on the variables coming from search_helper to update the path and the costs,
        # until it finds a goal state (a node that belongs to a Playground tile)
        def search_helper():
            """

            Inner function so that the first node can populate the queue twice,
                first with paths that are vertical:

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
            # For every edge connected to the current node...
            for edge in node_info.node.edges:
                # if the node on the other side of the edge is a node that's already been visited
                # (ie: in our closed list)... then we ignore that edge (and therefore that node) (see: 'continue')
                other_node = edge.get_other_node(node_info.node)
                if (
                    other_node.get_name() in closed_list or
                    # similarly, since role P can't go down diagonal edges, if the node is on the other side of a
                    # diagonal edge (from the current node), we also ignore that edge, and that node (ie: 'continue')
                    (
                        isinstance(edge, DiagonalEdge) and
                        not self.__is_first_and_inside(node_info.node, node_info.cost)
                    )
                ):
                    continue
                # otherwise we calculate the f(n) of the node (ie: calculate_f) sitting on the other side of the edge
                # (recall: we are currently looping through each edges connected to our current node)
                if node_info.node.get_name() == 'START':
                    priority = self.__calculate_f(other_node, edge, node_info.cost, current_node=node_info.node, vertical=vertical)
                else:
                    priority = self.__calculate_f(other_node, edge, node_info.cost)

                # However if it turns out that that the adjacent node is on the other side of an edge with an
                # edge cost of infinite value, then we should ignore that node ('continue') and leave a message
                # "infinite edge-cost encountered"
                if abs(priority) == float('inf'):
                    msg = "WARNING: infinite cost detected on {} {}--> {}".format(
                        node_info.node.get_name(),
                        '' if node_info.cost > 0 or self.middle_label is None else f'--> {self.__extra_label_str()} ',
                        other_node.get_name()
                    )
                    print(msg)
                    continue
                # otherwise, if all is good (the node on the other side is not in the visited list and is not sitting on
                # the other side of a diagonal edge or an edge with an infinite edge-cost value), then we add that node
                # to our priority queue... along with the current_node information (ie: current path so far,
                # current cost of the path so far...) as this information will allow us to retrace the solution path
                # (and its cost) easily later.
                cur_cost = self.__edge_cost(edge, node_info.cost, node_info.node, vertical)
                add_next = [edge] if node_info.cost > 0 or self.middle_label is None else [self.__extra_label_str(), edge]
                self.queue.queue(
                    priority,
                    InfoContainer(other_node, node_info.path + add_next, node_info.cost + cur_cost)
                )
        # /end of helper_function
        # we then create a map of distances; from curr node to closest goal node
        self.__create_d_map()
        # and we now start the process of the A*-algorithm...
        # by first appending the queue with our start_node and creating our closed list
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        closed_list = []
        # So then... while PQ is not empty...
        while not self.queue.empty():
            # we dequeue the node with the lowest f(n), from the PQ
            node_info = self.queue.dequeue()
            # append its info to the search path
            node_info.path.append(node_info.node)
            # and append it to our closed list
            closed_list.append(node_info.node.get_name())
            # if the dequeued node is not a node that borders a tile of type Playground then we recursively call our
            # inner function (which job is to add the adjacent nodes of the current node to the PQ)
            # However, if the dequeued node is a node that borders a tile of type Playgrounds, then we found
            # our goal-state and we break out of the "while PQ not empty" loop
            if node_info.node.borders_tile_of_type(PlayGround):   # see node.py (last function at the bottom)
                success_info = node_info
                break
            # if the dequeued node is the first node, and it's within a tile, then we need to add it twice to the queue
            # because we must pick the right adjacent node on its vertical axis (ie: vertical = true) and also
            # the right adjacent node on its horizontal axis (ie: vertical = false), to make sure that we end up
            # going to the right node, which sits on one of the corners of the tile that we are in
            if node_info.node.get_name() == 'START' and self.__is_first_and_inside(node_info.node, node_info.cost):
                # start node that is inside a tile goes twice (one time vertical axis, one time horizontal axis)
                for vertical in [True, False]:
                    search_helper()
            # but for all other nodes (not 'first_and_inside'), they'll be appended to the queue once
            else:
                vertical = False
                search_helper()
        # if we end up emptying the queue with no goal-state (a node bordering a playground tile) encountered,
        # we return 'path not found'
        if success_info is None:
            print('\n NO PATH FOUND')
        # or if we broke out of the loop and found our goal-state node, then we display the path found and the cost,
        # which is the accumulated cost of the last node (success_node). Recall: the dequeued node always holds the
        # information regarding the path itself that led to this node (which a compilation of its predecessor nodes),
        # and the cost of that path. So in the end we just have to display the last node's ('success_node') path & cost
        else:
            nodes = [
                (node.get_name() if isinstance(node, Node) else node)
                for node in success_info.path if isinstance(node, Node) or isinstance(node, str)
            ]
            print(f'\n PATH FOUND:\n   Path: {" --> ".join(nodes)}\n   Cost: {success_info.cost}')

    # if the start node is inside a tile, we label it as such
    def __extra_label_str(self) -> Optional[str]:
        label = self.middle_label
        self.middle_label = None
        return label

    # this function calculates the f(n) of a node, by adding:
    # the g(n) of a node, which is the previous node's cost (last registered 'current_cost')
    # to the h(n) of the node (defined below)
    def __calculate_f(self, node: Node, edge: Edge, current_cost: float, current_node: Node = None, vertical: bool = False) -> float:
        if current_node is None:
            g_n = current_cost + self.__edge_cost(edge, current_cost, node, vertical)
        else:
            g_n = current_cost + self.__edge_cost(edge, current_cost, current_node, vertical)
        h_n = self.__calculate_h(node, current_cost, vertical)
        return g_n + h_n

    # if we start inside a tile, we must calculate the cost to reach one of the nodes at the corners of the tile
    # we also have to display 'left', 'right', 'down', 'up', depending on which directions we take to reach
    # that node in the corner (ie: node with the lowest f(n))...
    def __cost_of_node_in_tile(self, middle_node: Node, edge: Edge, vertical: bool) -> float:
        target_node = edge.get_other_node(middle_node)
        # have to determine if this was left or right, up or down (note: y-axis is inverted; y>=0):
        x_axis = "right" if middle_node.col_idx < target_node.col_idx else "left"
        y_axis = "down" if middle_node.row_idx < target_node.row_idx else "up"
        # getting to the straight (vertical) edge
        target_vertical = target_node.get_other_node_on_axis(y_axis == 'down', vertical, x_axis == 'right')
        self.middle_label = f'{x_axis} --> {y_axis}' if vertical else f'{y_axis} --> {x_axis}'
        # cost of the inner tile moves = cost of walking inside the tile to the vertical edge
        #                                + cost of walking along the vertical edge
        return self.__tile_cost(edge.crossing) + self.__edge_cost(target_vertical, 0, target_node, vertical)

    # checking if the node is within a tile (ie: x,y coord are floats)
    def __node_is_in_tile(self, node: Node) -> bool:
        return isinstance(node.col_idx, float) and isinstance(node.row_idx, float)

    # using the previous function: checking if a 'first' node is within a tile
    def __is_first_and_inside(self, node: Node, cost: float) -> bool:
        return (
            (
                (isinstance(cost, int) and cost == 0) or
                (isinstance(cost, float) and cost.is_integer() and int(cost) == 0)
            ) and
            self.__node_is_in_tile(node)
        )

    # calculating the edge cost between 2 nodes
    def __edge_cost(self, edge: Edge, cost: float, node: Node, vertical: bool) -> float:
        # We consider the 'edge cost' of a start-node that inside a tile, as the sum of the two inner moves:
        # cost of walking inside the tile to the vertical edge + cost of walking along the vertical edge
        if self.__is_first_and_inside(node, cost):
            return self.__cost_of_node_in_tile(node, edge, vertical)
        # Otherwise, the cost of an edge depends on the tiles
        elif isinstance(edge, DiagonalEdge):
            return self.__tile_cost(edge.crossing)
        # if the edge is the side of only one tile, then the edge-cost if the value (cost) of that tile
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
        # but if the edge is the side of two tiles, then the edge-cost is the avg value of those 2 tiles
        # see the function below for finding the value of a tile (ie: tile_cost)
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2

    # for role P, tile_cost for Vaccine is 2, for Playground: 0, for Quarantine: infinite, and for unassigned: 1
    def __tile_cost(self, tile: Tile) -> float:
        if isinstance(tile.tile_type, Vaccine):
            return 2
        elif isinstance(tile.tile_type, PlayGround):
            return 0
        elif isinstance(tile.tile_type, Quarantine):
            return float('inf')
        else:
            return 1

    # calculates the best cost-estimation for a node, from its current location, to the closest goal-state.
    # h(n) = min(of all the costs related to the adjacent edges' of n)
    #        - 1 + (# moves in x direction + # moves in y direction to the closest goal node)
    # Reasoning: we cannot do an average of the edges costs (of the adjacent edges of n) because one or more of these
    #            edges may hold an infinite cost value. So, in order to remain 'informed' (and distinguish from
    #            a 'good' adjacent node and a 'bad' one), we will consider the lowest edge_cost attached to that
    #            adjacent node. So a favourable mix, is an adjacent node that connects to an edge with a low cost,
    #            AND also has few # moves left (on x and y) to reach the goal-state. That way, when choosing between
    #            an adjacent node that connects to edges of values: 1.5, 2.5, 3... and one that connects to edges of
    #            values: 2, 2, 2.5... with let's say, the same # of moves left on the x & y axis to reach the goal node,
    #            we will take the first one because at best it will go down an edge that is less cost than the latter.
    #            Note: we subtract one, because when counting the # of moves left, actually, we already counted one of
    #            them, and replaced that count by the best possible edge_cost value for that move...
    def __calculate_h(self, node: Node, current_cost: float, vertical: bool) -> float:
        min_cost = min([self.__edge_cost(edge, current_cost, node, vertical) for edge in node.edges])
        return min_cost - 1 + self.d_map[node.get_name()]

