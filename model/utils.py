from config import UP, DOWN, LEFT, RIGHT
from model.maze import Maze


def convert_player_direction_to_maze_direction(player_direction):
    maze_direction = None
    if player_direction == UP:
        maze_direction = Maze.DIRECTION_UP
    if player_direction == DOWN:
        maze_direction = Maze.DIRECTION_DOWN
    if player_direction == LEFT:
        maze_direction = Maze.DIRECTION_LEFT
    if player_direction == RIGHT:
        maze_direction = Maze.DIRECTION_RIGHT
    return maze_direction
