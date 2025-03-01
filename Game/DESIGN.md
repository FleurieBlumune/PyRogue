# PyRogue Design Document

## Game Overview
A roguelike game where the player uses serum injectors (represented as cards) to transform NPCs into various animals. The game combines deck-building mechanics with traditional roguelike elements.

## Core Systems

### Card System
The game uses a card-based inventory system where each card represents a serum injector that can transform entities into different animals.

#### Deck Management
The deck system represents the player's actively available cards during gameplay:
- Maximum deck size of 20 cards
- Cards must be in the player's inventory to be added to deck
- Deck is shuffled at the start of each level
- Draw pile and discard pile mechanics
- Hand size of 5 cards
- Cards are discarded after use (if not consumed)
- Deck can be modified between levels
- Deck persistence between levels (unless cards are consumed)

#### Card Data Management
Cards are defined in `Data/CSV/cards.csv` with the following structure:
- `id`: Unique identifier for the card
- `name`: Display name of the card
- `description`: Card description
- `rarity`: Card rarity (COMMON, UNCOMMON, RARE, LEGENDARY)
- `transformation`: Target animal type
- `duration`: Duration in seconds (-1 for permanent)
- `success_rate`: Float between 0.0 and 1.0
- `side_effects`: Comma-separated list of side effects
- `max_uses`: Integer number of uses (-1 for infinite)

The `CardLoader` utility in `Game/Content/Cards/CardLoader.py` handles loading and validating card data from the CSV file.

#### Card Structure
- **Base Card Properties**
  - Unique ID
  - Name
  - Description
  - Rarity (Common, Uncommon, Rare, Legendary)
  - Usage limits
  - Current usage count

#### Card Effects
- **Transformation Properties**
  - Target animal type
  - Duration (permanent or temporary)
  - Success rate
  - Side effects

#### Card Tiers
1. **Basic Injector (Common)**
   - 75% success rate
   - Permanent transformation
   - Minor side effects
   - 3 uses

2. **Advanced Injector (Uncommon)**
   - 90% success rate
   - Permanent transformation
   - Minimal side effects
   - 2 uses

3. **Experimental Injector (Rare)**
   - 100% success rate
   - Temporary transformation (5 minutes)
   - Unique side effects
   - 1 use

4. **Masterwork Injector (Legendary)**
   - 100% success rate
   - Permanent transformation
   - No side effects
   - 5 uses

### Inventory Management
- Maximum of 30 unique cards
- Stack system for multiple copies of the same card
- 5 active card slots for quick access
- Card organization by rarity and type

### Current Animal Types
- Rat
- Cat
- Dog
- Wolf
- Bear

### UI System

#### Menu Structure
The game features several specialized menus for card management:

1. **Inventory Menu** (`MenuID.INVENTORY`)
   - Implementation Details:
     - Centered modal window
     - Dark semi-transparent background overlay
     - Two main sections:
       - Left panel (350px): Available cards list
       - Right panel (350px): Current deck list
     - Bottom panel (100px): Card details and actions
     - Controls displayed at top:
       - ESC: Close inventory
       - Tab: Switch between panels
       - Enter: Add/Remove card from deck
   - Visual Elements:
     - Card entries show:
       - Name
       - Rarity (color-coded)
       - Quantity owned
       - If in deck (quantity)
     - Selected card shows:
       - Full description
       - Stats
       - Usage information
   - Functionality:
     - Toggle visibility with 'I' key
     - ESC to close
     - Persist changes on close
     - Auto-save deck modifications

2. **Deck Builder** (`MenuID.DECK_BUILDER`)
   - Available cards list
   - Current deck list
   - Deck validation
   - Save/cancel options

3. **Card Details** (`MenuID.CARD_DETAIL`)
   - Card name and description
   - Detailed stats display
   - Use card option (when available)
   - Side effects list

4. **In-Game Cards** (`MenuID.IN_GAME_CARDS`)
   - Current hand display
   - Draw pile counter
   - Discard pile counter
   - Quick card selection

#### Visual Elements
- Rarity symbols:
  - Common: ◆ (White)
  - Uncommon: ◆ (Green)
  - Rare: ◆ (Blue)
  - Legendary: ★ (Gold)
- Card counts and stack display
- Scrollable card lists
- Stat displays

#### Controls
- **In Game**
  - `Tab`: Toggle card hand display
  - `I`: Open inventory
  - `1-5`: Quick select cards in hand
  - `Space`: Use selected card
  - `Esc`: Open pause menu

