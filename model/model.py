import uuid

import numpy as np

from config import PLAYER_REWARD, BULLET_DAMAGE, MAXIMUM_PLAYERS
from model.bullet import Bullet
from model.entity_group import PlayerGroup, Group
from model.maze import Maze
from model.player import Player


class MainGameLogic:

    def __init__(self):

        self._users_counter = 0
        self._connected_instances_ = set()

        self.HANDLERS_MAP = {
            '_JOIN_GAME_': self._handle_join_game_,
            '_GAME_ACTION_': self._handle_game_action_,
            '_LOG_OUT_': self._handle_log_out_,
        }

        self._maze_ = None
        self._players_ = PlayerGroup()
        self._bullets_ = Group()
        self.flag = True

    def init_maze(self, maze_seed):
        self._maze_ = Maze(maze_seed)

    def init_players(self, players):
        for player in players:
            self._players_.add(Player(self._maze_, player['id'], self._players_, player['seed'],
                                      position=np.array(player['position']),
                                      current_direction=player['current_direction'],
                                      next_direction=player['next_direction'],
                                      bullet_cooldown=player['bullet_cooldown'], player_hp=player['hp'],
                                      bullet_counter=player['bullet_counter'], dead_counter=player['dead_counter']))

    def init_bullets(self, bullets):
        for bullet in bullets:
            self._bullets_.add(Bullet(self._bullets_, bullet['id'], bullet['player_id'], bullet['position'],
                                      bullet['direction'], self._maze_))

    def get_maze(self):
        return self._maze_

    def get_players(self):
        return self._players_

    def get_bullets(self):
        return self._bullets_

    def add_player(self, new_player):
        self._players_.add(new_player)

    def _check_collisions(self):
        players_hit = Group.groups_collide(self._players_, self._bullets_, False)
        for player in players_hit:
            for bullet in players_hit[player]:
                self._players_.reward_player(bullet.get_origin_id(), PLAYER_REWARD)
                bullet.remove()
            player.hit(BULLET_DAMAGE)

    def update(self, events):
        # Handle actions (shoot, change direction)
        for event in events:
            self._handle_event_(event)

        # Moving
        self._players_.update(None, self._bullets_)
        self._bullets_.update()

        # Check collide
        self._check_collisions()

    def serialize(self):
        result = {
            'maze': self._maze_.serialize(),
            'players': self._players_.serialize(),
            'bullets': self._bullets_.serialize(),
        }
        return result

    def _handle_event_(self, event):
        self.HANDLERS_MAP[event['type']](event)

    def _handle_join_game_(self, event):
        self.add_player(Player(self._maze_, event['user_id'], self._players_, event['seed']))

    def _handle_game_action_(self, event):
        self._players_.update(event, self._bullets_)

    def _handle_log_out_(self, event):
        self._players_.remove_by_id(event['user_id'])
        self._connected_instances_.remove(event['instance_id'])

    def get_new_user_id(self):
        result = self._users_counter
        self._users_counter += 1
        return result

    def get_new_instance_id(self):
        if len(self._connected_instances_) == MAXIMUM_PLAYERS:
            return None
        result = str(uuid.uuid4())
        self._connected_instances_.add(result)
        return result

    def check_instance_id(self, instance_id):
        return instance_id in self._connected_instances_
