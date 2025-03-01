# Map System Implementation Prompts

This document contains detailed prompts for implementing various components of the roguelike map system. Each prompt is designed to generate a specific part of the system while providing enough context for implementation.

## Core Data Structures

### Prompt 1: Map Tile Definitions

```
Create or extend a Python enum called TileType for map tiles used in my roguelike game with the following requirements:

1. Include these basic tile types:
   - WALL: Represents solid walls, blocks movement and vision
   - FLOOR: Basic walkable surface
   - DOOR: Can be opened/closed and locked/unlocked
   - WINDOW: Blocks movement but not vision
   - STAIRS_UP: Connection to the floor above
   - STAIRS_DOWN: Connection to the floor below
   - UNEXPLORED: Tiles not yet seen by the player
   - PREVIOUSLY_SEEN: Tiles seen before but not currently visible

2. Each tile type should have:
   - A string representation (like "#" for walls, "." for floors)
   - A property indicating whether it blocks movement
   - A property indicating whether it blocks vision
   - A property indicating whether it's interactive

3. Add a method to convert between ASCII characters and TileTypes in both directions.

Use proper Python documentation with docstrings and type hints. The implementation should be compatible with the existing codebase.
```

### Prompt 2: Map Entity Classes

```
Create an enhanced entity hierarchy for my roguelike game that builds on my existing codebase:

1. Extend the base Entity class to include:
   - Floor/Z-coordinate in Position
   - Unique ID generation
   - Properties dictionary for flexible state storage
   - YAML serialization methods compatible with existing CSV data loading
   - Transformation capabilities for all animate entities

2. Implement these NPC subclasses extending my existing NPC class:
   - Civilian: Basic NPC with defined routines
     - Properties: role, routine, transformed_type
   - Guard: Security NPC with patrol routes
     - Properties: role, patrol_route, alert_level, last_seen_player
   - Animal: Already transformed entity or normal animal (could be former Civilian, Guard, or Player)
     - Properties: original_type, animal_type, transform_time, friendly

3. Create new Object base class with these subclasses:
   - Furniture: Static objects like desks, chairs
     - Properties: furniture_type, can_be_moved, blocks_movement
   - SecurityDevice: Cameras, alarms, card readers
     - Properties: active, disabled, detection_range, trigger_condition
   - Interactive: Computers, vending machines, phones
     - Properties: used, requires_keycard, interaction_result

4. Add factory methods for creating entities from string definitions, compatible with my existing GameData loading system.

Use my existing Stats and GameData systems where possible to avoid redundancy.
Use proper Python documentation with docstrings and type hints.
```

### Prompt 3: Game Map Structure

```
Create Floor and GameMap classes for my roguelike game with these specifications:

1. Floor class features:
   - 2D grid of TileType for basic layout
   - Collection of entities with positions
   - Visibility grid tracking unexplored/seen/visible tiles
   - Methods to:
     - Add/remove/move entities
     - Check movement validity between tiles
     - Update visibility based on player position
     - Get entities at a specific position
     - Convert to/from ASCII representation
   - Floor number identifier
   - Connection points to other floors (stairs)

2. GameMap class features:
   - Collection of Floor objects
   - Metadata (name, type, creation date, etc.)
   - Game state tracking (alert level, discovered status)
   - Lists of important state changes:
     - Transformed NPCs
     - Disabled security devices
     - Unlocked doors
     - Collected items
   - Methods to:
     - Save/load to/from file
     - Change floors
     - Update game state
     - Track player progress
   - Connections to the world map

3. Include helper methods for:
   - Path finding across the map
   - Line of sight calculations
   - Entity lookup by ID
   - State querying (is camera X disabled? Is NPC Y transformed?)

Use proper Python documentation with docstrings and type hints. Ensure both classes are serializable for save/load functionality.
```

## File I/O

### Prompt 4: Map File Parser

