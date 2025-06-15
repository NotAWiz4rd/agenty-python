# The Shattered Realms RPG - Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Adding Content](#adding-content)
4. [Extending Systems](#extending-systems)
5. [Code Standards](#code-standards)
6. [Testing](#testing)
7. [Common Tasks](#common-tasks)

## Architecture Overview

### System Design
The game follows a modular architecture with clearly separated concerns:

```
rpg_project/
├── main.py                 # Entry point
├── game/                   # Core game systems
│   ├── game_engine.py     # Main game loop and coordination
│   ├── character.py       # Character classes and progression
│   ├── combat.py          # Turn-based combat system
│   ├── world.py           # World, locations, and environment
│   ├── inventory.py       # Items and equipment management
│   ├── quest.py           # Quest and objective system
│   ├── dialogue.py        # NPC conversations and branching dialogue
│   └── ui/                # User interface components
│       └── menu_system.py # Menu and UI handling
├── utils/                 # Utility systems
│   └── save_system.py     # Game state persistence
└── design/                # Design documents and lore
```

### Key Design Patterns

**Component-Entity System**: Characters and items are built from composable components

**Observer Pattern**: Quest system listens for game events to update progress

**State Machine**: Dialogue trees and game states use state machine patterns

**Template Method**: Items and characters use templates for consistent creation

## System Components

### Game Engine (`game_engine.py`)
Central coordinator that manages all other systems.

**Key Classes:**
- `GameState`: Manages global game state and flags
- `GameEngine`: Main game loop and system coordination

**Responsibilities:**
- Game loop management
- System integration
- Player input handling
- Save/load coordination

### Character System (`character.py`)
Handles player and NPC characters with progression.

**Key Classes:**
- `Character`: Base character with attributes and abilities
- `PlayerCharacter`: Player-specific features (titles, story flags, etc.)
- `NPC`: Non-player characters with AI and dialogue

**Key Features:**
- Attribute system (Strength, Dexterity, etc.)
- Experience and leveling
- Crystal attunement and corruption
- Equipment slots

### Combat System (`combat.py`)
Turn-based tactical combat with magic integration.

**Key Classes:**
- `CombatSystem`: Manages combat encounters
- `CombatAction`: Represents player/NPC actions
- `CombatResult`: Outcome of combat encounters

**Features:**
- Initiative-based turn order
- Attack, defend, magic, item, and flee actions
- Crystal magic integration
- AI decision making for NPCs

### World System (`world.py`)
Manages game world, locations, and environmental interactions.

**Key Classes:**
- `World`: Global world state and location management
- `Location`: Individual game locations with NPCs and items

**Features:**
- Location-based gameplay
- NPC placement and management
- Environmental storytelling
- Inter-location travel

### Inventory System (`inventory.py`)
Comprehensive item and equipment management.

**Key Classes:**
- `InventorySystem`: Central item management
- `Item`: Individual game items with stats and effects
- `Equipment`: Character equipment management

**Features:**
- Template-based item creation
- Equipment stats and bonuses
- Item usage and effects
- Inventory management

### Quest System (`quest.py`)
Event-driven quest and objective tracking.

**Key Classes:**
- `QuestSystem`: Central quest management
- `Quest`: Individual quests with objectives and rewards
- `QuestObjective`: Specific quest goals

**Features:**
- Objective tracking and completion
- Event-driven progress updates
- Quest prerequisites and branching
- Multiple quest types (main, side, faction)

### Dialogue System (`dialogue.py`)
Branching dialogue trees with conditional responses.

**Key Classes:**
- `DialogueSystem`: Manages all NPC conversations
- `DialogueTree`: Complete conversation tree for an NPC
- `DialogueNode`: Individual dialogue exchanges
- `DialogueOption`: Player response choices

**Features:**
- Conditional dialogue based on game state
- Dialogue effects (flags, items, quests)
- One-time and repeatable conversations
- NPC disposition tracking

## Adding Content

### Creating New Items
1. Add item template to `InventorySystem.create_item_templates()`
2. Define stats, effects, and requirements
3. Add to appropriate item creation methods

```python
# Example: Adding a new weapon
crystal_staff = Item("Crystal Staff", "weapon", "A staff infused with magical energy.")
crystal_staff.stats = {"attack": 6, "magic_power": 8}
crystal_staff.requirements = {"intelligence": 12}
crystal_staff.value = 150
self.item_templates["crystal_staff"] = crystal_staff
```

### Adding New Locations
1. Create location in `World.create_world()`
2. Set description, NPCs, items, and exits
3. Connect to existing locations

```python
# Example: Adding a new location
library = Location("ancient_library", "Ancient Library", 
                   "A vast library filled with dusty tomes and ancient knowledge.")
library.add_action("read books")
library.environmental_effects.append("The air hums with magical energy.")
self.locations[library.location_id] = library
```

### Creating New Quests
1. Add quest creation to `QuestSystem.create_quests()`
2. Define objectives, rewards, and prerequisites
3. Add event handlers if needed

```python
# Example: Adding a new quest
rescue_quest = Quest("rescue_scholar", "Rescue the Lost Scholar",
                     "A scholar has gone missing in the crystal caves.")
rescue_quest.add_objective(QuestObjective("find_scholar", ObjectiveType.TALK_TO,
                                         "Find the lost scholar", "Lost Scholar"))
rescue_quest.experience_reward = 100
self.add_quest(rescue_quest)
```

### Adding NPCs and Dialogue
1. Create NPC in location population methods
2. Add dialogue tree to `DialogueSystem.create_dialogue_trees()`
3. Define conversation nodes and options

```python
# Example: Adding NPC dialogue
def create_guard_dialogue(self):
    tree = DialogueTree("city_guard", "City Guard")
    
    start = DialogueNode("start", "npc", "Halt! What's your business here?")
    
    option1 = DialogueOption("explain", "I'm just passing through.", "let_pass")
    start.add_option(option1)
    
    self.dialogue_trees["City Guard"] = tree
```

## Extending Systems

### Adding New Magic Systems
1. Extend `CrystalType` enum in `character.py`
2. Add magic effects to `CombatSystem.process_magic()`
3. Create crystal items in inventory templates
4. Update corruption calculation if needed

### Adding Status Effects
1. Add status tracking to `Character` class
2. Extend combat system to apply/remove effects
3. Update turn processing for ongoing effects
4. Add UI indicators for active effects

### Implementing New Game Mechanics
1. Define data structures in appropriate system
2. Add processing logic to game loop
3. Create UI interactions
4. Add save/load support
5. Write tests for new functionality

## Code Standards

### Style Guidelines
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings for all classes and methods
- Keep functions focused and reasonably sized

### Documentation
- Document all public methods and classes
- Include type hints for function parameters and returns
- Add inline comments for complex logic
- Update design documents when adding major features

### Error Handling
- Use try-catch blocks for risky operations
- Provide meaningful error messages to players
- Log errors for debugging purposes
- Gracefully degrade when systems fail

### Testing
- Write unit tests for new functionality
- Test edge cases and error conditions
- Verify integration between systems
- Test save/load compatibility

## Testing

### Unit Testing
Create tests for individual system components:

```python
# Example test structure
def test_character_creation():
    player = PlayerCharacter("Test Hero")
    assert player.name == "Test Hero"
    assert player.level == 1
    assert player.current_health == player.max_health
```

### Integration Testing
Test system interactions:

```python
# Example integration test
def test_quest_progression():
    game_state = create_test_game_state()
    quest_system = QuestSystem()
    quest_system.start_quest("test_quest", game_state)
    quest_system.trigger_event(game_state, "item_collected", {"item_name": "test_item"})
    assert quest_system.get_quest("test_quest").status == QuestStatus.COMPLETED
```

### Manual Testing Checklist
- [ ] Character creation works correctly
- [ ] All movement between locations functions
- [ ] Combat system operates without errors
- [ ] Quest progression triggers properly
- [ ] Dialogue trees navigate correctly
- [ ] Save/load preserves game state
- [ ] Inventory management works as expected

## Common Tasks

### Adding a New Island
1. Design locations and connections in `world.py`
2. Create NPCs and populate locations
3. Add dialogue trees for new NPCs
4. Create island-specific quests
5. Add travel options from existing locations
6. Test all connections and interactions

### Balancing Combat
1. Adjust base damage values in combat system
2. Modify magic costs and effects
3. Update AI decision-making weights
4. Test against various character builds
5. Adjust experience and reward values

### Adding New Story Content
1. Design quest structure and objectives
2. Create supporting NPCs and dialogue
3. Add required items and locations
4. Implement quest-specific game flags
5. Test all story branches and outcomes

### Debugging Common Issues
- **Quest not progressing**: Check event trigger conditions
- **Dialogue not working**: Verify NPC names and tree registration
- **Save/load errors**: Check serialization of new data structures
- **Combat errors**: Verify character state and action validation

### Performance Optimization
- Profile game loop for bottlenecks
- Optimize frequent operations (combat, inventory)
- Cache expensive calculations
- Minimize file I/O operations
- Use efficient data structures for large collections

## Extension Points

### Plugin Architecture
The system is designed to support extensions:

- **New Systems**: Add alongside existing systems in `game/`
- **Custom Items**: Extend item templates and effects
- **Magic Schools**: Add new crystal types and effects
- **AI Behaviors**: Extend NPC decision making
- **World Events**: Add time-based or trigger-based events

### Modding Support
Consider these areas for future modding:

- External data files for items, quests, and dialogue
- Scripting system for complex interactions
- Asset replacement for descriptions and text
- Configuration files for game balance

---

*This developer guide covers the current architecture. As the game evolves, update this documentation to reflect new patterns and systems.*