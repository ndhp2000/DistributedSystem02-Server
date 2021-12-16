import random
from collections import deque

import pygame
import pygame.locals

from config import PROCESSED_EVENTS_PER_LOOPS, MAX_PING, FRAME_RATE_MS, UP, DOWN, LEFT, RIGHT, SHOOT
from model.model import MainGameLogic
from network.network import ServerNetwork
from view.view import MainGameView


class Controller:
    def __init__(self):

        self.HANDLERS_MAP = {
            '_JOIN_GAME_': self._handle_join_game_,
            '_GET_STATE_': self._handle_get_state_,
            '_GAME_ACTION_': self._handle_game_action_,
            '_LOG_OUT_': self._handle_log_out_,
        }

        # Init Network
        self._network_ = ServerNetwork()
        self._client_addresses_map_ = dict()
        # Init state
        self._time_elapsed_ = 0
        self._current_frame_ = 0
        self._reset_state_()
        # Init event queue
        self._events_queue_ = deque()
        # Start clock
        self._clock = pygame.time.Clock()

    def _reset_state_(self):
        # Get state form server
        self._time_elapsed_ = 0
        self._current_frame_ = 0

        # Init Logic
        self._logic_ = MainGameLogic()
        self._logic_.init_maze(maze_seed=11122000)
        self._logic_.init_players([])
        self._logic_.init_bullets([])

        # # Init View - TODO Delete when deployed
        # self._view_ = MainGameView()
        # self._view_.init_maze(self._logic_.get_maze())
        # self._view_.init_scoreboard(self._logic_.get_players())
        # self._view_.init_notification()
        # self._view_.init_players(self._logic_.get_players())
        # self._view_.init_bullets(self._logic_.get_bullets())

    @staticmethod
    def _get_event_(key_pressed):
        if key_pressed == pygame.K_UP:
            return UP
        if key_pressed == pygame.K_DOWN:
            return DOWN
        if key_pressed == pygame.K_LEFT:
            return LEFT
        if key_pressed == pygame.K_RIGHT:
            return RIGHT
        if key_pressed == pygame.K_SPACE:
            return SHOOT
        return None

    def _update(self):
        # Broadcast and processed packet
        packets = self._network_.receive(PROCESSED_EVENTS_PER_LOOPS)
        for raw_packet in packets:
            self._handle_packet_(raw_packet)

        # Choose events to handle
        processing_events = []
        while len(self._events_queue_):
            if self._events_queue_[0]['timeout'] == self._current_frame_:
                processing_events.append(self._events_queue_.popleft())
            else:
                break

        # Update with events
        self._logic_.update(processing_events)

        # self._view_.update()  # For debug illustration

    def loop(self):
        try:
            while True:
                while True:
                    dt = self._clock.tick(30)
                    self._time_elapsed_ += dt
                    while self._time_elapsed_ >= FRAME_RATE_MS:
                        self._time_elapsed_ -= FRAME_RATE_MS
                        self._current_frame_ += 1
                        self._update()
        except SystemExit:
            # Safely closed
            self._network_.safety_closed()
            # # TODO: DELETE
            # pygame.quit()
            exit()
        print("PLEASE WAIT FOR CLEANING THREADS...")

    def _handle_packet_(self, raw_packet):
        self.HANDLERS_MAP[raw_packet['game']['type']](raw_packet)

    def _handle_join_game_(self, raw_packet):
        instance_id = self._logic_.get_new_instance_id()
        user_id = self._logic_.get_new_user_id()
        self._client_addresses_map_[raw_packet['__client_address__']] = {'instance_id': instance_id, 'user_id': user_id}
        response = {'type': '_JOIN_GAME_',
                    'instance_id': instance_id,
                    'user_id': user_id,
                    'seed': random.randint(1, 100),
                    'timeout': self._current_frame_ + MAX_PING}
        self._network_.broadcast(response)
        self._events_queue_.append(response)

    def _handle_get_state_(self, raw_packet):
        game_packet = raw_packet['game']
        if self._logic_.check_instance_id(game_packet['instance_id']):
            response = {'type': '_GET_STATE_',
                        'instance_id': game_packet['instance_id'],
                        'user_id': game_packet['user_id'],
                        'state': self._logic_.serialize(),
                        'unprocessed_events': list(self._events_queue_),
                        'current_frame': self._current_frame_,
                        'time_elapsed': self._time_elapsed_}
            self._network_.send(response, raw_packet['__client_address__'])

    def _handle_game_action_(self, raw_packet):
        game_packet = raw_packet['game']
        if self._logic_.check_instance_id(game_packet['instance_id']):
            response = {'type': '_GAME_ACTION_',
                        'instance_id': game_packet['instance_id'],
                        'user_id': game_packet['user_id'],
                        'action': game_packet['action'],
                        'timeout': self._current_frame_ + MAX_PING}
            self._network_.broadcast(response)
            self._events_queue_.append(response)

    def _handle_log_out_(self, raw_packet):
        game_packet = raw_packet['game']
        if self._logic_.check_instance_id(self._client_addresses_map_[game_packet['address']]['instance_id']):
            response = {'type': '_LOG_OUT_',
                        'instance_id': self._client_addresses_map_[game_packet['address']]['instance_id'],
                        'user_id': self._client_addresses_map_[game_packet['address']]['user_id'],
                        'timeout': self._current_frame_ + MAX_PING
                        }
            self._network_.broadcast(response)
            self._events_queue_.append(response)