- **Inventory/Deck Building**
  - `Arrow Keys`: Navigate lists
  - `Enter`: Select/Use card
  - `Tab`: Switch between lists
  - `Esc`: Back/Close menu

### World Map System

#### Overview
The world map provides a higher-level view of the city, allowing players to strategically choose their next target location. Players can freely navigate between the world map and individual zones, planning their activities across different neighborhoods and districts.

#### Map Structure
1. **Districts**
   - Downtown (high security, high value targets)
   - Residential (suburbs, apartments)
   - Commercial (shopping centers, offices)
   - Industrial (warehouses, factories)
   - Educational (schools, universities)
   - Government (city hall, municipal buildings)

2. **Navigation Points**
   - Individual buildings/locations
   - Metro stations
   - Bus stops
   - Alleyway shortcuts
   - Safe houses

#### Map Features
1. **Location Types**
   - **Primary Targets**
     - Police Stations
     - Hospitals
     - Schools
     - Office Buildings
     - Shopping Centers
     - Government Buildings
   
   - **Support Locations**
     - Safe Houses (save points)
     - Black Markets (card trading)
     - Ally Hideouts (mission givers)
     - Storage Units (inventory expansion)

2. **Travel System**
   - Walk between adjacent locations
   - Use metro for fast travel (once unlocked)
   - Unlock shortcuts through story progression
   - Different travel options affect entry points in locations

3. **Information Display**
   - Alert level per district
   - Known security measures
   - Transformation progress
   - Available missions/objectives
   - Time of day
   - Population density

#### Strategic Elements
1. **District Status**
   - Transformation percentage
   - Alert level
   - Security presence
   - Available resources
   - Faction influence

2. **Time Management**
   - Day/Night cycle
   - Location schedules
   - Security shift changes
   - Population patterns

3. **Risk vs Reward**
   - Higher-value targets in secure areas
   - Resource distribution
   - Security response times
   - Escape route planning

#### Progression Mechanics
1. **District Unlocking**
   - Story-based progression
   - Transformation percentage thresholds
   - Security clearance requirements
   - Contact network expansion

2. **Travel Options**
   - Initially limited to walking
   - Unlock public transport
   - Discover shortcuts
   - Establish safe houses

3. **Information Gathering**
   - Reveal security patterns
   - Discover entry points
   - Learn patrol routes
   - Map restricted areas

#### Interface Elements
1. **Main Map View**
   - Zoomable city map
   - District boundaries
   - Location markers
   - Travel routes
   - Alert indicators

2. **Location Details**
   - Building information
   - Security level
   - Population details
   - Known entry points
   - Available missions

3. **Status Overlay**
   - Current objectives
   - District statistics
   - Alert levels
   - Time of day
   - Quick travel options

4. **Control Scheme**
   - WASD/Arrows for navigation
   - Mouse for selection
   - Tab for info overlay
   - Space to enter location
   - M to toggle map

### Zone Generation System

#### Overview
The game takes place across various urban locations, where the player (a member of an anthropomorphic animal society) uses serums to transform regular humans. Each zone represents a different type of civilian infrastructure or public space.

#### Zone Types
1. **Static Zones**
   - **Format**: JSON/YAML definition files
   - **Components**:
     - Building layouts and floor plans
     - Entry/exit points
     - Required NPC placements
     - Furniture and objects
     - Security measures
   - **Examples**:
     - Police Stations
     - Hospitals
     - Schools
     - Office Buildings
     - Shopping Centers
     - Government Buildings
     - Residential Areas

2. **Procedural Zones**
   - **Generation Parameters**:
     - Building type/theme
     - Size and floor count
     - Required room types
     - Population density
     - Security presence
   - **Room Types**:
     - Offices/Classrooms
     - Common Areas
     - Storage/Utility
     - Restricted Areas
     - Public Spaces

#### Zone Definition Format
```yaml
zone_id: "downtown_office_1"
zone_type: "OFFICE_BUILDING"
alert_level: 1  # How aware/suspicious the population is
dimensions:
  floors: 3
  width: 50
  height: 50

# Static floor/room definitions
static_areas:
  - id: "lobby"
    floor: 1
    type: "RECEPTION"
    position: [5, 5]
    dimensions: [15, 20]
    required_entities:
      - type: "CIVILIAN"
        role: "RECEPTIONIST"
        count: 1
      - type: "GUARD"
        role: "SECURITY"
        count: 1
    objects:
      - type: "DESK"
        position: [7, 7]
      - type: "SECURITY_CAMERA"
        position: [6, 6]

# Procedural generation rules
generation_rules:
  min_rooms_per_floor: 6
  max_rooms_per_floor: 10
  room_types:
    - type: "OFFICE"
      weight: 50
      min_count: 4
    - type: "BREAK_ROOM"
      weight: 20
      min_count: 1
    - type: "BATHROOM"
      weight: 15
      count_per_floor: 2
  
  # Population distribution
  population:
    CIVILIAN: 
      weight: 70
      min_per_room: 1
      roles: ["WORKER", "VISITOR"]
    GUARD:
      weight: 15
      patrol_routes: true
    SUBJECT:
      weight: 15  # Already transformed individuals
```

