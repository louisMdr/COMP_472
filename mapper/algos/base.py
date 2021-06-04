from mapper.core.map import Map
from mapper.core.node import Node


class HeuristicAStar:
    def __init__(self, cov_map: Map):
        self.map: Map = cov_map
        self.start_node: Node = self.map.lookup_node('START')
        self.__update_start()

    def __update_start(self):
        # if a algo is supposed to start at a corner of a tile if it finds itself in the middle of a tile to start
        # it just needs to implement this algorithm
        pass

    def search(self):
        # each role needs to implement a different search algorithm
        ...

    def accepted_tile_type(self):
        ...


class InfoContainer:
    """ Helper data class for search """
    def __init__(self, node: Node, path_to: list, cost: int = 0):
        self.node: Node = node
        self.path: list = path_to
        self.cost: int = cost
