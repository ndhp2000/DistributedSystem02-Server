import uuid
from collections import deque

import pygame
import pygame.locals
from pygame import QUIT

from config import PROCESSED_EVENTS_PER_LOOPS, MAX_PING, FRAME_RATE_MS, UP, DOWN, LEFT, RIGHT, SHOOT
from network.network import ServerNetwork
from view.view import MainGameView
from model.model import MainGameLogic


class Controller:
    def __init__(self):

        self.HANDLERS_MAP = {
            '_JOIN_GAME_': self._handle_join_game_,
            '_GET_STATE_': self._handle_get_state_,
            '_GAME_ACTION_': self._handle_game_action_,
            '_LOG_OUT_': self._handle_log_out_,
        }

        # Init Network
        # self._network_ = ServerNetwork()
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
        self._users_counter = 0
        self._connected_instances_ = set()

        # Init Logic
        self._logic_ = MainGameLogic(seed=1112000)
        self._logic_.init_maze(maze_seed=1112200)
        self._logic_.init_players()

        # Init View - TODO Delete when deployed
        self._view_ = MainGameView()
        self._view_.init_maze(self._logic_.get_maze())
        self._view_.init_scoreboard(self._logic_.get_players())
        self._view_.init_notification()
        self._view_.init_players(self._logic_.get_players())
        self._view_.init_bullets(self._logic_.get_bullets())

    def _get_new_user_id_(self):
        result = self._users_counter
        self._users_counter += 1
        return result

    def _get_new_instance_id_(self):
        result = str(uuid.uuid4())
        self._connected_instances_.add(result)
        return result

    def _check_instance_id_(self, instance_id):
        return instance_id in self._connected_instances_

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
        print("Frame = ", self._current_frame_)

        # Broadcast and processed packet
        # packets = self._network_.receive(PROCESSED_EVENTS_PER_LOOPS)
        # for raw_packet in packets:
        #     self._handle_packet_(raw_packet)

        # TODO DELETE
        # Catch key event
        input_event = None
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                input_event = self._get_event_(event.key)
                response = {'type': '_GAME_ACTION_',
                            'instance_id': '1234',
                            'user_id': 18120143,
                            'action': input_event,
                            'timeout': self._current_frame_}
                self._events_queue_.append(response)

        # Choose events to handle
        processing_events = []
        while len(self._events_queue_):
            if self._events_queue_[0]['timeout'] == self._current_frame_:
                processing_events.append(self._events_queue_.popleft())
            else:
                break

        if len(processing_events):
            print("CURRENT FRAME = ", self._current_frame_)
            print("EVENT_QUEUE = ", self._events_queue_)
            print("PROCESSING EVENTS = ", processing_events)

        # Update with events
        self._logic_.update(processing_events)

        self._view_.update()  # For debug illustration

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
            # self._network_.safety_closed()
            # TODO: DELETE
            pygame.quit()
            exit()
        print("PLEASE WAIT FOR CLEANING THREADS...")

    def _handle_packet_(self, raw_packet):
        self.HANDLERS_MAP[raw_packet['game']['type']](raw_packet)

    def _handle_join_game_(self, raw_packet):
        instance_id = self._get_new_instance_id_()
        user_id = self._get_new_user_id_()
        response = {'type': '_JOIN_GAME_',
                    'instance_id': instance_id,
                    'user_id': user_id,
                    'timeout': self._current_frame_ + MAX_PING}
        self._network_.broadcast(response)
        self._events_queue_.append(response)

    def _handle_get_state_(self, raw_packet):
        game_packet = raw_packet['game']
        if self._check_instance_id_(game_packet['instance_id']):
            response = {'type': '_GET_STATE_',
                        'instance_id': game_packet['instance_id'],
                        'user_id': game_packet['user_id'],
                        'state': self._logic_.serialize(),
                        'unprocessed_events': list(self._events_queue_),
                        'current_frame': self._current_frame_}
            self._network_.send(response, raw_packet['__client_address__'])

    def _handle_game_action_(self, raw_packet):
        game_packet = raw_packet['game']
        if self._check_instance_id_(game_packet['instance_id']):
            response = {'type': '_GAME_ACTION_',
                        'instance_id': game_packet['instance_id'],
                        'user_id': game_packet['user_id'],
                        'action': game_packet['action'],
                        'timeout': self._current_frame_ + MAX_PING}
            self._network_.broadcast(response)
            self._events_queue_.append(response)

    def _handle_log_out_(self, raw_packet):
        pass
