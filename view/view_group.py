import pygame


class ViewGroup:
    def __init__(self, model_group, view_class_init_function): # View class init
        super().__init__()
        self._view_class_init_function = view_class_init_function
        self._model_group = model_group

    def draw(self, screen: pygame.Surface):
        for entity in self._model_group:
            if entity.is_removed():
                continue
            view_entity = self._view_class_init_function(entity)
            view_entity.add_to_parent(screen, view_entity.get_world_position(), is_centered=True)

