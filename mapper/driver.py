from mapper.core.map import Map
from mapper.core.tile import TileTypeFactory


def main():

    print('\n Welcome to the COVID Mapper')
    print('\n Please create a map:\n')
    num_rows = int(input('   Enter the number of rows for the map: '))
    num_cols = int(input('   Enter the number of columns for the map: '))
    print(f'\n Creating map of {num_rows} X {num_cols}...')
    cov_map = Map(num_columns=num_cols, num_rows=num_rows)
    print('\n Finished, the empty map looks like: \n\n')
    cov_map.str_display()
    print('\n\n\n Begin filling the spots')
    fill_spots(cov_map)


def fill_spots(cov_map: Map):
    """

    Will update tiles on the map until the user quits

    """
    print('\n Enter ## to quit filling spaces on the grid')
    print(' Tile types are:')
    print('   Q - Quarantine')
    print('   P - PlayGround')
    print('   V - Vaccine\n')
    while True:
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