from model.base_entity import Entity


class AbstractGroup:
    def __init__(self):
        self._entities_dict = {}
        self._index_entities = {}
        self._removed_entities = []

    def add(self, entity):
        self._entities_dict[entity] = 0
        self._index_entities[entity.get_id()] = entity

    def remove(self, entity):
        self._entities_dict[entity] = 1
        self._removed_entities.append(entity)

    def remove_by_id(self, deleted_id):
        for entity in self._entities_dict:
            if entity.get_id() == deleted_id:
                entity.remove()

    def has(self, entity):
        if self._entities_dict[entity] == 1:
            return False
        return True

    def empty(self):
        for entity in self._entities_dict:
            self.remove(entity)
            entity.remove(self)

    def __len__(self):
        return len(list(self._entities_dict))


class Group(AbstractGroup):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        return iter(sorted(self._entities_dict.keys()))

    def add(self, entity):
        super().add(entity)

    def update(self, *args, **kwargs):
        for entity in sorted(self._entities_dict.keys()):
            if self.has(entity):
                entity.update(*args, **kwargs)
        for entity in sorted(self._entities_dict.keys()):
            if self.has(entity):
                entity.synchronize()

        for entity in self._removed_entities:
            del self._entities_dict[entity]
            del self._index_entities[entity.get_id()]

        self._removed_entities = []

    def serialize(self):
        result = []
        for entity in sorted(self._entities_dict.keys()):
            if self.has(entity):
                result.append(entity.serialize())
        return result

    @staticmethod
    def groups_collide(group1, group2, remove_entity_group2_on_hit=False) -> {}:
        collide_function = Entity.collide
        collided_entities = {}
        for entity1 in group1:
            for entity2 in group2:
                if group1.has(entity1) and group2.has(entity2):
                    is_collided = collide_function(entity1, entity2)
                    if is_collided:
                        if entity1 not in collided_entities:
                            collided_entities[entity1] = []
                        if remove_entity_group2_on_hit:
                            entity2.remove()
                        else:
                            collided_entities[entity1].append(entity2)
        return collided_entities

    @staticmethod
    def entity_collide(entity, group):
        pass


class PlayerGroup(Group):
    def get_scores(self):
        result = []
        for player in self._entities_dict:
            result.append((player.get_id(), player.get_hp(), player.get_player_type()))
        result = sorted(result, key=lambda p: p[1])
        return result

    def reward_player(self, player_id, reward_amount):
        self._index_entities[player_id].reward(reward_amount)
