"""Game data loading and management."""

import yaml
from pathlib import Path
import logging
from typing import Dict, Any

class GameDataLoader:
    """Loads and manages game data from YAML files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(__file__).parent / "GameData"
        self._faction_data = None

    def load_all(self) -> None:
        """Load all game data."""
        self._faction_data = self._load_yaml("factions.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        try:
            with open(self.data_dir / filename, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load {filename}: {e}")
            return {}

    def get_faction_data(self) -> Dict[str, Any]:
        """Get faction and stats data."""
        if self._faction_data is None:
            self.load_all()
        return self._faction_data

    def get_stats_for_type(self, entity_type: str) -> Dict[str, int]:
        """Get stats for a specific entity type."""
        faction_data = self.get_faction_data()
        return faction_data.get(entity_type, {}).get('stats', {})

    def get_faction_relations(self, faction_name: str) -> Dict[str, int]:
        """Get relations for a specific faction."""
        faction_data = self.get_faction_data()
        return faction_data.get(faction_name, {}).get('relations', {})
