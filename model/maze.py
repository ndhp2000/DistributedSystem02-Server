import random
from io import StringIO

from config import *


class DisjointSet:
    def __init__(self):
        self._p_ = {}
        self._n_components_ = 0

    def set_root(self, node_key):
        if not self._p_.get(node_key, None):
            self._n_components_ = self._n_components_ + 1
            self._p_[node_key] = -1

    def find_set(self, node_key):
        if self._p_[node_key] == -1:
            return node_key
        result = self.find_set(self._p_[node_key])
        self._p_[node_key] = result
        return result

    def union(self, node_key_u, node_key_v):
        if abs(self._p_[node_key_u]) > abs(self._p_[node_key_v]):
            self._p_[node_key_v] = node_key_u
        else:
            self._p_[node_key_u] = node_key_v
        self._n_components_ = self._n_components_ - 1

    def size(self):
        return self._n_components_


class Maze:
    DELTA = ((-1, 0), (1, 0), (0, -1), (0, 1))
    DIRECTION_UP = 0
    DIRECTION_DOWN = 1
    DIRECTION_LEFT = 2
    DIRECTION_RIGHT = 3
    _REVERSE_DIRECTION_ = {DIRECTION_LEFT: DIRECTION_RIGHT, DIRECTION_RIGHT: DIRECTION_LEFT,
                           DIRECTION_UP: DIRECTION_DOWN, DIRECTION_DOWN: DIRECTION_UP}
    _CYCLE_RATIO_ = 1

    def __init__(self, random_seed, width=MAP_WIDTH, height=MAP_HEIGHT):
        self._seed_ = random_seed
        self._random_ = random.Random(random_seed)
        self._width_ = width
        self._height_ = height
        self._adj_matrix_ = np.zeros((self._height_, self._width_, 4))  # HEIGHT x WIDTH x 4
        self._generate_()

    def _generate_(self):
        dsu = DisjointSet()
        for x in range(self._height_):
            for y in range(self._width_):
                dsu.set_root((x, y))
        # Create fully connected graph
        while dsu.size() > 1:
            u = (self._random_.randint(0, self._height_ - 1), self._random_.randint(0, self._width_ - 1))
            random_direction = self._random_.randint(0, 3)
            v = (u[0] + self.DELTA[random_direction][0], u[1] + self.DELTA[random_direction][1])
            if self.is_box_in_maze(u) and self.is_box_in_maze(v):
                u_root = dsu.find_set(u)
                v_root = dsu.find_set(v)
                if u_root != v_root:
                    dsu.union(u_root, v_root)
                    self._adj_matrix_[u[0], u[1], random_direction] = 1
                    self._adj_matrix_[v[0], v[1], self._REVERSE_DIRECTION_[random_direction]] = 1

        # Create some Cycle
        for i in range(int(self._height_ * self._width_ * self._CYCLE_RATIO_)):
            u = (self._random_.randint(0, self._height_ - 1), self._random_.randint(0, self._width_ - 1))
            random_direction = self._random_.randint(0, 3)
            v = (u[0] + self.DELTA[random_direction][0], u[1] + self.DELTA[random_direction][1])
            if self.is_box_in_maze(u) and self.is_box_in_maze(v):
                self._adj_matrix_[u[0], u[1], random_direction] = 1
                self._adj_matrix_[v[0], v[1], self._REVERSE_DIRECTION_[random_direction]] = 1

    def is_box_in_maze(self, p):
        return 0 <= p[0] < self._height_ and 0 <= p[1] < self._width_

    def get_width(self):
        return self._width_

    def get_height(self):
        return self._height_

    def is_connected_to_direction(self, p, direction):
        return self._adj_matrix_[p[0], p[1], direction]

    def serialize(self):
        return {
            'seed': self._seed_,
            'width': self._width_,
            'height': self._height_
        }

    def __str__(self):
        result = StringIO()
        result.write("Size : {} * {}\n".format(self._height_, self._width_))

        for x in range(self._height_):
            if x == 0:
                for y in range(self._width_):
                    if y == 0:
                        result.write('|')
                    result.write('=')
                    if y == self._width_ - 1:
                        result.write('|')
                    else:
                        result.write('=')
                result.write('\n')

            for y in range(self._width_):
                if y == 0:
                    result.write('|')
                result.write(' ')
                if not self._adj_matrix_[x][y][self.DIRECTION_RIGHT]:
                    result.write('|')
                else:
                    result.write(' ')
            result.write('\n')

            for y in range(self._width_):
                if y == 0:
                    result.write('*')
                if not self._adj_matrix_[x][y][self.DIRECTION_DOWN]:
                    result.write('=*')
                else:
                    result.write(' *')
            result.write('\n')
        return result.getvalue()
