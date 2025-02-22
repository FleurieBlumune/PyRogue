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

## Planned Features

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