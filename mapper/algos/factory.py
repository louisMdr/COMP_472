from mapper.core.map import Map
from mapper.algos.c import RoleCAlgo
from mapper.algos.p import RolePAlgo
from mapper.algos.v import RoleVAlgo
from mapper.algos.base import HeuristicAStar


class RoleAlgoFactory:

    def __init__(self, cov_map: Map):
        self.map = cov_map

    def create(self, role_char: str) -> HeuristicAStar:
        if role_char == 'C':
            return RoleCAlgo(self.map)
        elif role_char == 'P':
            return RolePAlgo(self.map)
        elif role_char == 'V':
            # TODO import and instantiate Role V specific algo
            return RoleVAlgo(self.map)
        else:
            raise RuntimeError(f'No algorithm defined for role {role_char}')