```
Create a comprehensive map file parser with these requirements:

1. Function signature: parse_map_file(file_path: str) -> GameMap

2. Parse these section types:
   - [metadata]: Key-value pairs for map information
   - [state]: Lists of state changes (transformed NPCs, etc.)
   - [floor_X]: ASCII representation of floor layout
   - [floor_X_items]: Entity definitions with properties
   - [floor_X_zones]: Special zone definitions (patrol routes, etc.)

3. Handle these parsing details:
   - ASCII characters → TileType conversion
   - Entity placement from single characters with properties
   - Property string parsing: "ENTITY_TYPE(key1:value1,key2:value2)"
   - Comment lines starting with #
   - Multi-line visibility masks
   - Coordinate pairs like (x,y)

4. Include validation:
   - Check for required sections
   - Validate floor connections
   - Verify entity references
   - Check for map boundary consistency

5. Add graceful error handling with specific error messages for:
   - File not found
   - Invalid format
   - Missing required sections
   - Inconsistent data

Use proper Python documentation with docstrings and type hints. The parser should be robust against common formatting errors.
```

### Prompt 5: Map File Writer

```
Create a map file writer with these requirements:

1. Function signature: save_map_to_file(game_map: GameMap, file_path: str) -> bool

2. Generate these sections:
   - File header with comments (name, creation date, last modified)
   - [metadata] section with map properties
   - [state] section with game state changes
   - [floor_X] sections with ASCII map representations
   - [floor_X_items] sections with entity definitions
   - [floor_X_zones] sections with special zones

3. Support these formatting features:
   - Convert TileType grid to ASCII characters
   - Create entity definitions with properties
   - Format property strings: "ENTITY_TYPE(key1:value1,key2:value2)"
   - Create visibility masks
   - Format coordinates as (x,y)

4. Implement these quality-of-life features:
   - Create backup of existing file before overwriting
   - Add file header comments for human readability
   - Include section comments explaining format
   - Pretty-print output with consistent indentation
   - Add timestamp for last modification

5. Include error handling:
   - Permission issues
   - Disk space issues
   - Encoding problems

Use proper Python documentation with docstrings and type hints. Return true on success, false on failure, with appropriate logging.
```

## Map Generation

### Prompt 6: Room Generation

```
Create a room generation module with these requirements:

1. Define a common interface:
   ```python
   def generate_room(room_type: str, width: int, height: int, params: dict) -> (list[list[TileType]], list[Entity])
   ```

2. Implement generators for these room types:
   - Office: Desks, chairs, computers, possibly meeting table
   - Bathroom: Stalls, sinks, mirrors
   - Break Room: Tables, chairs, vending machines, microwave
   - Hallway: Long passage with proper connections
   - Reception: Desk, waiting area, decorative elements
   - Security: Monitors, lockers, weapon storage
   - Storage: Shelves, boxes, storage units

3. For each room type, include:
   - Appropriate furniture placement
   - Door placement on edges
   - Window placement where appropriate
   - Entity placement (NPCs based on room type)
   - Variation algorithms (don't make all rooms identical)

4. Add these customization options:
   - Security level affecting camera placement
   - Population density affecting NPC count
   - Time of day affecting NPC positions
   - Room quality/condition (fancy offices vs. basic)

5. Include validation:
   - Ensure doors are accessible
   - Verify path exists between all points
   - Check for proper spacing

Use proper Python documentation with docstrings and type hints. Include randomization with seed support for reproducibility.
```

### Prompt 7: Building Layout Generator

```
Create a building layout generator with these requirements:

1. Function signature:
   ```python
   def generate_building(building_type: str, floors: int, width: int, height: int, params: dict) -> GameMap
   ```

2. Support these building types:
   - Office Building: Mostly offices, break rooms, bathrooms
   - Police Station: Offices, cells, armory, evidence room
   - Hospital: Patient rooms, operating theaters, reception
   - School: Classrooms, gym, cafeteria, offices
   - Shopping Center: Stores, food court, security office
   - Residential: Apartments, lobby, utility rooms

3. Implement this generation process:
   - Create outer walls and basic structure
   - Divide into zones based on building type
   - Place mandatory rooms for the building type
   - Fill remaining space with appropriate room types
   - Create hallways connecting all rooms
   - Place stairs between floors
   - Add doors and windows
   - Place appropriate NPCs
   - Add security features based on security level

4. Include these customization parameters:
   - Security level (0-4)
   - Population density (0-10)
   - Time of day (affects NPC placement)
   - Complexity (affects number of rooms)
   - Seed value for reproducibility

5. Ensure the result has:
   - All areas accessible
   - Appropriate distribution of room types
   - Logical placement of NPCs
   - Working floor connections
   - No isolated areas

Use proper Python documentation with docstrings and type hints. The generator should produce varied but realistic layouts.
```

