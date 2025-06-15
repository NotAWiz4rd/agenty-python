# The Shattered Realms RPG

A comprehensive text-based role-playing game set in a post-apocalyptic fantasy world where reality itself was shattered into floating islands.

## Overview

The Shattered Realms is a feature-rich RPG that demonstrates advanced game development concepts including:
- Modular system architecture
- Complex character progression
- Turn-based tactical combat
- Dynamic quest system
- Branching dialogue trees
- Crystal-based magic system
- Comprehensive save/load functionality

## Features

### 🎭 Character System
- **Multi-background Character Creation**: Choose from Scholar, Warrior, Diplomat, or Survivor
- **Six-Attribute System**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- **Experience and Leveling**: Gain levels and distribute attribute points
- **Crystal Attunement**: Master different types of magical crystals
- **Corruption Mechanics**: Risk vs. reward magic system

### ⚔️ Combat System
- **Turn-Based Tactical Combat**: Initiative-based turn order
- **Multiple Actions**: Attack, defend, cast magic, use items, or flee
- **Crystal Magic Integration**: Six types of magical crystals with unique effects
- **AI-Driven Enemies**: NPCs with intelligent combat behavior
- **Experience Rewards**: Character progression through combat

### 🎒 Inventory & Equipment
- **Comprehensive Item System**: Weapons, armor, consumables, crystals, and quest items
- **Equipment Slots**: Weapon, armor, accessory, and crystal focus
- **Item Templates**: Consistent item creation and management
- **Weight and Capacity**: Realistic inventory limitations
- **Item Effects**: Stats, bonuses, and special abilities

### 📜 Quest System
- **Multiple Quest Types**: Main story, side quests, and faction missions
- **Objective Tracking**: Automatic progress updates
- **Event-Driven Updates**: Quests respond to player actions
- **Quest Prerequisites**: Structured story progression
- **Rewards System**: Experience, items, and reputation

### 💬 Dialogue System
- **Branching Conversations**: Complex dialogue trees with multiple outcomes
- **Conditional Responses**: Options based on attributes, items, and story flags
- **Consequence System**: Dialogue choices affect story and relationships
- **NPC Disposition**: Relationship tracking with all characters
- **One-Time Events**: Special dialogue options and story moments

### 🌍 World System
- **Multiple Islands**: Explore Aethros, Verdant Isle, Crystalline Peaks, and Shadowmere
- **Rich Lore**: Deep world-building with consistent internal logic
- **Environmental Storytelling**: Locations tell stories through description
- **Inter-Island Travel**: Ship-based travel between major locations
- **Dynamic World State**: Time progression and world events

### 💾 Save System
- **Complete State Persistence**: Save all game progress
- **Multiple Save Slots**: Manage multiple playthroughs
- **Auto-Save Functionality**: Automatic progress protection
- **Save File Management**: Export, import, and organize saves
- **Version Compatibility**: Forward-compatible save format

## Getting Started

### Requirements
- Python 3.7 or higher
- No external dependencies required

### Installation
1. Clone or download the project
2. Navigate to the `rpg_project` directory
3. Run the game: `python main.py`

### First Steps
1. Create your character and choose a background
2. Read the prologue to understand the world
3. Explore Port Aethros and talk to NPCs
4. Check your quest log to see available objectives
5. Visit different islands to discover new content

## Documentation

- **[Player Guide](PLAYER_GUIDE.md)**: Complete gameplay instructions and strategies
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Architecture overview and extension guidelines
- **[API Reference](API_REFERENCE.md)**: Detailed technical documentation

## Project Structure

