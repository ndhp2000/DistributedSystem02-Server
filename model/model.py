from random import Random

import numpy as np

from config import PLAYER_REWARD, BULLET_DAMAGE, PLAYER
from model.entity_group import PlayerGroup, Group
from model.maze import Maze
from model.player import Player, Bot


class MainGameLogic:
    def __init__(self, seed):
        self.HANDLERS_MAP = {
            '_JOIN_GAME_': self._handle_join_game_,
            '_GAME_ACTION_': self._handle_game_action_,
            '_LOG_OUT_': self._handle_log_out_,
        }

        self._maze_ = None
        self._players_ = PlayerGroup()
        self._bullets_ = Group()
        self._seed_ = seed
        self._random_ = Random(seed)
        self.flag = True

    def init_maze(self, maze_seed):
        self._maze_ = Maze(maze_seed)

    def init_players(self):
        new_position = np.array((self._random_.randint(0, self._maze_.get_width() - 1),
                                 self._random_.randint(0, self._maze_.get_height() - 1)), dtype='float64')
        self.add_player(
            Player(new_position, self._maze_, 18120143, self._players_, 123))

        self.add_player(
            Bot(new_position, self._maze_, 19201412, self._players_, 456))

    def init_bullets(self):
        pass

    def get_maze(self):
        return self._maze_

    def get_players(self):
        return self._players_

    def get_bullets(self):
        return self._bullets_

    def add_player(self, new_player):
        self._players_.add(new_player)

    def update(self, events):
        # Handle actions (shoot, change direction)
        for event in events:
            self._handle_event_(event)

        # Moving
        self._players_.update(None, self._bullets_)
        self._bullets_.update()

        # Check collide
        self._check_collisions()

    def _check_collisions(self):
        players_hit = Group.groups_collide(self._players_, self._bullets_, False)
        for player in players_hit:
            for bullet in players_hit[player]:
                self._players_.reward_player(bullet.get_origin_id(), PLAYER_REWARD)
                bullet.remove()
            player.hit(BULLET_DAMAGE)

    def serialize(self):
        result = {
            'maze': self._maze_.serialize(),
            'players': self._players_.serialize(),
            'bullets': self._bullets_.serialize(),
            'seed': self._seed_
        }
        return result

    def _handle_event_(self, event):
        self.HANDLERS_MAP[event['type']](event)

    def _handle_join_game_(self, event):
        while True:
            new_position = np.array((self._random_.randint(0, self._maze_.get_width() - 1),
                                     self._random_.randint(0, self._maze_.get_height() - 1)), dtype='float64')
            if not self._maze_.is_cell_occupied((int(new_position[1]), int(new_position[0])), event['user_id']):
                self.add_player(
                    Player(new_position, self._maze_, event['user_id'], self._players_, player_type=PLAYER))
                break

    def _handle_game_action_(self, event):
        self._players_.update(event, self._bullets_)

    def _handle_log_out_(self, event):
        pass
