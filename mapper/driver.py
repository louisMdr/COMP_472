from mapper.core.map import Map
from mapper.core.tile import TileTypeFactory
from mapper.algos.base import HeuristicAStar
from mapper.algos.factory import RoleAlgoFactory


class Driver:

    def __init__(self):
        self.require_break: bool = False
        self.role_factory: RoleAlgoFactory = None
        self.map: Map = None
        self.role: HeuristicAStar = None
        self.__create_map(True)

    def __create_map(self, first_prompt: bool = False):
        if first_prompt:
            print('\n Please create a map:\n')
        else:
            print(' Creating a map...')
        num_rows, num_cols = None, None
        while num_rows is None:
            num_rows = input('   Enter the number of rows for the map: ')
            if num_rows.isnumeric():
                num_rows = int(num_rows)
            else:
                print('   Invalid selection!')
                num_rows = None
        while num_cols is None:
            num_cols = input('   Enter the number of columns for the map: ')
            if num_cols.isnumeric():
                num_cols = int(num_cols)
            else:
                print('   Invalid selection!')
                num_cols = None
        print(f'\n Creating map of {num_rows} X {num_cols}...')
        self.map = Map(num_columns=num_cols, num_rows=num_rows)
        print('\n Finished, the empty map looks like: \n\n')
        self.map.str_display()
        self.role_factory = RoleAlgoFactory(self.map)
        self.role = None

    def __print_types(self):
        v, p, q, u = self.map.get_counts()
        print(' Tile types are:    (Current count)')
        print(f'   U - Unassign        {u}')
        print(f'   Q - Quarantine      {q}')
        print(f'   P - PlayGround      {p}')
        print(f'   V - Vaccine         {v}\n')

    def __main_menu(self) -> int:
        print(' Main menu:')
        print('   1 - New map')
        print('   2 - Edit tiles')
        print('   3 - Choose role')
        print('   4 - Run search')
        print('   5 - Set START/END')
        print('   6 - Remove user points')
        print('   7 - Quit\n')
        
        while True:
            choice = input(' Your choice: ')
            if choice.isnumeric() and 0 < int(choice) < 8:
                return int(choice)
            else:
                print(' Invalid choice!')

    def __fill_spots(self):
        print('\n\n\n Begin filling the spots')
        self.require_break = False
        while True:
            tile_choice = None
            self.__print_types()
            while True:
                tile_num = None
                tile_num_str = input(' Enter a tile number to update its type (or ##): ')
                if tile_num_str == '##':
                    self.require_break = True
                    break
                tile_num = tile_num_str
                if tile_num.isnumeric():
                    tile_num = int(tile_num)
                    if self.map.validate_index(tile_num):
                        print(f' Tile {tile_num} selected')
                        break
                else:
                    print(' Invalid tile selection, try again')
            while True and not self.require_break:
                tile_choice = input(' Enter a tile type (or ##): ')
                if tile_choice == '##':
                    self.require_break = True
                    break
                if TileTypeFactory.validate(tile_choice):
                    print(f' Type {tile_choice} chosen')
                    break
                else:
                    print('Invalid choice, try again')
            if tile_num is None or tile_choice is None or self.require_break:
                break
            self.map.update_tile(tile_num, tile_choice)
            print('\n\n MAP UPDATED \n\n')
            self.map.str_display()
            print('\n\n')
        self.require_break = False
    
    def __choose_role(self):
        if self.map.has_start():
            role, first = '', True
            while role.lower() not in ['c', 'v', 'p']:
                if not first:
                    print(' Please try again with C, V, or P\n')
                else:
                    first = False
                role = input(' Enter a role: ')
                if role == '##':
                    break
            if role.lower() in ['c', 'v', 'p']:
                self.role = self.role_factory.create(role.upper())
        else:
            print(' Map must have start node!')
        
    def __run_search(self):
        if self.role is None:
            print(' Bad choice, role was not set!')
        elif not self.map.valid_map_for_role(self.role.accepted_tile_type()):
            print(f' The map is missing a tile of type {self.role.accepted_tile_type().__class__.__name__}')
        elif not self.map.has_start():
            print(' The map does not have a valid start point!')
        else:
            self.role.search()
    
    def __add_points(self):
        if self.map.has_start():
            self.__remove_points()
        print(
            f'\n For the purpose of entering points, assume every map tile is {self.map.unit_length()} x {self.map.unit_length()} units')
        print(' Additionally, note that the grid coordinates are inverted:')
        print('     - (0,0) is top left')
        print(f'     - ({self.map.max_x()},{self.map.max_y()}) is bottom right')
        print(' Please enter beginning and end points\n')
        self.require_break = False
        point_counter = 0
        while point_counter < 2 and not self.require_break:
            point = 'START' if point_counter == 0 else 'END'
            x, y = None, None
            while x is None and not self.require_break:
                x = input(f' Enter x-coord for {point} point: ')
                if x.replace('.', '', 1).isnumeric():
                    x = float(x)
                else:
                    if x == '##':
                        self.require_break = True
                    else:
                        print(f' x-coord {x} is invalid!')
                    x = None
            while y is None and not self.require_break:
                y = input(f' Enter y-coord for {point} point: ')
                if y.replace('.', '', 1).isnumeric():
                    y = float(y)
                else:
                    if y == '##':
                        self.require_break = True
                    else:
                        print(f' y-coord {y} is invalid!')
                    y = None

            if not self.require_break and x is not None and y is not None and self.map.validate_coords(x, y):
                point_counter += 1
                print(f' Added {point} point at ({x}, {y})\n')
                self.map.add_point(x, y, point)
            elif not self.require_break:
                print(' Invalid point, try again\n')
        if not self.require_break:
            self.map.str_display()
        self.require_break = False
    
    def __remove_points(self):
        print('Removing user points from map....\n\n')
        self.map.remove_user_points()
        self.map.str_display()

    def run(self):
        while True:
            choice = self.__main_menu()
            if choice == 7:
                break
            elif choice == 1:
                self.__create_map()
            elif choice == 2:
                self.__fill_spots()
            elif choice == 3:
                self.__choose_role()
            elif choice == 4:
                self.__run_search()
            elif choice == 5:
                self.__add_points()
            elif choice == 6:
                self.__remove_points()
            else:
                print('Invalid choice')
            

def main():

    print('\n Welcome to the COVID Mapper')
    print('\n Enter ## to break out of a loop at any time')
    driver = Driver()
    driver.run()


if __name__ == '__main__':
    main()