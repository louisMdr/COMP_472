from mapper.core.map import Map
from mapper.core.tile import TileTypeFactory
from mapper.algos.base import HeuristicAStar
from mapper.algos.factory import RoleAlgoFactory


def main():

    print('\n Welcome to the COVID Mapper')
    print('\n Enter ## to break out of a loop at any time')
    print_types()
    print_roles()
    cov_map = create_map()
    fill_spots(cov_map)
    add_points(cov_map)
    role_factory = RoleAlgoFactory(cov_map)
    role = input('Enter a role: ')
    algo = role_factory.create(role)
    algo.search()


def revert_map(cov_map: Map):
    print('Removing user points from map....\n\n')
    cov_map.remove_user_points()
    cov_map.str_display()


def create_map() -> Map:
    print('\n Please create a map:\n')
    num_rows = int(input('   Enter the number of rows for the map: '))
    num_cols = int(input('   Enter the number of columns for the map: '))
    print(f'\n Creating map of {num_rows} X {num_cols}...')
    cov_map = Map(num_columns=num_cols, num_rows=num_rows)
    print('\n Finished, the empty map looks like: \n\n')
    cov_map.str_display()
    return cov_map


def print_roles():
    pass


def print_types():
    print(' Tile types are:')
    print('   Q - Quarantine')
    print('   P - PlayGround')
    print('   V - Vaccine\n')


def add_points(cov_map: Map):
    print(f'\n For the purpose of entering points, assume every map tile is {cov_map.unit_length()} x {cov_map.unit_length()} units')
    print(' Additionally, note that the grid coordinates are inverted:')
    print('     - (0,0) is top left')
    print(f'     - ({cov_map.max_x()},{cov_map.max_y()}) is bottom right')
    print(' Please enter beginning and end points\n')
    point_counter = 0
    while point_counter < 2:
        point = 'START' if point_counter == 0 else 'END'
        x = float(input(f' Enter x-coord for {point} point: '))
        y = float(input(f' Enter y-coord for {point} point: '))
        if cov_map.validate_coords(x, y):
            point_counter += 1
            print(f' Added {point} point at ({x}, {y})\n')
            cov_map.add_point(x, y, point)
        else:
            print(' Invalid point, try again\n')
    cov_map.str_display()


def fill_spots(cov_map: Map):
    """

    Will update tiles on the map until the user quits

    """
    print('\n\n\n Begin filling the spots')
    while True:
        print_types()
        while True:
            tile_num = None
            tile_num_str = input(' Enter a tile number to update its type: ')
            if tile_num_str == '##':
                break
            tile_num = int(tile_num_str)
            if cov_map.validate_index(tile_num):
                print(f' Tile {tile_num} selected')
                break
            else:
                print('Invalid tile selection, try again')
        while True:
            tile_choice = input(' Enter a tile type: ')
            if tile_choice == '##':
                break
            if TileTypeFactory.validate(tile_choice):
                print(f' Type {tile_choice} chosen')
                break
            else:
                print('Invalid choice, try again')
        if tile_num is None or tile_choice is None:
            break
        cov_map.update_tile(tile_num, tile_choice)
        print('\n\n MAP UPDATED \n\n')
        cov_map.str_display()
        print('\n\n')


if __name__ == '__main__':
    main()