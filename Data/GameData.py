"""Simple CSV-based game data management."""

import csv
from pathlib import Path
from typing import Dict, NamedTuple
import logging

class EntityStats(NamedTuple):
    quickness: int
    max_action_points: int

class GameData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameData, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self._stats: Dict[str, EntityStats] = {}
        self._relations: Dict[str, Dict[str, int]] = {}
        self._initialized = True
        self._load_data()

    @staticmethod
    def get_instance():
        if GameData._instance is None:
            GameData()
        return GameData._instance

    def _load_data(self):
        """Load all CSV data files."""
        data_dir = Path(__file__).parent / "CSV"
        
        # Load entity stats
        with open(data_dir / "entity_stats.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._stats[row['entity_type']] = EntityStats(
                    quickness=int(row['quickness']),
                    max_action_points=int(row['max_action_points'])
                )

        # Load faction relations
        with open(data_dir / "faction_relations.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                faction = row['faction']
                if faction not in self._relations:
                    self._relations[faction] = {}
                self._relations[faction][row['other_faction']] = int(row['disposition'])

    def get_stats(self, entity_type: str) -> EntityStats:
        """Get stats for an entity type."""
        return self._stats.get(entity_type, EntityStats(100, 1000))  # Default stats

    def get_faction_disposition(self, faction: str, other: str) -> int:
        """Get disposition between factions."""
        return self._relations.get(faction, {}).get(other, 0)
