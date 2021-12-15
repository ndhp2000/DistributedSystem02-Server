import pygame

from config import WIN_WIDTH, WIN_HEIGHT
from view.bullet import BulletView
from view.maze import MazeView
from view.notification import NotificationView
from view.player import PlayerView
from view.scoreboard import ScoreboardView
from view.view_group import ViewGroup


class MainGameView:
    _MAZE_SCREEN_RATIO_ = (2 / 3, 1)
    _MAZE_SCREEN_OFFSET_ = (0, 0)

    _NOTIFICATION_SCREEN_RATIO_ = (1 / 3, 2 / 3)
    _NOTIFICATION_SCREEN_OFFSET_ = (2 / 3, 0)

    _SCOREBOARD_SCREEN_RATIO_ = (1 / 3, 1 / 3)
    _SCOREBOARD_SCREEN_OFFSET_ = (2 / 3, 2 / 3)

    def __init__(self):
        pygame.init()
        self._screen_display_ = pygame.display
        self._screen_display_.set_caption('Zace Maze')
        self._screen_ = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), 0, 32)
        self._maze_screen_ = None
        self._scoreboard_screen_ = None
        self._notification_screen_ = None

        self._players_view_ = None
        self._bullets_view_ = None

    def update(self, player=None):
        # Update maze
        maze_screen_offset_y = self._MAZE_SCREEN_OFFSET_[0] * self._screen_.get_height()
        maze_screen_offset_x = self._MAZE_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._maze_screen_.add_to_parent(self._screen_, (maze_screen_offset_y, maze_screen_offset_x))

        self._players_view_.draw(self._screen_)
        self._bullets_view_.draw(self._screen_)

        # Update Notification View
        notification_screen_offset_y = self._NOTIFICATION_SCREEN_OFFSET_[0] * self._screen_.get_height()
        notification_screen_offset_x = self._NOTIFICATION_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._notification_screen_.add_to_parent(self._screen_,
                                                 (notification_screen_offset_x, notification_screen_offset_y))

        # Update Scoreboard View
        self._scoreboard_screen_.reload_scoreboard()
        scoreboard_screen_offset_y = self._SCOREBOARD_SCREEN_OFFSET_[0] * self._screen_.get_height()
        scoreboard_screen_offset_x = self._SCOREBOARD_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._scoreboard_screen_.add_to_parent(self._screen_, (scoreboard_screen_offset_x, scoreboard_screen_offset_y))

        self._screen_display_.update()

    def init_maze(self, maze):
        maze_screen_height = int(self._screen_.get_height() * self._MAZE_SCREEN_RATIO_[0])
        maze_screen_width = int(self._screen_.get_width() * self._MAZE_SCREEN_RATIO_[1])
        maze_screen_offset_y = self._MAZE_SCREEN_OFFSET_[0] * self._screen_.get_height()
        maze_screen_offset_x = self._MAZE_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._maze_screen_ = MazeView(maze, maze_screen_height, maze_screen_width)
        self._maze_screen_.add_to_parent(self._screen_, (maze_screen_offset_y, maze_screen_offset_x))

    def init_players(self, players_group=None):
        self._players_view_ = ViewGroup(players_group, PlayerView)
        self._players_view_.draw(self._screen_)

    def init_bullets(self, bullets_group):
        self._bullets_view_ = ViewGroup(bullets_group, BulletView)

    def init_scoreboard(self, players):
        scoreboard_screen_height = int(self._screen_.get_height() * self._SCOREBOARD_SCREEN_RATIO_[0])
        scoreboard_screen_width = int(self._screen_.get_width() * self._SCOREBOARD_SCREEN_RATIO_[1])
        scoreboard_screen_offset_y = self._SCOREBOARD_SCREEN_OFFSET_[0] * self._screen_.get_height()
        scoreboard_screen_offset_x = self._SCOREBOARD_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._scoreboard_screen_ = ScoreboardView(scoreboard_screen_height, scoreboard_screen_width, players)
        self._scoreboard_screen_.add_to_parent(self._screen_, (scoreboard_screen_offset_x, scoreboard_screen_offset_y))

    def init_notification(self):
        notification_screen_height = int(self._screen_.get_height() * self._NOTIFICATION_SCREEN_RATIO_[0])
        notification_screen_width = int(self._screen_.get_width() * self._NOTIFICATION_SCREEN_RATIO_[1])
        notification_screen_offset_y = self._NOTIFICATION_SCREEN_OFFSET_[0] * self._screen_.get_height()
        notification_screen_offset_x = self._NOTIFICATION_SCREEN_OFFSET_[1] * self._screen_.get_width()
        self._notification_screen_ = NotificationView(notification_screen_height, notification_screen_width)
        self._notification_screen_.add_to_parent(self._screen_,
                                                 (notification_screen_offset_x, notification_screen_offset_y))

    def print_log(self, text):
        self._notification_screen_.print(text)
