"""
Menu configuration data including font settings and menu layouts.
"""

from Menu.MenuTypes import MenuID

FONT_CONFIGS = {
    "Title": {"Name": None, "Size": 74},
    "MenuItem": {"Name": None, "Size": 36}
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
    }
} 