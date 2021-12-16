import numpy as np


class Entity:
    def __init__(self, entity_id, maze_radius, position, speed, group):
        self._speed_ = speed
        self._id_ = entity_id
        if position is not None:
            self._position_ = position.copy()
        else:
            self._position_ = None
        self._group_ = group
        self._is_removed_ = False
        self._maze_radius_ = maze_radius

    def get_id(self):
        return self._id_

    def get_maze_radius(self):
        return self._maze_radius_

    def get_speed(self):
        return self._speed_

    def get_position(self):
        return self._position_.copy()

    def remove(self):
        if self._group_ is not None:
            self._group_.remove(self)
        self._is_removed_ = True

    def is_removed(self):
        return self._is_removed_

    @staticmethod
    def collide(entity1, entity2, guess_future=False):
        if entity1.get_origin_id() == entity2.get_origin_id():
            return False
        if entity1.is_removed() or entity2.is_removed():
            return False

        if guess_future:
            entity1_position = entity1.get_future_position()
            entity2_position = entity2.get_future_position()
        else:
            entity1_position = entity1.get_position()
            entity2_position = entity2.get_position()

        distance_between_entity = np.sum(np.abs(entity1_position - entity2_position))
        sum_radius = entity1.get_maze_radius() + entity2.get_maze_radius()

        if distance_between_entity < sum_radius:
            return True

        return False
