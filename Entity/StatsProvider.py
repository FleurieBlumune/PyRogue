"""Provider for entity statistics."""

from Entity.Stats import Stats
from Entity.EntityType import EntityType
from Data.GameData import GameData

class StatsProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsProvider, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    @staticmethod
    def get_instance():
        if StatsProvider._instance is None:
            StatsProvider()
        return StatsProvider._instance

    def create_stats(self, entity_type: EntityType) -> Stats:
        """Create a Stats instance based on entity type."""
        type_name = entity_type.name
        stats_data = GameData.get_instance().get_stats(type_name)
        return Stats(
            quickness=stats_data.quickness,
            max_action_points=stats_data.max_action_points,
            max_hp=stats_data.max_hp
        )
