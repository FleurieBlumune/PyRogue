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
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not GameData._initialized:
            self.logger = logging.getLogger(__name__)
            self._stats: Dict[str, EntityStats] = {}
            self._relations: Dict[str, Dict[str, int]] = {}
            self.logger.debug("Initializing GameData singleton")
            self._load_data()
            GameData._initialized = True

    @staticmethod
    def get_instance():
        if GameData._instance is None:
            GameData._instance = GameData()
            GameData._instance.logger.debug("Created new GameData instance")
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
                other = row['other_faction']
                disposition = int(row['disposition'])
                if faction not in self._relations:
                    self._relations[faction] = {}
                self._relations[faction][other] = disposition
                self.logger.debug(f"Loaded faction relation: {faction} -> {other} = {disposition}")

    def get_stats(self, entity_type: str) -> EntityStats:
        """Get stats for an entity type."""
        return self._stats.get(entity_type, EntityStats(100, 1000))  # Default stats

    def get_faction_disposition(self, faction: str, other: str) -> int:
        """Get disposition between factions. Checks both directions and returns most hostile value."""
        self.logger.debug(f"Current faction relations: {self._relations}")
        direct = self._relations.get(faction, {}).get(other, 0)
        reverse = self._relations.get(other, {}).get(faction, 0)
        self.logger.debug(f"Checking disposition {faction} -> {other}: direct={direct}, reverse={reverse}")
        # Return the more hostile (lower) disposition
        return min(direct, reverse)
