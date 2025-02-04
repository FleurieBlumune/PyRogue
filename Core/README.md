# PyRogue Core Systems

This directory contains the core systems that power the game engine.

## Key Components

### GameLoop
Primary game controller that coordinates all other systems. Handles:
- Game initialization and settings
- Main update/render loop
- Title screen management
- System coordination

### EventManager
Singleton event system that provides game-wide communication. Features:
- Custom game events
- Event subscription/publishing
- Debug logging
- Centralized event processing

### InputHandler
Processes all user input and converts it to game actions. Manages:
- Keyboard and mouse input
- Camera control
- Movement processing
- Path selection

### Renderer
Handles all game visualization. Provides:
- Tile-based rendering
- Entity visualization
- Camera management
- Zoom functionality
- Window management

### TurnManager
Manages the game's turn-based systems. Handles:
- Turn sequencing
- Turn event broadcasting
- Action coordination

### MenuSystem
Flexible menu creation and management system. Features:
- Multiple menu item types (Text, Toggle, Selector, Action)
- Configurable layouts
- Event-driven input handling
- Custom styling support

## Event Types
Current supported game events:
```python
PLAYER_MOVED        # When player position changes
ENTITY_MOVED        # When any entity moves
PLAYER_TURN_ENDED   # End of player's turn
CAMERA_MOVED        # Camera position update
GAME_QUIT           # Game exit signal
EVENT_QUEUE_PROCESSED # All events processed
TURN_STARTED        # New turn begins
TURN_ENDED          # Current turn completes
```

## Usage Example
```python
# Initialize core systems
event_manager = EventManager.get_instance()
turn_manager = TurnManager.get_instance()

# Subscribe to events
event_manager.subscribe(GameEventType.PLAYER_MOVED, my_handler)

# Start game loop
game = GameLoop(width=800, height=600)
game.run()
```

## Dependencies
- pygame
- logging
- abc (for abstract base classes)
- enum
- collections.defaultdict