#### Static Map Editor System

##### Map Format
```
# police_station_1.map
[metadata]
name: Downtown Police Station
type: POLICE_STATION
security_level: 3
floors: 2

[floor_1]
# Legend:
# # - Wall          . - Floor     D - Door
# W - Window        E - Entry     ^ - Stairs Up
# S - Security      R - Reception  L - Locker
# C - Camera        G - Guard     P - Prison Cell
# = - Desk         @ - Chair     * - Special Spawn
####################################
#        Downtown Police Station    #
####################################
#WWWWWWWWWWWWWWWWWWWWW#############
#...................D..............#
#..=R=..............#.....PPPPPP..#
#..@...C...........D#.....PPPPPP..#
#...................#.....PPPPPP..#
#........G.........#.....PPPPPP..#
#...................#.............#
#..S=...............D............#
#WWWWWWWWW#D#WWWWWWW#............#
#.........#.#.......#....^.......#
#.........#.#.......#............#
####################################

[floor_1_entities]
R: CIVILIAN[patrol=entry_loop]
G: GUARD[role=DESK_SERGEANT]
S: GUARD[role=SECURITY]

[floor_1_objects]
=: DESK
@: CHAIR
C: SECURITY_CAMERA[rotation=180,range=8]

[floor_1_zones]
entry_loop: {
    type: PATROL_ROUTE
    points: [(8,3), (15,3), (15,8), (8,8)]
}

[floor_2]
####################################
#          Evidence Room           #
####################################
#............#..................L.#
#............#..................L.#
#....E=......D...................#
#....@.......#...................#
#............#...................#
#............#...................#
#WWWWWW#D#WWW#...................#
#......#.#....#...................#
#......#v#....#...................#
####################################

[floor_2_entities]
E: CIVILIAN[role=EVIDENCE_CLERK]

[floor_2_objects]
=: DESK
@: CHAIR
L: LOCKER[content=EVIDENCE]

[connections]
floor_1.^: floor_2.v
```

##### Editor Features
1. **Visual Editor**
   - ASCII-based grid editing
   - Multiple floors
   - Real-time preview
   - Copy/paste regions
   - Undo/redo support

2. **Entity Placement**
   - Drag and drop from entity palette
   - Configure entity properties
   - Define patrol routes
   - Set spawn conditions

3. **Object Management**
   - Place furniture and items
   - Configure object properties
   - Set interaction rules
   - Define locked/restricted status

4. **Zone Definition**
   - Draw patrol routes
   - Mark restricted areas
   - Define trigger zones
   - Set camera coverage

5. **Validation Tools**
   - Path accessibility checking
   - Required exits verification
   - Entity placement rules
   - Security coverage analysis

##### Editor Controls
```
[Editor Controls]
Navigation:
- Arrow Keys: Move cursor
- Tab: Switch floors
- Space: Place/remove tile
- E: Place entity
- O: Place object
- Z: Define zone
- C: Copy region
- V: Paste region
- S: Save map
- L: Load map
- R: Rotate selection

Quick Tiles:
1: Wall (#)
2: Floor (.)
3: Door (D)
4: Window (W)
5: Stairs (^/v)
```

##### Integration Features
1. **Export Options**
   - Binary format for game
   - ASCII for version control
   - PNG preview generation
   - Tileset preview

2. **Import Capabilities**
   - Merge partial layouts
   - Import object templates
   - Load entity presets
   - Convert from PNG layouts

3. **Scripting Support**
   - Define custom behaviors
   - Set up triggers
   - Create event sequences
   - Configure security responses

4. **Testing Tools**
   - Pathfinding visualization
   - Security coverage display
   - NPC routine simulation
   - Spawn point verification

This format provides several advantages:
- Visual representation of layouts
- Easy to edit in any text editor
- Clear connection between floors
- Flexible entity and object placement
- Support for complex behaviors
- Version control friendly

