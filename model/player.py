import random
from datetime import datetime

from config import *
from model.base_entity import Entity
from model.bullet import Bullet
from model.maze import Maze
from model.utils import convert_player_direction_to_maze_direction


class Player(Entity):
    def __init__(self, maze: Maze, player_id, players_group, seed, position=None, current_direction=None,
                 next_direction=None, bullet_cooldown=0, player_hp=PLAYER_HP, bullet_counter=0, dead_counter=0):
        super().__init__(player_id, PLAYER_MAZE_RADIUS, position, PLAYER_MOVING_SPEED, players_group)
        self._maze_ = maze
        self._hp_ = player_hp
        self._bullet_cooldown_ = bullet_cooldown
        self._seed_ = seed
        self._random_ = random.Random(seed)
        self._current_direction_ = current_direction
        self._next_direction_ = next_direction
        self._bullet_counter_ = bullet_counter
        self._dead_counter_ = dead_counter
        for i in range(self._dead_counter_):  # Refresh the random seed
            x = self._random_.randint(0, MAP_WIDTH - 1)
            y = self._random_.randint(0, MAP_HEIGHT - 1)

        if self._position_ is None:
            self._rand_position_and_direction()
            self._next_direction_ = None
        self._future_position_ = None

        self.synchronize()

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

    def _check_collide_with_other_players(self, guess_future=True):
        result = False
        for other_player in self._group_:
            if other_player.get_id != self._id_:
                if Entity.collide(self, other_player, guess_future):
                    result = True
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

    def synchronize(self):
        self._future_position_ = self._position_.copy()
        if not self._meet_middle_box() or self._is_valid_direction(self._current_direction_):
            self._future_position_ += DIRECTIONS[self._current_direction_] * self._speed_

    def get_future_position(self):
        return self._future_position_.copy()

    def get_origin_id(self):
        return self._id_

    def get_hp(self):
        return self._hp_

    def get_current_direction(self):
        return self._current_direction_

    def _shoot_(self, bullets_group):
        if self._bullet_cooldown_ == 0:
            Bullet(bullets_group, (self._id_, self._bullet_counter_), self._id_, np.around(self._position_),
                   self._current_direction_,
                   self._maze_)
            self._bullet_counter_ += 1
            self._bullet_cooldown_ = 4 / BULLET_MOVING_SPEED
        self._hp_ -= BULLET_COST

    def hit(self, damage):
        self._hp_ -= damage
        self._rand_position_and_direction()

    def _rand_position_and_direction(self):
        self._dead_counter_ += 1
        self._next_direction_ = None
        while True:
            x = self._random_.randint(0, MAP_WIDTH - 1)
            y = self._random_.randint(0, MAP_HEIGHT - 1)
            self._position_ = np.array((x, y), dtype='float64')
            if not self._check_collide_with_other_players(guess_future=False):
                for direction in sorted(DIRECTIONS.keys()):
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
            'seed': self._seed_,
            'bullet_cooldown': self._bullet_cooldown_,
            'bullet_counter': self._bullet_counter_,
            'dead_counter': self._dead_counter_
        }

    @staticmethod
    def get_player_type():
        return 'human'

    def __lt__(self, other):
        return self.get_id() < other.get_id()
