# The Shattered Realms RPG - Player Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Character Creation](#character-creation)
3. [Basic Gameplay](#basic-gameplay)
4. [Combat System](#combat-system)
5. [Crystal Magic](#crystal-magic)
6. [Inventory and Equipment](#inventory-and-equipment)
7. [Quests and Story](#quests-and-story)
8. [World Exploration](#world-exploration)
9. [NPCs and Dialogue](#npcs-and-dialogue)
10. [Tips and Strategies](#tips-and-strategies)

## Getting Started

### Installation and Running
1. Ensure you have Python 3.7+ installed
2. Navigate to the `rpg_project` directory
3. Run the game with: `python main.py`
4. Choose "New Game" from the main menu

### First Steps
- Create your character by choosing a name and background
- Read the prologue story to understand the world
- Explore Port Aethros to get familiar with the interface
- Talk to NPCs to learn about the world and start quests

## Character Creation

### Backgrounds
Choose from four distinct backgrounds that affect your starting stats and equipment:

**Scholar** 
- +2 Intelligence, +1 Wisdom
- Starts with Scholar's Robes, Crystal Analysis Kit, and Ancient Map Fragment
- Bonus: +2 Harmony Crystal Knowledge

**Warrior**
- +2 Strength, +1 Constitution  
- Starts with Iron Sword, Leather Armor, and Shield
- Ideal for combat-focused gameplay

**Diplomat**
- +2 Charisma, +1 Wisdom
- Starts with Fine Clothes, Signet Ring, and Letter of Introduction
- Excels at social interactions and quest negotiations

**Survivor**
- +1 Constitution, +1 Dexterity
- Starts with Survival Knife, Patched Cloak, and Emergency Supplies
- Balanced approach with practical skills

### Character Attributes
- **Strength**: Affects attack damage and carrying capacity
- **Dexterity**: Affects accuracy, defense, and initiative in combat
- **Constitution**: Affects health and resistance to corruption
- **Intelligence**: Affects magic power and learning ability
- **Wisdom**: Affects magic points and reduces corruption risk
- **Charisma**: Affects social interactions and NPC relations

## Basic Gameplay

### Interface Commands
- **look**: Examine your current location
- **inventory**: View your items
- **character**: View your character sheet
- **quests**: View active and completed quests
- **rest**: Recover health and magic (advances time)
- **save**: Save your game progress
- **help**: Show available actions

### Movement
- **go [direction]**: Move in specified direction (north, south, east, west, up, down)
- **board ship to [destination]**: Travel between islands

### Interaction
- **talk [npc name]**: Start conversation with an NPC
- **use [item]**: Use a consumable item
- **equip [item]**: Equip weapons, armor, or accessories
- **drop [item]**: Drop items at your current location

## Combat System

### Combat Basics
Combat is turn-based with initiative determined by Dexterity. Each turn you can:

1. **Attack**: Basic melee attack using equipped weapon
2. **Defend**: Defensive stance that recovers magic points
3. **Use Magic**: Cast crystal-based spells
4. **Use Item**: Consume potions or other items
5. **Flee**: Attempt to escape combat

### Combat Statistics
- **Health**: When reduced to 0, you are defeated
- **Magic Points**: Required for casting spells
- **Corruption**: Accumulated from risky crystal magic use

### Victory and Defeat
- **Victory**: Gain experience points and potential item rewards
- **Defeat**: Return to a safe location (implementation varies)
- **Fleeing**: Successfully escape but gain no rewards

## Crystal Magic

### Crystal Types
Six types of crystals provide different magical effects:

- **Flame**: High damage fire magic
- **Frost**: Moderate damage with potential slow effects
- **Life**: Healing magic for you and allies
- **Shadow**: Moderate damage with fear effects
- **Storm**: High damage lightning magic with stun potential
- **Mind**: Utility magic for buffs and mental effects

### Attunement System
- Attune to crystals to unlock magical abilities
- Higher attunement levels increase spell power
- Risk of corruption increases with power level and multiple attunements

### Corruption
- Accumulated from failed attunements or excessive crystal use
- High corruption can lead to negative effects
- Managed through careful crystal use and certain items/abilities

## Inventory and Equipment

### Inventory Management
- Limited inventory space (20 items by default)
- Items stack by type and name
- Sort by name, type, value, or quantity
- Drop items to make space

### Equipment Slots
- **Weapon**: Primary melee weapon
- **Armor**: Defensive gear
- **Accessory**: Rings, amulets, and other special items
- **Crystal Focus**: Enhances magical abilities

### Item Types
- **Weapons**: Swords, knives, and other combat gear
- **Armor**: Protective clothing and gear
- **Consumables**: Potions, food, and single-use items
- **Crystals**: Magical crystals for attunement
- **Quest Items**: Story-important items
- **Materials**: Crafting components and trade goods

## Quests and Story

### Quest Types
- **Main Quests**: Primary story progression
- **Side Quests**: Optional adventures with rewards
- **Faction Quests**: Missions for specific organizations

### Quest Tracking
- View active quests with the "quests" command
- Objectives update automatically as you progress
- Completed quests are tracked for reference

### Story Progression
- Your choices affect the story and available options
- Build relationships with NPCs and factions
- Discover the mystery of the Harmony Crystals
- Multiple paths and endings based on your decisions

## World Exploration

### Major Locations

**Port Aethros** - Trading Hub
- Neutral territory with merchants and travelers
- Harbor Master provides ship passage
- Taverns and markets for supplies and information

**Verdant Isle** - Living Island
- Nature-focused magic and druid culture
- Grove of Whispers with ancient wisdom
- Life crystal deposits and natural mazes

**Crystalline Peaks** - Mining Colony
- Rich crystal deposits and mining operations
- Dangerous but profitable crystal harvesting
- Advanced crystal refining techniques

**Shadowmere** - Mysterious Island
- Dark magic and ancient knowledge
- Whispering Library with forbidden texts
- Shadow crystal formations and memory magic

**The Void** - Between Islands
- Dangerous void crossings between islands
- Fragment collection and void navigation
- Unpredictable magical phenomena

### Travel
- Book passage between islands at docks
- Each island has unique challenges and opportunities
- Travel time advances the game clock

## NPCs and Dialogue

### Conversation System
- Multiple dialogue options affect story outcomes
- NPC disposition affects available options
- Some dialogue choices are one-time only

### Important NPCs
- **Harbor Master Jorik**: Provides information and travel arrangements
- **Mara the Tavern Keeper**: Offers food, rooms, and local rumors
- **Various Merchants**: Trade goods and rare items
- **Faction Representatives**: Offer special quests and rewards

### Relationship Building
- NPC disposition ranges from Hostile to Friendly
- Positive relationships unlock new dialogue options
- Some quests require good relationships with specific NPCs

## Tips and Strategies

### Character Development
- Specialize in a few crystal types rather than spreading too thin
- Balance combat and magic abilities based on your background
- Plan attribute increases during level-ups carefully

### Combat Strategy
- Use magic strategically - it's powerful but limited by magic points
- Defensive actions can be valuable for magic recovery
- Consider the corruption risk when using powerful magic

### Exploration
- Talk to everyone to discover quests and lore
- Rest regularly to maintain health and magic
- Save frequently, especially before dangerous activities

### Resource Management
- Manage inventory space carefully
- Stock up on consumables before long journeys
- Balance equipment upgrades with inventory space

### Story Choices
- Consider the long-term consequences of your decisions
- Build relationships with multiple factions when possible
- Some quests have time-sensitive elements

## Troubleshooting

### Common Issues
- **Game crashes**: Save frequently and report bugs
- **Missing items**: Check if items were consumed or dropped
- **Stuck in conversation**: Look for dialogue options or report bugs
- **Quest not progressing**: Ensure you've met all requirements

### Getting Help
- Use the "help" command for available actions
- Check quest log for objective details
- Talk to NPCs for hints and guidance
- Consult this guide for game mechanics

---

*The Shattered Realms RPG is a work in progress. Features and mechanics may change in future updates. Enjoy your adventure!*