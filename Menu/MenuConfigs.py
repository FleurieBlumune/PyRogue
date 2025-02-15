"""
Menu configuration data including font settings and menu layouts.
"""

from Menu.MenuTypes import MenuID, MenuItemType  # Added MenuItemType since we use it in configs

FONT_CONFIGS = {
    "Title": {"Name": None, "Size": 74},
    "MenuItem": {"Name": None, "Size": 36},
    "HUD": {"Name": None, "Size": 24},  # Smaller font for HUD
    "ActivityLog": {"Name": None, "Size": 16}  # Even smaller for activity log
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
        "Title": "Activity Log",
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