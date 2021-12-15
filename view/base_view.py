import pygame


class BaseView:
    def __init__(self, screen_height, screen_width):
        self._screen_ = pygame.Surface((screen_width, screen_height), 0, 32)

    def _clear_view(self):
        self._screen_.fill((0, 0, 0))

    def _add_child(self, child: pygame.Surface, location):
        self._screen_.blit(child, child.get_rect(center=location))

    def get_world_position(self):
        assert False

    def add_to_parent(self, parent: pygame.Surface, location=None, is_centered=None):
        if location is None:
            location = self.get_world_position()

        if is_centered is None:
            parent.blit(self._screen_, location)
        else:
            parent.blit(self._screen_, self._screen_.get_rect(center=location))