### Prompt 8: Entity Placement

```
Create an entity placement system with these requirements:

1. Function signature:
   ```python
   def populate_map(game_map: GameMap, params: dict) -> None
   ```

2. Place these entity types:
   - Civilians based on location type and time of day
   - Guards with patrol routes
   - Furniture appropriate to each room type
   - Security devices (cameras, alarms)
   - Interactive objects (computers, vending machines)
   - Already transformed subjects (random placement)

3. Implement these placement strategies:
   - Role-based placement (receptionists at reception desks)
   - Density-based general placement
   - Patrol route generation for guards
   - Group-based placement (meeting rooms have multiple civilians)
   - Security coverage optimization (cameras cover key areas)

4. Consider these factors:
   - Time of day (more/fewer NPCs)
   - Building type (different civilian roles)
   - Security level (more guards and cameras)
   - Alert level (guard positioning)
   - Room functions (appropriate furniture)

5. Ensure these constraints:
   - No unreachable NPCs
   - No overlapping entities
   - Logical furniture arrangement
   - Appropriate density
   - Realism (guards at entrances, etc.)

Use proper Python documentation with docstrings and type hints. The system should make buildings feel appropriately populated and functional.
```

## Map Editing

### Prompt 9: Simple Map Editor

```
Create a terminal-based map editor with these requirements:

1. Core features:
   - ASCII display of the current floor
   - Cursor movement for tile selection
   - Tile placement (walls, floors, doors, etc.)
   - Entity placement
   - Floor navigation
   - Save/load functionality

2. UI components:
   - Main map display
   - Tool palette
   - Status line
   - Command input area
   - Mini-help display
   - Layer toggle (tiles/entities/both)

3. Editing operations:
   - Left-click (or SPACE): Place selected tile/entity
   - Right-click (or DELETE): Remove tile/entity
   - Number keys (1-9): Select tile type
   - E key: Place entity mode
   - F key: Place furniture mode
   - C key: Copy region
   - V key: Paste region
   - S key: Save map
   - L key: Load map
   - TAB key: Switch floors
   - Arrow keys: Move cursor

4. Advanced features:
   - Room templates (quickly place predefined rooms)
   - Patrol route definition
   - Entity property editing
   - Flood fill
   - Validation tools
   - Rectangle/line drawing tools

5. Technical requirements:
   - Use curses or similar library for terminal UI
   - Support resizable terminal window
   - Save files in the defined ASCII format
   - Provide a clean exit that doesn't break terminal

Use proper Python documentation with docstrings and type hints. Make the editor intuitive and efficient for creating maps.
```

### Prompt 10: Map Validation

```
Create a map validation module with these requirements:

1. Core validation functions:
   ```python
   def validate_map(game_map: GameMap) -> (bool, list[str])  # Returns (valid, errors)
   ```

2. Implement these validators:
   - Accessibility validator: Ensure all walkable tiles are reachable
   - Boundary validator: Check map boundaries are properly enclosed
   - Connection validator: Verify stairs properly connect between floors
   - Entity validator: Check entities are properly placed (not in walls)
   - Requirement validator: Verify map has all required components
   - Logic validator: Check game rules make sense (entry and exit points, etc.)

3. Add room-specific validation:
   - Bathroom validation (stalls, sinks)
   - Office validation (desks, chairs)
   - Security validation (cameras, coverage)
   - Reception validation (entry points, desk)

4. Implement these utility functions:
   - Flood fill from entry point to identify unreachable areas
   - Path finding to verify key locations are accessible
   - Entity relationship checking (guards near key areas)
   - Security coverage analysis

5. Add fix recommendations:
   - Suggest ways to fix validation errors
   - Auto-fix options for common problems
   - Warning levels (critical, warning, suggestion)

Use proper Python documentation with docstrings and type hints. The validator should help identify issues before they affect gameplay.
```

## Integration

### Prompt 11: Map State Manager

