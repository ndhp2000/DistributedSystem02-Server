import random

from config import *
from model.base_entity import Entity
from model.bullet import Bullet
from model.maze import Maze
from model.utils import convert_player_direction_to_maze_direction


class Player(Entity):
    def __init__(self, position, maze: Maze, player_id, players_group, seed):
        super().__init__(PLAYER_MAZE_RADIUS, position, PLAYER_MOVING_SPEED)
        self._maze_ = maze
        self._id_ = player_id
        self._hp_ = PLAYER_HP
        self._current_direction_ = None
        self._group_ = players_group
        self._bullet_cooldown_ = 0
        self._seed_ = seed
        self._random_ = random.Random(seed)

        for direction in DIRECTIONS:
            if self._get_next_valid_cell(position, direction) is not None:
                self._current_direction_ = direction
                break
        self._next_direction_ = None

    def _meet_middle_box(self):
        return int(self._position_[0]) == self._position_[0] and self._position_[1] == int(self._position_[1])

    def _reverse_direction(self):
        self._current_direction_ = self._current_direction_ * -1

    def _is_valid_direction(self, player_direction):
        maze_direction = convert_player_direction_to_maze_direction(player_direction)
        return self._maze_.is_connected_to_direction((int(self._position_[1]), int(self._position_[0])), maze_direction)

    def _get_next_valid_cell(self, position, player_direction):
        direction = convert_player_direction_to_maze_direction(player_direction)
        if self._maze_.is_connected_to_direction((int(position[1]), int(position[0])), direction):
            return np.array([position[0] + Maze.DELTA[direction][1], position[1] + Maze.DELTA[direction][0]])
        else:
            return None

    def _check_collide_with_other_players(self):
        result = False
        for other_player in self._group_:
            if other_player.get_id != self._id_:
                predicted_position = self._position_ + 2 * DIRECTIONS[self._current_direction_] * self._speed_
                current_position = self._position_
                self._position_ = predicted_position
                if Entity.collide(self, other_player):
                    result = True
                self._position_ = current_position
                if result:
                    return result
        return result

    def _move(self):
        if (not self._meet_middle_box() or self._is_valid_direction(
                self._current_direction_)) and not self._check_collide_with_other_players():
            self._position_ += DIRECTIONS[self._current_direction_] * self._speed_  # move

        if self._next_direction_ == -self._current_direction_:  # reverse turn
            self._reverse_direction()
            self._next_direction_ = None
            return

        if self._meet_middle_box():
            if self._next_direction_ and self._is_valid_direction(self._next_direction_):  # next turn is valid
                self._current_direction_ = self._next_direction_
            self._next_direction_ = None

    def update(self, event, bullets_group):
        self._bullet_cooldown_ = max(0, self._bullet_cooldown_ - 1)
        if event:
            if event['user_id'] == self._id_:  # Run event with suitable ID.
                if event['action'] in PLAYER_MOVEMENT:
                    self._next_direction_ = event['action']
                elif event['action'] in PLAYER_SHOOT:
                    self._shoot_(bullets_group)
        else:
            self._move()

    def remove(self):
        if self._group_ is not None:
            self._group_.remove(self)
        self._is_removed_ = True

    def get_origin_id(self):
        return self._id_

    def get_id(self):
        return self._id_

    def get_hp(self):
        return self._hp_

    def _shoot_(self, bullets_group):
        if self._bullet_cooldown_ == 0:
            Bullet(bullets_group, 0, self._id_, np.around(self._position_), self._current_direction_, self._maze_)
            self._bullet_cooldown_ = 4 / BULLET_MOVING_SPEED
        self._hp_ -= BULLET_COST

    def hit(self, damage):
        self._hp_ -= damage
        self._rand_position_and_direction()

    def _rand_position_and_direction(self):
        self._next_direction_ = None

        while True:
            x = self._random_.randint(0, MAP_WIDTH - 1)
            y = self._random_.randint(0, MAP_HEIGHT - 1)
            self._position_ = np.array((x, y), dtype='float64')
            for direction in DIRECTIONS:
                if self._get_next_valid_cell(self._position_, direction) is not None:
                    self._current_direction_ = direction
                    break
            break

    def reward(self, hp):
        self._hp_ += hp

    def serialize(self):
        return {
            'id': self._id_,
            'hp': self._hp_,
            'position': [self._position_[0], self._position_[1]],
            'current_direction': self._current_direction_,
            'next_direction': self._next_direction_,
            'previous_anchor': [self._previous_anchor[0], self._previous_anchor[1]],
            'next_anchor': [self._next_anchor[0], self._next_anchor[1]],
            'recent_running_bullet_id': self._recent_running_bullet_.get_id()
        }

    def get_player_type(self):
        return 'human'


class Bot(Player):
    COOLDOWN_COMMAND = 20

    def __init__(self, position, maze: Maze, player_id, players_group, seed):
        super().__init__(position, maze, player_id, players_group, seed)
        self._counter = self.COOLDOWN_COMMAND

    def update(self, event, bullets_group):  # Upgrade later
        self._bullet_cooldown_ = max(0, self._bullet_cooldown_ - 1)
        event = self.create_command()
        if event:
            if event in PLAYER_MOVEMENT:
                self._next_direction_ = event
            elif event in PLAYER_SHOOT:
                self._shoot_(bullets_group)
        else:
            self._move()

    def create_command(self):
        self._counter -= 1
        if self._counter == 0:
            self._counter = self.COOLDOWN_COMMAND
            rand_num = random.randint(-N_TYPE_COMMANDS, N_TYPE_COMMANDS - 1)  # TODO UPDATE FOR BACKEND
            if rand_num < 0:
                return SHOOT
            else:
                return list(PLAYER_MOVEMENT.keys())[rand_num - 1]
        return None

    def get_player_type(self):
        return 'machine'
