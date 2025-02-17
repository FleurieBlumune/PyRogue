"""
Tests for the menu system components.
"""

import pytest
import pygame
import os
from Engine.UI.MenuSystem.MenuItem import MenuItem
from Engine.UI.MenuSystem.Menu import Menu
from Engine.UI.MenuSystem.MenuTypes import MenuID, MenuItemType
from Game.UI.Menus.MenuFactory import MenuFactory
from Game.UI.Menus.MenuConfigs import MENU_CONFIGS, FONT_CONFIGS

# Initialize pygame properly for testing
pygame.init()
os.environ['SDL_VIDEODRIVER'] = 'dummy' if os.environ.get('CI') else 'window'
pygame.display.set_mode((800, 600))

@pytest.fixture
def mock_action_handlers():
    """Create mock handlers for all actions found in menu configs"""
    handlers = {}
    
    # Collect all unique actions from menu configs
    for menu_config in MENU_CONFIGS.values():
        for item in menu_config["Items"]:
            # Handle basic actions
            action = item.get("Action")
            if action and action not in handlers:
                handlers[action] = lambda: None
                
            # Handle getter actions for special types
            if item["Type"] in ["SELECTOR", "TOGGLE"]:
                if "GetOptions" in item:
                    handlers[item["GetOptions"]] = lambda: ["800x600", "1024x768"]
                if "GetCurrent" in item:
                    handlers[item["GetCurrent"]] = lambda: "800x600"
    
    # Override specific handlers that need return values
    handlers["StartGame"] = lambda: {"exit": True}
    handlers["GetFullscreenState"] = lambda: False
    handlers["ResumeGame"] = lambda: None
    handlers["QuitToMain"] = lambda: {"exit": True, "to_main": True}
    
    return handlers

@pytest.fixture
def menu_factory(mock_action_handlers):
    return MenuFactory(mock_action_handlers)

class TestMenuSystem:
    @pytest.mark.parametrize("menu_id", [menu_id for menu_id in MenuID])
    def test_menu_structure(self, menu_factory, menu_id):
        """Test each menu's structure matches its configuration"""
        config = MENU_CONFIGS[menu_id]
        menu = menu_factory.create_menu(config)
        
        assert menu.title == config["Title"]
        assert len(menu.items) == len(config["Items"])
        
        # Test each menu item matches its configuration
        for i, (item, item_config) in enumerate(zip(menu.items, config["Items"])):
            assert item.text == item_config["Text"]
            assert item.type == MenuItemType[item_config["Type"]]
            
            # Test special item types
            if item_config["Type"] == "SELECTOR":
                assert isinstance(item.options, list)
                assert item.value in item.options
            elif item_config["Type"] == "TOGGLE":
                assert isinstance(item.value, bool)
    
    @pytest.mark.parametrize("menu_id", [menu_id for menu_id in MenuID])
    def test_menu_navigation(self, menu_factory, menu_id):
        """Test navigation works for each menu"""
        menu = menu_factory.create_menu(MENU_CONFIGS[menu_id])
        item_count = len(MENU_CONFIGS[menu_id]["Items"])
        
        # Test down navigation
        for i in range(item_count * 2):  # Test wrap-around
            expected_index = i % item_count
            assert menu.selected_index == expected_index
            menu.handle_input(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
    
    @pytest.mark.parametrize("menu_id", [menu_id for menu_id in MenuID])
    def test_menu_rendering(self, menu_factory, menu_id):
        """Test rendering for each menu"""
        menu = menu_factory.create_menu(MENU_CONFIGS[menu_id])
        surface = pygame.Surface((800, 600))
        surface.fill((0, 0, 0))
        menu.render(surface, 800, 600)
        
        # Verify title and items are rendered at expected positions
        def has_content(y):
            return any(any(surface.get_at((400 + x, y + offset))[:3]) 
                      for x in range(-5, 6)
                      for offset in range(-5, 6))
        
        # Check title
        assert has_content(150), f"No title content found for {menu_id}"
        
        # Check first item
        assert has_content(300), f"No menu item content found for {menu_id}"
    
    def test_all_actions_have_handlers(self, mock_action_handlers):
        """Verify all actions in configs have corresponding handlers"""
        for menu_id in MenuID:
            config = MENU_CONFIGS[menu_id]
            for item in config["Items"]:
                if "Action" in item:
                    assert item["Action"] in mock_action_handlers
                if "GetOptions" in item:
                    assert item["GetOptions"] in mock_action_handlers
                if "GetCurrent" in item:
                    assert item["GetCurrent"] in mock_action_handlers

def teardown_module(module):
    pygame.quit()