#### Map Persistence System

##### Generated Map Saving
```
# generated_downtown_office_3.save
[metadata]
name: Zenith Corp Office
type: OFFICE_BUILDING
alert_level: 2
generation_seed: 1234567
generation_date: 2024-03-15T14:30:00
last_visit: 2024-03-15T15:45:00

[state]
transformed_npcs: ["civilian_23", "civilian_45"]
alert_triggers: ["camera_2", "guard_4"]
discovered_areas: ["floor_1", "floor_1_east", "floor_2_south"]
unlocked_doors: ["door_12", "door_15"]
disabled_cameras: ["camera_1"]

[floor_1]
# Generated Office Layout - Floor 1
# Last visited: 2024-03-15 15:45:00
####################################
#          Zenith Corp             #
####################################
#WWWWWWWWWWWWWWWDWWWWW#############
#...................T..............#
#..=R=..............#.....OOOOOO..#
#..@...C...........D#.....OOOOOO..#
#...................#.....??????..#
#........G.........#.....??????..#
#...................#.............#
#..=................D............#
#WWWWWWWWW#D#WWWWWWW#............#
#.........#.#.......#....^.......#
#.........#.#.......#............#
####################################

[floor_1_entities]
# Current state of NPCs
R: CIVILIAN[id=civilian_23,transformed=true,type=CAT]
G: GUARD[id=guard_4,alert=true,last_seen_player=(12,5)]
T: CIVILIAN[id=civilian_45,transformed=true,type=DOG]

[floor_1_objects]
=: DESK[searched=true]
@: CHAIR
C: SECURITY_CAMERA[id=camera_1,disabled=true]

[floor_1_fog]
# ? represents unexplored areas
# O represents seen but not currently visible
# . represents currently visible
revealed_mask: """
111111111111111111111111111111111
111111111111111111111111111111111
111111111111111111111000000000111
111111111111111111111000000000111
111111111111111111111000000000111
111111111111111111111000000000111
111111111111111111111111111111111
"""

[floor_2]
# ? represents unexplored areas
####################################
#          Unknown Area            #
####################################
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#???????????????????????.........#
#.......??????????????????????...#
#.......??????????????????????...#
####################################

[scripted_events]
guard_4_alert: {
    trigger: "player_spotted"
    timestamp: "2024-03-15T15:44:30"
    state: "active"
    countdown: 120
}

[navigation_data]
entry_points: [(1,1), (15,1)]
known_shortcuts: ["vent_3", "maintenance_2"]
mapped_cameras: ["camera_1", "camera_2"]
guard_patterns: {
    "guard_4": [(8,3), (15,3), (15,8), (8,8)]
}
```

##### Save System Features
1. **State Tracking**
   - Transformed NPCs
   - Alert status
   - Discovered areas
   - Modified objects
   - Unlocked doors
   - Disabled systems

2. **Fog of War**
   - Unexplored areas (?)
   - Previously seen areas (O)
   - Currently visible areas (.)
   - Revealed secrets

3. **Entity Memory**
   - NPC transformations
   - Guard alert states
   - Patrol modifications
   - Last known positions

4. **Progress Markers**
   - Searched containers
   - Hacked systems
   - Collected items
   - Triggered events

##### Technical Implementation
1. **Save Format**
   - ASCII map representation
   - Binary state data
   - Compressed fog of war
   - Entity state deltas

2. **Update Triggers**
   - Room entry/exit
   - Major events
   - Time intervals
   - Manual saves

3. **Loading System**
   - Fast state reconstruction
   - Entity rehydration
   - Event continuation
   - Partial loading for adjacent areas

4. **Version Control**
   - Save format versioning
   - Migration support
   - Backwards compatibility
   - State verification

This system provides:
- Persistent world state
- Progress tracking
- Debugging support
- State rollback capability
- Memory-efficient storage

#### Generation Process
1. **Layout Planning**
   - Load building blueprints if static
   - Generate floor plans
   - Place mandatory rooms
   - Create corridors and stairwells

2. **Area Population**
   - Place required NPCs
   - Distribute random civilians
   - Add appropriate furniture
   - Set up security measures

3. **Connectivity**
   - Main entrances/exits
   - Emergency exits
   - Elevator placement
   - Maintenance areas

4. **Security Elements**
   - Security desk placement
   - Camera coverage
   - Guard patrol routes
   - Access card readers

#### Special Features

1. **Alert Levels**
   - Level 0: Unaware
   - Level 1: Suspicious Activity Reported
   - Level 2: Increased Security
   - Level 3: Active Search
   - Level 4: Lockdown

