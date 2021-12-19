from config import *
from model.base_entity import Entity
from model.utils import convert_player_direction_to_maze_direction


class Bullet(Entity):
    def __init__(self, bullets_group, bullet_id, player_id, position, direction, maze):
        super().__init__(tuple(bullet_id), BULLET_MAZE_RADIUS, position, BULLET_MOVING_SPEED, bullets_group)
        self._group_ = bullets_group
        self._player_id_ = player_id
        self._direction_ = direction
        self._maze_ = maze
        self._future_position_ = None
        self.synchronize()
        bullets_group.add(self)

    def _meet_middle_box(self):
        return int(self._position_[0]) == self._position_[0] and self._position_[1] == int(self._position_[1])

    def _is_valid_direction(self, player_direction):
        maze_direction = convert_player_direction_to_maze_direction(player_direction)
        return self._maze_.is_connected_to_direction((int(self._position_[1]), int(self._position_[0])), maze_direction)

    def _move(self):
        if not self._meet_middle_box() or self._is_valid_direction(self._direction_):
            self._position_ += DIRECTIONS[self._direction_] * self._speed_
        else:
            self.remove()

    def update(self):
        self._move()

    def get_origin_id(self):
        return self._player_id_

    def synchronize(self):
        self._future_position_ = self._position_.copy()
        if not self._meet_middle_box() or self._is_valid_direction(self._direction_):
            self._future_position_ += DIRECTIONS[self._direction_] * self._speed_

    def get_future_position(self):
        return self._future_position_.copy()

    def serialize(self):
        return {
            'id': self._id_,
            'position': [self._position_[0], self._position_[1]],
            'direction': self._direction_,
            'player_id': self._player_id_
        }

    def __lt__(self, other):
        return tuple(self.get_id()) < tuple(other.get_id())