```
Create a map state manager with these requirements:

1. Core class definition:
   ```python
   class MapStateManager:
       def __init__(self, game_map: GameMap)
       def update_visibility(self, player_pos: Position) -> None
       def transform_npc(self, npc_id: str, animal_type: str) -> bool
       def toggle_door(self, door_id: str) -> bool
       def disable_security(self, device_id: str) -> bool
       def update_alert_level(self) -> int
       def get_visible_entities(self) -> list[Entity]
       # ...and more
   ```

2. Implement state tracking for:
   - Fog of war (unexplored/seen/visible)
   - NPC transformations
   - Door states (open/closed, locked/unlocked)
   - Security device states (active/disabled)
   - Alert level based on player actions
   - Collected/used items
   - Triggered events

3. Add these helper methods:
   - Query methods to check current state
   - Condition checkers (is exit accessible? are all guards neutralized?)
   - Path finding aware of current state
   - Vision calculations for security devices
   - Event trigger checkers

4. Include these optimization features:
   - Dirty region tracking (only update what changed)
   - Spatial partitioning for entity lookup
   - Caching for repeated queries
   - Batch updates

5. Add these gameplay helpers:
   - Methods to find safe routes
   - Security coverage analysis
   - Transformation progress tracking
   - Mission objective status

Use proper Python documentation with docstrings and type hints. The manager should efficiently track all relevant state changes during gameplay.
```

### Prompt 12: Map Format Converter

```
Create a map format conversion module with these requirements:

1. Core conversion functions:
   ```python
   def convert_procedural_to_ascii(generated_map: GameMap) -> str
   def convert_ascii_to_game_map(ascii_map: str) -> GameMap
   def apply_template_to_map(template_path: str, game_map: GameMap) -> GameMap
   ```

2. Implement these conversion features:
   - Translate between internal map representation and ASCII format
   - Convert entity instances to/from string definitions
   - Translate between game coordinates and ASCII positions
   - Convert visibility information to/from mask format
   - Apply generation templates to existing maps

3. Add these utility functions:
   - Extract floor sections from full map files
   - Merge multiple maps (useful for creating large areas)
   - Generate preview images from maps
   - Convert between different map formats
   - Extract statistics from maps (room counts, entity distribution)

4. Include optimization for:
   - Large maps with many entities
   - Memory-efficient conversion
   - Streaming conversion for very large files

5. Support these additional features:
   - Comments and annotations
   - Metadata preservation
   - Versioning information
   - Author attribution
   - Map merging with conflict resolution

Use proper Python documentation with docstrings and type hints. The converter should handle the translation efficiently and accurately.
```

### Prompt 13: Serialization Helpers

```
Create serialization helpers for complex map objects with these requirements:

1. Core serialization functions:
   ```python
   def serialize_entity(entity: Entity) -> str
   def deserialize_entity(definition: str) -> Entity
   def serialize_patrol_route(route: list[Position]) -> str
   def deserialize_patrol_route(definition: str) -> list[Position]
   def serialize_properties(properties: dict) -> str
   def deserialize_properties(definition: str) -> dict
   ```

2. Implement serialization for:
   - Entity states with all properties
   - Patrol routes with waypoints
   - Security device configurations
   - Property dictionaries with various value types
   - NPC behaviors and schedules
   - Event triggers and conditions

3. Use these formatting guidelines:
   - Entity: 'TYPE(key1:value1,key2:value2)'
   - Positions: '(x,y)'
   - Lists: '[item1,item2,item3]'
   - Simple property format: 'key:value'
   - Escape special characters properly

4. Include these helpers:
   - Type conversion utilities
   - Validation functions
   - Pretty printing for debugging
   - Compact modes for storage efficiency
   - Diff generation between states

5. Add support for:
   - Custom serialization for special types
   - Versioning for backward compatibility
   - Schema validation
   - Default values for missing properties
   - Enum value handling

Use proper Python documentation with docstrings and type hints. The helpers should make it easy to convert between objects and their string representations.
```

### Prompt 14: World Map Integration

