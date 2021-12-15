from config import *


def convert_maze_to_world_pos(maze_x, maze_y):
    maze_screen_height = int(WIN_HEIGHT * MAZE_SCREEN_RATIO[0])
    maze_screen_width = int(WIN_WIDTH * MAZE_SCREEN_RATIO[1])

    cell_height = int(maze_screen_height / MAP_HEIGHT)
    cell_width = int(maze_screen_width / MAP_WIDTH)
    world_x = (maze_x * cell_height + cell_height / 2)
    world_y = (maze_y * cell_width + cell_width / 2)

    return world_x, world_y
