import numpy as np

LOGGER = [("game-debug", "./logs"), ("game-view", "./logs"), ("game-controller", "./logs"),
          ("game-model", "./logs"),
          ("game-socket", "./logs")]

PROCESSED_EVENTS_PER_LOOPS = 1000
FRAME_RATE = 45
FRAME_RATE_MS = int(1000 / FRAME_RATE)
MAX_PING = 8  # frames

MAP_WIDTH = 32
MAP_HEIGHT = 16
WIN_WIDTH = 1024
WIN_HEIGHT = 768
NAME_TAG_FONT_SIZE = 32
CONSOLE_FONT_SIZE = 18

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1234

MAXIMUM_PLAYERS = 20
PLAYER = "human"
MACHINE = "machine"
ENEMY = "enemy"

PLAYER_HP = 10
PLAYER_MOVING_SPEED = 1 / 16  # box per frame
PLAYER_MAZE_RADIUS = 1 / 2  # box
PLAYER_REWARD = 11

BULLET_MOVING_SPEED = 4 * PLAYER_MOVING_SPEED
BULLET_MAZE_RADIUS = 1 / 16  # box
BULLET_DAMAGE = 5
BULLET_COST = 1
COOLDOWN_RANGE = 4

N_TYPE_COMMANDS = 5
UP = 1
DOWN = -1
LEFT = 2
RIGHT = -2
SHOOT = 3

DIRECTIONS = {
    UP: np.array([0, -1]),
    DOWN: np.array([0, 1]),
    LEFT: np.array([-1, 0]),
    RIGHT: np.array([1, 0])
}

EVENT_TYPE = {
    'PLAYER_MOVEMENT': 0,
    'PLAYER_SHOOT': 1
}

PLAYER_MOVEMENT = {
    UP: UP,
    DOWN: DOWN,
    LEFT: LEFT,
    RIGHT: RIGHT
}

PLAYER_SHOOT = {
    SHOOT: SHOOT
}

MAZE_SCREEN_RATIO = (2 / 3, 1)
DAMAGE = 5
