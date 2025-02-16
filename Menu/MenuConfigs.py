"""
Menu configuration data including font settings and menu layouts.
"""

from Menu.MenuTypes import MenuID, MenuItemType

# Fallback chain: Consolas -> System Default
FONT_CONFIGS = {
    "Title": {
        "Name": ["segoeuisymbol.ttf", "consolas.ttf"],
        "Size": 74,
        "Bold": False,
        "Antialias": True
    },
    "MenuItem": {
        "Name": ["segoeuisymbol.ttf", "consolas.ttf"],
        "Size": 36,
        "Bold": False,
        "Antialias": True
    },
    "HUD": {
        "Name": ["segoeuisymbol.ttf","consolas.ttf"],
        "Size": 24,
        "Bold": False,
        "Antialias": True
    },
    "ActivityLog": {
        "Name": ["segoeuisymbol.ttf","consolas.ttf"],
        "Size": 16,
        "Bold": False,
        "Antialias": True
    }
}

MENU_CONFIGS = {
    MenuID.MAIN: {
        "Title": "PyRogue",
        "Items": [
            {
                "Text": "Start Game",
                "Type": "ACTION",
                "Action": "StartGame"
            },
            {
                "Text": "Options",
                "Type": "ACTION",
                "Action": "ShowOptions"
            }
        ]
    },
    MenuID.OPTIONS: {
        "Title": "Options",
        "Items": [
            {
                "Text": "Resolution",
                "Type": "SELECTOR",
                "Action": "ChangeResolution",
                "GetOptions": "GetAvailableResolutions",
                "GetCurrent": "GetCurrentResolution"
            },
            {
                "Text": "Fullscreen",
                "Type": "TOGGLE",
                "Action": "ToggleFullscreen",
                "GetCurrent": "GetFullscreenState"
            },
            {
                "Text": "Back",
                "Type": "ACTION",
                "Action": "MenuBack"
            }
        ]
    },
    MenuID.PAUSE: {
        "Title": "Paused",
        "Items": [
            {
                "Text": "Resume",
                "Type": "ACTION",
                "Action": "ResumeGame"
            },
            {
                "Text": "Options",
                "Type": "ACTION",
                "Action": "ShowOptions"
            },
            {
                "Text": "Quit to Main Menu",
                "Type": "ACTION",
                "Action": "QuitToMain"
            }
        ]
    },
    MenuID.HUD: {
        "Title": "",  # No title for HUD
        "Position": "top-left",  # Special position indicator
        "Items": [
            {
                "Text": "HP",
                "Type": "STAT",
                "GetValue": "GetPlayerHP"
            }
        ]
    },
    MenuID.ACTIVITY_LOG: {
        "Title": "Activity Log (↑↓ or wheel to scroll, hold Shift for page scroll)",  # Updated scroll controls hint
        "Position": "right",  # Position on right side
        "Items": [
            {
                "Text": "",  # Will be populated with log messages
                "Type": "LOG",
                "GetValue": "GetActivityLogMessages"
            }
        ]
    }
}