```
Create a world map integration system with these requirements:

1. Core class definition:
   ```python
   class WorldMapManager:
       def __init__(self, world_map_path: str)
       def get_location(self, location_id: str) -> GameMap
       def save_location_state(self, location_id: str, game_map: GameMap) -> bool
       def update_world_state(self) -> None
       def can_travel_to(self, location_id: str) -> bool
       # ...and more
   ```

2. Implement these features:
   - Track which locations have been visited
   - Store the state of each location when the player leaves
   - Load location state when the player returns
   - Update world map based on player actions
   - Track alert levels across districts
   - Manage travel options between locations

3. Support these world mechanics:
   - Time passing between locations
   - NPC movement between locations
   - News/events spreading based on player actions
   - Security response to player activities
   - Transformation percentage tracking by district

4. Add these gameplay helpers:
   - Mission availability tracking
   - Resource distribution
   - Fast travel options
   - Safe house functionality
   - District status reporting

5. Include optimization for:
   - Minimal memory usage for inactive locations
   - Efficient state storage
   - Background simulation of unvisited locations
   - Lazy loading of location data

Use proper Python documentation with docstrings and type hints. The system should seamlessly connect individual maps with the larger game world.
```

### Prompt 15: Template System

```
Create a map template system with these requirements:

1. Core template functions:
   ```python
   def load_template(template_path: str) -> dict
   def apply_template(template: dict, dimensions: (int, int, int)) -> GameMap
   def extract_template(game_map: GameMap) -> dict
   ```

2. Template file format should include:
   - Building type specification
   - Room type distribution
   - Required room types
   - Entity distribution rules
   - Security level parameters
   - Connection requirements
   - Special features

3. Implement template application for:
   - Building layout generation
   - Room type selection
   - Entity placement
   - Security system arrangement
   - Civilian population
   - Room contents

4. Include these template features:
   - Percentage-based room distribution
   - Minimum/maximum counts for room types
   - Required entity placements
   - Conditional placements
   - Randomization parameters
   - Weighted selections

5. Add these quality-of-life features:
   - Template validation
   - Default values for missing parameters
   - Template composition (combine templates)
   - Template overrides
   - Template versioning

Use proper Python documentation with docstrings and type hints. The template system should make it easy to define generation rules for different building types.
```

## Additional Components

### Prompt 16: Fog of War System

```
Create a fog of war system with these requirements:

1. Core visibility classes and functions:
   ```python
   class VisibilityGrid:
       def __init__(self, width: int, height: int)
       def update(self, viewer_pos: Position, view_distance: int) -> set[Position]
       def is_visible(self, x: int, y: int) -> bool
       def is_explored(self, x: int, y: int) -> bool
       def get_visible_positions(self) -> set[Position]
       # ...and more
   
   def calculate_field_of_view(pos: Position, max_distance: int, obstacles: set[Position]) -> set[Position]
   ```

2. Implement these visibility states:
   - Unexplored: Never seen by player
   - Previously seen: Seen before but not currently visible
   - Currently visible: In player's field of view

3. Support these visibility features:
   - Line of sight calculation
   - Wall blocking
   - Door/window special handling
   - Vision distance limits
   - Memory of previously seen areas

4. Add these optimization techniques:
   - Incremental updates (only recalculate what changed)
   - Quadtree or similar for large maps
   - Precalculated visibility for static obstacles
   - Dirty region tracking

5. Include these gameplay elements:
   - Security camera vision cones
   - NPC sight ranges
   - Lighting effects (darker areas = shorter vision)
   - Stealth mechanics integration

Use proper Python documentation with docstrings and type hints. The fog of war system should efficiently handle visibility updates during gameplay.
```

### Prompt 17: Path Finding

```
Create a path finding system with these requirements:

1. Core path finding functions:
   ```python
   def find_path(start: Position, goal: Position, game_map: GameMap, entity_id: str = None) -> list[Position]
   def find_closest(start: Position, targets: list[Position], game_map: GameMap) -> Position
   def calculate_distance(pos1: Position, pos2: Position, game_map: GameMap = None) -> float
   ```

2. Implement these algorithms:
   - A* for optimal pathfinding
   - Breadth-first search for simple distances
   - Dijkstra's for multiple targets
   - Jump point search for optimization

3. Support these movement constraints:
   - Walls and obstacles
   - Entity-specific movement rules
   - Door states (open/closed)
   - Security level access
   - Special movement abilities

4. Add these optimization features:
   - Path caching
   - Grid chunking for large maps
   - Early exit optimizations
   - Hierarchical pathfinding
   - Waypoint simplification

5. Include these gameplay helpers:
   - Patrol route generation
   - Escape route finding
   - Stealth path finding (avoid cameras)
   - Group movement
   - Fallback paths

Use proper Python documentation with docstrings and type hints. The path finding system should efficiently handle navigation for both player and NPCs.
```

