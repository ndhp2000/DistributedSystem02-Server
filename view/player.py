import pygame

from config import WIN_WIDTH, MAP_WIDTH
from model.player import Player
from view.base_view import BaseView
from view.utils import convert_maze_to_world_pos


class PlayerView(BaseView):
    def __init__(self, player: Player):
        self._player = player
        self.name = "Player"

        r = self._player.get_maze_radius() * (WIN_WIDTH / MAP_WIDTH) * 0.5
        color = pygame.Color("red")
        super().__init__(r * 2, r * 2)
        self._screen_.fill(pygame.Color("black"))
        pygame.draw.circle(self._screen_, color,
                           (int(self._screen_.get_height() / 2),
                            int(self._screen_.get_width() / 2)),
                           r)

    def get_world_position(self):
        position = self._player.get_position()
        world_position = convert_maze_to_world_pos(position[0], position[1])
        return world_position
