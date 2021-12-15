from config import *
from model.base_entity import Entity
from model.utils import convert_player_direction_to_maze_direction


class Bullet(Entity):
    def __init__(self, bullets_group, bullet_id, player_id, position, direction, maze):
        super().__init__(BULLET_MAZE_RADIUS, position, BULLET_MOVING_SPEED)
        print("BULLET position: ", self._position_)
        self._group_ = bullets_group
        self._id_ = bullet_id
        self._player_id_ = player_id
        self._initial_position_ = self._position_.copy()
        self._direction_ = direction
        self._maze_ = maze
        bullets_group.add(self)

    def remove(self):
        if self._group_ is not None:
            self._group_.remove(self)
        self._is_removed_ = True

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

    def serialize(self):
        return {
            'id': self._id_,
            'position': [self._position_[0], self._position_[1]],
            'direction': self._direction_,
            'initial_position': [self._initial_position_[0], self._initial_position_[1]],
        }
