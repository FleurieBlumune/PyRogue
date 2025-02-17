# PyRogue Design Document

## Game Overview
A roguelike game where the player uses serum injectors (represented as cards) to transform NPCs into various animals. The game combines deck-building mechanics with traditional roguelike elements.

## Core Systems

### Card System
The game uses a card-based inventory system where each card represents a serum injector that can transform entities into different animals.

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

## Planned Features

### Immediate Todo
- [ ] UI system for card display and management
- [ ] Implementation of transformation effects on entities
- [ ] Card acquisition mechanics
- [ ] Special card combinations and effects

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

---
*This document will be updated as new features are implemented and design decisions are made.* 