"""Default entity statistics configuration."""

DEFAULT_STATS = {
    'PLAYER': {
        'quickness': 120,
        'max_action_points': 1000,
    },
    'HUMANOID': {
        'quickness': 100,
        'max_action_points': 1000,
    },
    'BEAST': {
        'quickness': 130,  # Beasts are fast
        'max_action_points': 800,
    },
    'UNDEAD': {
        'quickness': 70,   # Undead are slow but relentless
        'max_action_points': 1200,
    },
    'MERCHANT': {
        'quickness': 90,
        'max_action_points': 1000,
    },
    'DEFAULT': {
        'quickness': 100,
        'max_action_points': 1000,
    }
}
