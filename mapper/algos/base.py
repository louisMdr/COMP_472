from mapper.core.map import Map
from mapper.core.node import Node


class HeuristicAStar:
    def __init__(self, cov_map: Map):
        self.map: Map = cov_map
        self.start_node: Node = self.map.lookup_node('START')
        self.__update_start()

    def __update_start(self):
        pass

    def search(self):
        ...
