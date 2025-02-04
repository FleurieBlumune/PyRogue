from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Any, Optional
import pygame
from MenuConfigs import FONT_CONFIGS

class MenuItemType(Enum):
    TEXT = auto()
    TOGGLE = auto()
    SELECTOR = auto()
    ACTION = auto()

class MenuItem:
    def __init__(self, 
                 text: str, 
                 item_type: MenuItemType,
                 callback: Optional[Callable] = None,
                 options: list[Any] = None,
                 value: Any = None):
        self.text = text
        self.type = item_type
        self.callback = callback
        self.options = options
        self.value = value
        self.selected = False
        
    def activate(self) -> Any:
        if self.callback:
            return self.callback()
        return None
    
    def next_value(self) -> Any:
        if self.type == MenuItemType.SELECTOR and self.options:
            current_index = self.options.index(self.value)
            self.value = self.options[(current_index + 1) % len(self.options)]
        elif self.type == MenuItemType.TOGGLE:
            self.value = not self.value
        return self.value
    
    def previous_value(self) -> Any:
        if self.type == MenuItemType.SELECTOR and self.options:
            current_index = self.options.index(self.value)
            self.value = self.options[(current_index - 1) % len(self.options)]
        return self.value
    
    def get_display_text(self) -> str:
        if self.type == MenuItemType.TOGGLE:
            return f"{self.text}: {'On' if self.value else 'Off'}"
        elif self.type == MenuItemType.SELECTOR:
            return f"{self.text}: {self.value}"
        return self.text

class Menu:
    def __init__(self, 
                 title: str,
                 font_large: pygame.font.Font,
                 font_small: pygame.font.Font):
        self.title = title
        self.items: list[MenuItem] = []
        self.selected_index = 0
        self.font_large = font_large
        self.font_small = font_small
        
    def add_item(self, item: MenuItem) -> None:
        self.items.append(item)
        
    def handle_input(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                return self.items[self.selected_index].activate()
            elif event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                item = self.items[self.selected_index]
                if event.key == pygame.K_RIGHT:
                    item.next_value()
                else:
                    item.previous_value()
                if item.callback:
                    return item.callback()
        return None
    
    def render(self, screen: pygame.Surface, width: int, height: int) -> None:
        # Draw title
        title_surface = self.font_large.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(title_surface, title_rect)
        
        # Draw menu items starting from vertical center
        start_y = height // 2
        for i, item in enumerate(self.items):
            color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
            text_surface = self.font_small.render(item.get_display_text(), True, color)
            pos = (width // 2, start_y + i * 40)
            rect = text_surface.get_rect(center=pos)
            screen.blit(text_surface, rect)

class MenuFactory:
    def __init__(self, action_handlers: dict[str, Callable]):
        self.action_handlers = action_handlers
        self.title_font = pygame.font.Font(FONT_CONFIGS["Title"]["Name"], FONT_CONFIGS["Title"]["Size"])
        self.item_font = pygame.font.Font(FONT_CONFIGS["MenuItem"]["Name"], FONT_CONFIGS["MenuItem"]["Size"])
        
    def create_menu(self, config: dict) -> Menu:
        menu = Menu(config["Title"], self.title_font, self.item_font)
        
        for item_config in config["Items"]:
            menu.add_item(self._create_menu_item(item_config))
            
        return menu
    
    def _create_menu_item(self, config: dict) -> MenuItem:
        item_type = MenuItemType[config["Type"]]
        
        # Get callback handler
        callback = self.action_handlers.get(config["Action"])
        
        # Handle special types
        if item_type == MenuItemType.SELECTOR:
            options_getter = self.action_handlers[config["GetOptions"]]
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback,
                options=options_getter(),
                value=current_getter()
            )
        elif item_type == MenuItemType.TOGGLE:
            current_getter = self.action_handlers[config["GetCurrent"]]
            return MenuItem(
                config["Text"],
                item_type,
                callback,
                value=current_getter()
            )
        
        return MenuItem(config["Text"], item_type, callback)