2. **Environmental Elements**
   - Crowds for cover
   - Security cameras
   - Public/Private areas
   - Restricted zones

3. **Navigation Features**
   - Multiple entry points
   - Service corridors
   - Emergency stairs
   - Elevator systems

4. **Interactive Elements**
   - Computers/Workstations
   - Security Systems
   - Vending Machines
   - Public Phones
   - Storage Units

#### Zone Connectivity
- **City Layout Model**
  - Downtown district
  - Residential areas
  - Industrial zones
  - Public spaces
  - Transport hubs

- **Building Connectivity**
  - Multiple floors
  - Parking structures
  - Underground tunnels
  - Rooftop access

#### Entity Placement Strategy
1. **Static Placement**
   - Security personnel
   - Key employees
   - Story-critical NPCs
   - Existing transformed allies

2. **Dynamic Placement**
   - Civilian routines
   - Security patrols
   - Visitor patterns
   - Maintenance staff

3. **Group Behaviors**
   - Office workers
   - Security teams
   - Maintenance crews
   - Social groups

#### Progression System
- **Area Unlocking**
  - Story progression
  - Reputation system
  - Security clearances
  - Contact networks

- **Difficulty Scaling**
  - Increased security
  - Civilian awareness
  - Camera coverage
  - Response teams

### Planned Features

### Immediate Todo
- UI System for Card Display and Management
  #### Visual Style Guidelines
  - **Overall Aesthetic**
    - Clean, minimalist interface inspired by modern roguelikes
    - High contrast color scheme for readability
    - Simple geometric shapes and borders
    - Text-forward design with minimal decorative elements
    - Consistent use of space and alignment
    
  #### Card Display Components
  - **Card Visual Template**
    - Compact, text-based design
    - Simple border style varying by rarity:
      - Common: Single line border
      - Uncommon: Double line border
      - Rare: Bold border
      - Legendary: Double bold border
    - Clear typography hierarchy:
      - Card name in bold
      - Stats in monospace font
      - Description in regular weight
    - Minimal use of color:
      - White text on dark background
      - Rarity colors as subtle highlights only
    - No card art - focus on clear information display

  #### Management Interfaces
  - **Hand Display**
    - Simple horizontal list at bottom of screen
    - Minimal visual elements:
      - Card number (1-5) clearly indicated
      - Current selection highlighted with inverse colors
      - Stack numbers in brackets [x3]
    - Status indicators:
      - Draw pile: Simple counter [D:15]
      - Discard pile: Simple counter [R:7]
    
  - **Deck Builder Interface**
    - Two-column layout with clear divider
    - Keyboard-friendly navigation
    - Simple list format:
      - One card per line
      - Quantity shown in brackets
      - Rarity indicated by subtle color prefix
    - Stats displayed as simple text footer:
      - "20/20 cards in deck"
      - "Common: 12 | Uncommon: 5 | Rare: 2 | Legendary: 1"
    
  - **Card Collection View**
    - Single-column scrollable list
    - Category headers in inverse colors
    - Simple filter indicators at top
    - Keyboard shortcuts shown in brackets [r]arity [t]ype [d]ate

  #### Interaction Systems
  - **Card Selection**
    - Keyboard-first navigation
    - Tab/arrow key movement between sections
    - Quick-select with number keys
    - Mouse support as secondary option
    
  - **Card Usage**
    - Clear targeting system:
      - Highlight potential targets
      - Show range with simple distance markers
      - Success chance displayed as percentage
    - Feedback through text notifications:
      - "Injector used successfully"
      - "Target resisted transformation"
      - "Duration: 45s remaining"


### Future Considerations
- Additional animal types
- Special abilities for transformed entities
- Card crafting system
- Reputation system based on transformations
- Quest system related to specific transformations

## Technical Architecture

### Core Components
- Card system (`Game/Content/Cards/`)
  - Base card definitions
  - Card factory for creating different types
  - Inventory management system
  - Deck management system
- UI system (`Game/UI/`)
  - Menu configurations
  - Card UI manager
  - Visual elements
  - Input handling

### Design Principles
1. Modular and extensible card system
2. Clear separation of concerns between systems
3. Type-safe implementations with proper error handling
4. Well-documented code with comprehensive comments

## Version History

### v0.1
- Initial implementation of card system
- Basic card types and effects
- Inventory management system
- Core animal transformations
- Card UI system and menus

---
*This document will be updated as new features are implemented and design decisions are made.*

