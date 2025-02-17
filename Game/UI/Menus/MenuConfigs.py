"""
Menu configuration data including font settings and menu layouts.
"""

from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuItemType

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
        "Title": "Activity Log ↑↓",  # Updated scroll controls hint
        "Position": "right",  # Position on right side
        "Items": [
            {
                "Text": "",  # Will be populated with log messages
                "Type": "LOG",
                "GetValue": "GetActivityLogMessages"
            }
        ]
    },
    MenuID.INVENTORY: {
        "Title": "Inventory",
        "Position": "center",
        "Items": [
            {
                "Text": "Cards",
                "Type": "LIST",
                "GetValue": "GetInventoryCards",
                "Action": "SelectCard"
            },
            {
                "Text": "Build Deck",
                "Type": "ACTION",
                "Action": "ShowDeckBuilder"
            },
            {
                "Text": "Back",
                "Type": "ACTION",
                "Action": "MenuBack"
            }
        ]
    },
    MenuID.DECK_BUILDER: {
        "Title": "Deck Builder",
        "Position": "center",
        "Items": [
            {
                "Text": "Available Cards",
                "Type": "LIST",
                "GetValue": "GetAvailableCards",
                "Action": "AddCardToDeck"
            },
            {
                "Text": "Current Deck",
                "Type": "LIST",
                "GetValue": "GetCurrentDeck",
                "Action": "RemoveCardFromDeck"
            },
            {
                "Text": "Save Deck",
                "Type": "ACTION",
                "Action": "SaveDeck",
                "Enabled": "CanSaveDeck"
            },
            {
                "Text": "Back",
                "Type": "ACTION",
                "Action": "MenuBack"
            }
        ]
    },
    MenuID.CARD_DETAIL: {
        "Title": "Card Details",
        "Position": "center",
        "Items": [
            {
                "Text": "",  # Will be populated with card name
                "Type": "HEADER"
            },
            {
                "Text": "",  # Will be populated with card description
                "Type": "TEXT"
            },
            {
                "Text": "",  # Will be populated with card stats
                "Type": "STAT",
                "GetValue": "GetCardStats"
            },
            {
                "Text": "Use Card",
                "Type": "ACTION",
                "Action": "UseCard",
                "Enabled": "CanUseCard"
            },
            {
                "Text": "Back",
                "Type": "ACTION",
                "Action": "MenuBack"
            }
        ]
    },
    MenuID.IN_GAME_CARDS: {
        "Title": "Cards",
        "Position": "right",
        "Items": [
            {
                "Text": "Hand",
                "Type": "LIST",
                "GetValue": "GetCurrentHand",
                "Action": "SelectHandCard"
            },
            {
                "Text": "Draw Pile",
                "Type": "STAT",
                "GetValue": "GetDrawPileCount"
            },
            {
                "Text": "Discard Pile",
                "Type": "STAT",
                "GetValue": "GetDiscardPileCount"
            }
        ]
    }
}