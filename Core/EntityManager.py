"""
Manages entity lifecycle and coordination.
"""

import logging
from typing import List
from Core.Interfaces import IEntityContainer, IEntity
from Core.TurnManager import TurnManager

class EntityManager(IEntityContainer):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EntityManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.entities: List[IEntity] = []
            self.turn_manager = TurnManager.get_instance()
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        if EntityManager._instance is None:
            EntityManager()
        return EntityManager._instance

    def add_entity(self, entity: IEntity) -> None:
        """Add an entity and register it for turn processing"""
        if entity not in self.entities:
            self.entities.append(entity)
            self.turn_manager.register_entity(entity)
            self.logger.debug(f"EntityManager: Added {entity.type.name} to managed entities")

    def remove_entity(self, entity: IEntity) -> None:
        """Remove an entity and unregister it from turn processing"""
        if entity in self.entities:
            self.entities.remove(entity)
            self.turn_manager.unregister_entity(entity)
            self.logger.debug(f"EntityManager: Removed {entity.type.name} from managed entities")

    def get_entities(self) -> List[IEntity]:
        """Get all managed entities"""
        self.logger.debug(f"EntityManager: Getting {len(self.entities)} entities: {[e.type.name for e in self.entities]}")
        return self.entities.copy()