#### Map Storage System

##### Map File Structure
```
# downtown_office_3.map
# Created: 2024-03-15 14:30
# Last Modified: 2024-03-15 15:45
# Type: OFFICE_BUILDING
# Alert Level: 2

[metadata]
name: Downtown Office Building
floors: 2
alert_level: 2
discovered: true

[state]
transformed: civilian_23, civilian_45
disabled_cameras: camera_1, camera_2
unlocked_doors: door_12, door_15

[floor_1]
####################################
#          Reception Area          #
####################################
#WWWWWWWWWWWWWWWDWWWWW#############
#...................T..............#
#..=R=..............#.....OOOOOO..#
#..@...C...........D#.....OOOOOO..#
#...................#.....??????..#
#........G.........#.....??????..#
#...................#.............#
#..=................D............#
#WWWWWWWWW#D#WWWWWWW#............#
#.........#.#.......#....^.......#
#.........#.#.......#............#
####################################

[floor_1_items]
R = CIVILIAN(transformed:CAT, id:civilian_23)
G = GUARD(alert:true)
T = CIVILIAN(transformed:DOG, id:civilian_45)
C = CAMERA(disabled:true, id:camera_1)
= = DESK
@ = CHAIR
? = UNEXPLORED
O = PREVIOUSLY_SEEN

[floor_2]
####################################
#         Executive Offices        #
####################################
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#????????????????????????OOOOOOOO#
#???????????????????????.........#
#.......??????????????????????...#
#.......??????????????????????...#
####################################

[floor_2_items]
? = UNEXPLORED
O = PREVIOUSLY_SEEN
```

##### Storage Strategy
1. **One File Per Map**
   - Simple text files with `.map` extension
   - Human-readable ASCII format
   - Clear section headers
   - Basic metadata

2. **File Organization**
   ```
   saves/
   ├── static/              # Pre-designed maps
   │   ├── police_hq.map
   │   ├── hospital.map
   │   └── school.map
   │
   ├── generated/           # Procedurally generated
   │   ├── office_1.map
   │   ├── house_2.map
   │   └── shop_3.map
   │
   └── templates/           # Generation templates
       ├── office.template
       ├── house.template
       └── shop.template
   ```

3. **Map Elements**
   - Walls (#)
   - Floors (.)
   - Doors (D)
   - Windows (W)
   - Stairs (^/v)
   - Entities (letters)
   - Items (symbols)

4. **State Tracking**
   - Simple lists in [state] section
   - Entity states in _items sections
   - Basic visibility tracking (?, O, .)

##### Benefits
1. **Development**
   - Easy to edit manually
   - Quick to debug
   - Version control friendly
   - Simple to parse

2. **Performance**
   - Fast to load/save
   - Small file sizes
   - No compression needed
   - Direct memory mapping

3. **Flexibility**
   - Easy to modify
   - Simple to extend
   - Clear structure
   - Human readable

##### Implementation Notes
1. **Loading**
```python
def load_map(path: str) -> GameMap:
    with open(path, 'r') as f:
        current_section = None
        map_data = {}
        
        for line in f:
            if line.startswith('['):
                current_section = line.strip('[]').strip()
                map_data[current_section] = []
            elif current_section:
                map_data[current_section].append(line.rstrip())
                
    return parse_map_data(map_data)
```

2. **Saving**
```python
def save_map(game_map: GameMap, path: str):
    with open(path, 'w') as f:
        # Write metadata
        f.write(f"# {game_map.name}\n")
        f.write(f"# Created: {game_map.created_at}\n")
        f.write(f"# Last Modified: {datetime.now()}\n\n")
        
        # Write state
        f.write("[metadata]\n")
        f.write(f"name: {game_map.name}\n")
        f.write(f"floors: {game_map.floors}\n\n")
        
        # Write each floor
        for floor in game_map.floors:
            f.write(f"[floor_{floor.number}]\n")
            f.write(floor.to_ascii())
            f.write("\n")
            
            f.write(f"[floor_{floor.number}_items]\n")
            f.write(floor.items_to_ascii())
            f.write("\n")
```

3. **Editing**
```python
def edit_map(path: str) -> None:
    """Simple terminal-based map editor."""
    map_data = load_map(path)
    
    while True:
        display_map(map_data)
        cmd = input("> ")
        
        if cmd == 'q':
            break
        elif cmd.startswith('e'):  # Edit mode
            handle_edit_mode(map_data)
        elif cmd.startswith('s'):  # Save
            save_map(map_data, path)
```