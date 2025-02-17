"""
Turn-based game management system.
"""

import logging
from Engine.Core.Events import EventManager, GameEventType
from typing import List, Any, Set

class TurnManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TurnManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.event_manager = EventManager.get_instance()
            self.current_turn = 0
            self._registered_entities: Set[Any] = set()
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger(__name__)
            self._initialized = True

    @staticmethod
    def get_instance():
        if TurnManager._instance is None:
            TurnManager()
        return TurnManager._instance

    def register_entity(self, entity: Any) -> None:
        """Register an entity for turn processing and give initial AP"""
        if entity not in self._registered_entities:
            # Give initial AP when registering
            entity.stats.accumulate_action_points()
            self._registered_entities.add(entity)
            self.logger.debug(f"Registered entity {entity.type.name} for turn processing with {entity.stats.action_points} AP")

    def unregister_entity(self, entity: Any) -> None:
        """Unregister an entity from turn processing"""
        if entity in self._registered_entities:
            self._registered_entities.remove(entity)
            self.logger.debug(f"Unregistered entity {entity.type.name} from turn processing")

    def start_turn(self, active_entities: List[Any]):
        """
        Process a new turn, handling entities in order of quickness.
        
        Args:
            active_entities: List of entities to process this turn
        """
        self.current_turn += 1
        self.logger.debug(f"Starting turn {self.current_turn} with {len(active_entities)} entities")
        
        # Only process registered entities
        active_registered = [e for e in active_entities if e in self._registered_entities]
        self.logger.debug(f"Found {len(active_registered)} registered entities")
        
        # Sort entities by quickness and max AP for turn order
        sorted_entities = sorted(
            active_registered,
            key=lambda e: (e.stats.quickness, e.stats.max_action_points),
            reverse=True
        )
        self.logger.debug(f"Processing entities in order: {[(e.type.name, e.stats.quickness) for e in sorted_entities]}")
        
        # Signal turn start
        self.event_manager.emit(GameEventType.TURN_STARTED, turn_number=self.current_turn)
        
        # Process each entity's turn
        for entity in sorted_entities:
            self.logger.debug(f"Processing turn for {entity.type.name} (AP: {entity.stats.action_points}, Quickness: {entity.stats.quickness})")
            self.event_manager.emit(
                GameEventType.ENTITY_TURN,
                entity=entity,
                visible_entities=self._get_visible_entities(entity, active_registered)
            )
            self.event_manager.process_events()
        
        # Signal turn end
        self.logger.debug(f"Ending turn {self.current_turn}")
        self.event_manager.emit(GameEventType.TURN_ENDED, turn_number=self.current_turn)

    def _get_visible_entities(self, entity: Any, all_entities: List[Any]) -> List[Any]:
        """Get list of entities visible to the given entity"""
        visible = []
        for other in all_entities:
            if other != entity:
                dx = abs(entity.position.x - other.position.x)
                dy = abs(entity.position.y - other.position.y)
                if dx <= entity.detection_range and dy <= entity.detection_range:
                    visible.append(other)
        return visible
