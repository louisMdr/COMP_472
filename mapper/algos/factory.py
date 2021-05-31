from mapper.core.map import Map
from mapper.algos.c import RoleCAlgo
from mapper.algos.base import HeuristicAStar


class RoleAlgoFactory:

    def __init__(self, cov_map: Map):
        self.map = cov_map

    def create(self, role_char: str) -> HeuristicAStar:
        if role_char == 'C':
            return RoleCAlgo(self.map)
        elif role_char == 'P':
            # TODO import and instantiate Role P specific algo
            return HeuristicAStar(self.map)
        elif role_char == 'V':
            # TODO import and instantiate Role V specific algo
            return HeuristicAStar(self.map)
        else:
            raise RuntimeError(f'No algorithm defined for role {role_char}')