### Prompt 18: Map Loading Manager

```
Create a map loading manager with these requirements:

1. Core class definition:
   ```python
   class MapManager:
       def __init__(self, base_path: str)
       def load_map(self, map_id: str) -> GameMap
       def save_map(self, game_map: GameMap) -> bool
       def create_new_map(self, map_type: str, params: dict) -> GameMap
       def get_available_maps(self) -> list[str]
       # ...and more
   ```

2. Implement these features:
   - Lazy loading of maps
   - Caching frequently used maps
   - Map generation for new locations
   - Automatic saving of modified maps
   - Map versioning and backups

3. Support these file operations:
   - Load maps from static files
   - Generate maps from templates
   - Save maps with state changes
   - Export maps in different formats
   - Map file management (delete, rename, etc.)

4. Add these organizational helpers:
   - Categorization by building type
   - Search by map properties
   - Sorting options
   - Metadata browsing
   - Template management

5. Include these quality-of-life features:
   - Error recovery (corrupted files)
   - Auto-save
   - Map migration between versions
   - Development/production mode
   - Debugging helpers

Use proper Python documentation with docstrings and type hints. The manager should provide a clean, efficient interface for all map loading/saving operations.
```

### Prompt 19: NPC Behavior System

```
Create an NPC behavior system with these requirements:

1. Core class definitions:
   ```python
   class Behavior:
       def __init__(self, entity_id: str, params: dict)
       def update(self, game_map: GameMap) -> None
       def get_next_action(self) -> Action
       def react_to_event(self, event_type: str, data: dict) -> None
       # ...and more

   class PatrolBehavior(Behavior): pass
   class CivilianBehavior(Behavior): pass
   class GuardBehavior(Behavior): pass
   ```

2. Implement these NPC behaviors:
   - Patrol behavior (follow waypoints)
   - Guard behavior (stand position, respond to alerts)
   - Civilian behavior (work at desk, take breaks)
   - Transformed behavior (follows player, assists)
   - Hostile behavior (chase player, attack)

3. Support these behavior features:
   - Time-based routines (work hours, breaks)
   - Position-based triggers
   - Alert response levels
   - Group coordination
   - Memory of events

4. Add these interaction capabilities:
   - Response to player proximity
   - Reaction to transformation attempts
   - Security alert raising
   - Communication between NPCs
   - Use of environmental features

5. Include these state machines:
   - Idle → Alert → Searching → Combat
   - Working → Break → Return
   - Patrol → Investigate → Return
   - Normal → Transformed → Friendly

Use proper Python documentation with docstrings and type hints. The behavior system should create realistic, interesting NPC behaviors that respond to player actions.
```

### Prompt 20: Map Conversion Tools

```
Create map conversion tools with these requirements:

1. Core tool functions:
   ```python
   def convert_ascii_to_image(ascii_map: str, output_path: str) -> bool
   def convert_image_to_ascii(image_path: str) -> str
   def export_map_as_json(game_map: GameMap) -> dict
   def import_map_from_json(json_data: dict) -> GameMap
   ```

2. Implement these conversion tools:
   - ASCII map to PNG/JPEG visualization
   - Map to JSON for API usage
   - Map to CSV for data analysis
   - Map statistics extraction
   - Batch conversion utilities

3. Support these visualization options:
   - Customizable tile colors
   - Entity icons
   - Floor separation
   - Legend generation
   - Grid overlay

4. Add these utility features:
   - Command line interface
   - Batch processing
   - Format validation
   - Error reporting
   - Progress indication

5. Include these integration hooks:
   - Web viewer export
   - Level editor import/export
   - Version control friendly formats
   - Diff generation
   - Map merging tools

Use proper Python documentation with docstrings and type hints. The tools should make it easy to convert between formats and visualize maps for development.
```

This document provides a comprehensive set of prompts that break down the entire map system into manageable components. Each prompt includes specific requirements and details to guide implementation.