```
rpg_project/
├── main.py                    # Game entry point
├── game/                      # Core game systems
│   ├── game_engine.py        # Main game coordination
│   ├── character.py          # Character classes and progression
│   ├── combat.py             # Turn-based combat system
│   ├── world.py              # World and location management
│   ├── inventory.py          # Item and equipment system
│   ├── quest.py              # Quest and objective tracking
│   ├── dialogue.py           # NPC conversation system
│   └── ui/                   # User interface components
│       └── menu_system.py    # Menu and UI handling
├── utils/                    # Utility systems
│   └── save_system.py        # Game state persistence
├── design/                   # Design documents and lore
│   ├── design_overview.md    # Project design summary
│   ├── world_design.md       # World-building and lore
│   ├── narrative_structure.md # Story structure and quests
│   └── characters_and_lore.md # Character backgrounds and culture
├── tests/                    # Testing framework
│   └── test_suite.py         # Comprehensive test suite
└── docs/                     # Documentation
    ├── PLAYER_GUIDE.md       # Player documentation
    ├── DEVELOPER_GUIDE.md    # Developer documentation
    └── API_REFERENCE.md      # Technical API reference
```

## Testing

Run the comprehensive test suite:
```bash
python tests/test_suite.py
```

The test suite covers:
- Character creation and progression
- Combat mechanics
- Inventory management
- Quest system functionality
- Dialogue tree navigation
- World state management
- Save/load operations
- System integration

## Design Philosophy

### Modularity
Each system is designed as an independent module with clear interfaces, making the codebase maintainable and extensible.

### Emergent Complexity
Simple systems interact to create complex gameplay experiences, such as how the crystal magic system affects both combat and character progression.

### Player Agency
Multiple solutions exist for most challenges, allowing players to approach problems based on their character build and preferences.

### Narrative Integration
Game mechanics reinforce story themes, such as the corruption system reflecting the world's magical instability.

## Key Systems Overview

### Crystal Magic System
The core magical system revolves around six types of crystals:
- **Flame**: Destructive fire magic
- **Frost**: Ice magic with control effects
- **Life**: Healing and nature magic
- **Shadow**: Dark magic and mental effects
- **Storm**: Lightning magic with stunning power
- **Mind**: Utility and enhancement magic

Players can attune to multiple crystal types but risk magical corruption, creating meaningful risk/reward decisions.

### Reputation and Relationships
Character interactions affect long-term story progression through:
- Individual NPC disposition tracking
- Faction reputation systems
- Story flags that unlock new content
- Multiple ending possibilities

## Contributing

### For Developers
1. Read the [Developer Guide](DEVELOPER_GUIDE.md) for architecture overview
2. Check the [API Reference](API_REFERENCE.md) for implementation details
3. Run the test suite before making changes
4. Follow the established code style and patterns

### For Content Creators
1. New quests can be added to the quest system
2. Dialogue trees can be expanded or modified
3. Items and equipment can be easily added
4. Locations and world content are extensible

## Technical Highlights

### Event-Driven Architecture
The quest system uses an event-driven approach where player actions automatically trigger quest progress updates.

### Template-Based Content Creation
Items, characters, and locations use template systems for consistent and easy content creation.

### State Machine Implementation
Dialogue trees and game states use state machine patterns for reliable navigation and management.

### Comprehensive Error Handling
Robust error handling ensures the game continues running even when subsystems encounter issues.

## Performance Considerations

- **Memory Efficient**: Minimal memory footprint with efficient data structures
- **Save File Optimization**: JSON-based saves balance readability and file size
- **Responsive Interface**: Fast response times for all player actions
- **Scalable Architecture**: Systems designed to handle content expansion

## Future Expansion Possibilities

### Planned Features
- Enhanced AI behaviors for NPCs
- Expanded crystal magic combinations
- Additional islands and locations
- Character skill trees
- Crafting system
- Party-based gameplay

### Modding Support
The modular architecture supports future modding capabilities:
- External data files for content
- Scripting system for complex interactions
- Plugin architecture for new systems
- Configuration files for game balance

## License

This project was created as a demonstration of AI-driven game development and creative writing capabilities.

## Acknowledgments

Created through AI collaboration to demonstrate:
- Complex system design and implementation
- Creative world-building and narrative design
- Comprehensive documentation practices
- Test-driven development approaches
- Modular software architecture

---

**Version**: 1.0  
**Status**: Complete and playable  
**Last Updated**: December 2024

*Explore the Shattered Realms and discover the secrets of the crystal magic that broke the world... and might just save it.*