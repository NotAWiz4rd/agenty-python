# The Shattered Realms RPG - API Reference

## Table of Contents
1. [Character System](#character-system)
2. [Combat System](#combat-system)
3. [Inventory System](#inventory-system)
4. [Quest System](#quest-system)
5. [Dialogue System](#dialogue-system)
6. [World System](#world-system)
7. [Game Engine](#game-engine)
8. [Save System](#save-system)

## Character System

### Character Class
Base class for all characters in the game.

#### Constructor
```python
Character(name: str, level: int = 1)
```

#### Key Methods
```python
def add_experience(amount: int) -> None
def level_up() -> None
def attune_crystal(crystal_type: CrystalType, power: int) -> bool
def heal(amount: int) -> None
def take_damage(amount: int) -> None
def use_magic(amount: int) -> bool
def get_attribute_modifier(attribute: Attribute) -> int
def update_derived_stats() -> None
def is_alive() -> bool
def get_status() -> str
```

#### Properties
```python
name: str
level: int
experience: int
attributes: Dict[Attribute, int]
current_health: int
max_health: int
current_magic: int
max_magic: int
crystal_attunements: Dict[CrystalType, int]
corruption_level: int
inventory: List[Item]
equipment: Dict[str, Item]
```

### PlayerCharacter Class
Extends Character with player-specific features.

#### Additional Methods
```python
def distribute_attribute_points(points: int) -> None
def add_title(title: str) -> None
def modify_alignment(order: int = 0, chaos: int = 0, good: int = 0, evil: int = 0) -> None
def add_memory_fragment(fragment: dict) -> None
def set_story_flag(flag: str, value: bool = True) -> None
def get_story_flag(flag: str) -> bool
def get_character_sheet() -> str
```

### NPC Class
Extends Character for non-player characters.

#### Constructor
```python
NPC(name: str, npc_type: str, level: int = 1)
```

#### Methods
```python
def modify_disposition(change: int) -> None
def get_disposition_text() -> str
```

#### Properties
```python
npc_type: str
disposition: int
dialogue_state: str
services_offered: List[str]
```

## Combat System

### CombatSystem Class
Manages turn-based combat encounters.

#### Methods
```python
def start_combat(player: PlayerCharacter, enemies: List[Character]) -> CombatResult
def process_action(action: CombatAction) -> Dict[str, Any]
def get_health_bar(character: Character) -> str
```

### CombatAction Class
Represents an action in combat.

#### Constructor
```python
CombatAction(action_type: ActionType, actor: Character, 
             target: Optional[Character] = None, data: Dict[str, Any] = None)
```

### CombatResult Class
Contains the outcome of a combat encounter.

#### Properties
```python
victory: bool
participants: List[Character]
experience_gained: int
items_found: List[Item]
fled: bool
```

## Inventory System

### InventorySystem Class
Manages items and equipment throughout the game.

#### Methods
```python
def create_item(template_id: str, quantity: int = 1) -> Optional[Item]
def add_item(character: Character, item: Item) -> bool
def remove_item(character: Character, item: Item, quantity: int = 1) -> bool
def find_item(character: Character, item_name: str) -> Optional[Item]
def get_inventory_value(character: Character) -> int
def get_inventory_weight(character: Character) -> int
def transfer_item(from_character: Character, to_character: Character, 
                 item: Item, quantity: int = 1) -> bool
def drop_item(character: Character, item: Item, quantity: int = 1, 
             location: Location = None) -> bool
def pick_up_item(character: Character, item: Item, location: Location = None) -> bool
```

### Item Class
Represents an individual item.

#### Constructor
```python
Item(name: str, item_type: str, description: str, quantity: int = 1)
```

#### Methods
```python
def can_use(character: Character) -> bool
def use(character: Character, game_state = None) -> Dict[str, Any]
def get_info() -> str
```

#### Properties
```python
name: str
item_type: str
description: str
quantity: int
value: int
weight: int
stats: Dict[str, int]
effects: Dict[str, Any]
requirements: Dict[str, Any]
```

## Quest System

### QuestSystem Class
Manages all quests and objectives.

#### Methods
```python
def start_quest(quest_id: str, game_state: GameState) -> bool
def get_quest(quest_id: str) -> Optional[Quest]
def update_quest_progress(game_state: GameState, event_type: str, event_data: Dict[str, Any]) -> None
def trigger_event(game_state: GameState, event_type: str, event_data: Dict[str, Any]) -> None
def get_active_quests() -> List[Quest]
def get_completed_quests() -> List[Quest]
def get_available_quests(game_state: GameState) -> List[Quest]
def get_quest_log() -> str
```

### Quest Class
Represents an individual quest.

#### Constructor
```python
Quest(quest_id: str, title: str, description: str)
```

#### Methods
```python
def can_start(game_state: GameState) -> bool
def start_quest(game_state: GameState) -> bool
def add_objective(objective: QuestObjective) -> None
def update_progress(game_state: GameState, objective_id: str = None, amount: int = 1) -> None
def complete_quest(game_state: GameState) -> None
def fail_quest(game_state: GameState, reason: str = "") -> None
def get_status_text() -> str
```

### QuestObjective Class
Represents a quest objective.

#### Constructor
```python
QuestObjective(objective_id: str, objective_type: ObjectiveType, 
               description: str, target: str = "", quantity: int = 1)
```

#### Methods
```python
def update_progress(game_state: GameState, amount: int = 1) -> bool
def check_completion(game_state: GameState) -> bool
def get_progress_text() -> str
```

## Dialogue System

### DialogueSystem Class
Manages NPC conversations and dialogue trees.

#### Methods
```python
def start_conversation(npc: NPC, game_state: GameState) -> None
def end_conversation() -> None
def add_dialogue_tree(tree: DialogueTree) -> None
def get_dialogue_tree(npc_name: str) -> Optional[DialogueTree]
def create_simple_dialogue(npc_name: str, greeting: str, responses: List[str]) -> DialogueTree
```

### DialogueTree Class
Represents a complete conversation tree for an NPC.

#### Constructor
```python
DialogueTree(tree_id: str, npc_name: str)
```

#### Methods
```python
def add_node(node: DialogueNode) -> None
def get_node(node_id: str) -> Optional[DialogueNode]
def reset_conversation() -> None
def set_conversation_flag(flag: str, value: Any) -> None
def get_conversation_flag(flag: str, default: Any = False) -> Any
```

### DialogueNode Class
Represents a single dialogue exchange.

#### Constructor
```python
DialogueNode(node_id: str, speaker: str, text: str)
```

#### Methods
```python
def add_option(option: DialogueOption) -> None
def is_accessible(game_state: GameState) -> bool
def get_available_options(game_state: GameState) -> List[DialogueOption]
```

### DialogueOption Class
Represents a player dialogue choice.

#### Constructor
```python
DialogueOption(option_id: str, text: str, next_node: str = "")
```

#### Methods
```python
def add_condition(condition: DialogueCondition) -> None
def add_effect(effect: DialogueEffect) -> None
def is_available(game_state: GameState) -> bool
def choose(game_state: GameState, npc: NPC) -> None
```

## World System

### World Class
Manages the game world and all locations.

#### Methods
```python
def get_location(location_id: str) -> Optional[Location]
def set_global_flag(flag: str, value: Any) -> None
def get_global_flag(flag: str, default: Any = False) -> Any
def advance_world_time(hours: int = 1) -> None
def get_nearby_locations(location_id: str) -> List[str]
def can_travel_to(from_location: str, to_location: str) -> bool
```

### Location Class
Represents a game location.

#### Constructor
```python
Location(location_id: str, name: str, description: str)
```

#### Methods
```python
def add_exit(direction: str, destination: str) -> None
def add_npc(npc: NPC) -> None
def remove_npc(npc: NPC) -> None
def add_item(item: Item) -> None
def remove_item(item: Item) -> None
def add_action(action: str, handler: Optional[Callable] = None) -> None
def process_action(action: str, game_state: GameState) -> bool
def on_enter(game_state: GameState) -> None
def on_exit(game_state: GameState) -> None
```

#### Properties
```python
location_id: str
name: str
description: str
exits: Dict[str, str]
npcs: List[NPC]
items: List[Item]
available_actions: List[str]
```

## Game Engine

### GameEngine Class
Main game coordination and loop management.

#### Constructor
```python
GameEngine(save_system: SaveSystem)
```

#### Methods
```python
def start_new_game() -> None
def continue_game() -> None
def create_player_character() -> None
def initialize_world() -> None
def main_game_loop() -> None
def show_location_info() -> None
def process_action(action: str) -> None
def move_player(direction: str) -> None
def talk_to_npc(npc_name: str) -> None
def save_game() -> None
def handle_quit() -> None
```

### GameState Class
Manages global game state.

#### Methods
```python
def set_flag(flag: str, value: Any = True) -> None
def get_flag(flag: str, default: Any = False) -> Any
def advance_time() -> None
```

#### Properties
```python
player: Optional[PlayerCharacter]
current_location: Optional[Location]
world: Optional[World]
turn_count: int
game_flags: Dict[str, Any]
time_of_day: str
day_count: int
```

## Save System

### SaveSystem Class
Handles game state persistence.

#### Methods
```python
def save_game(game_state: GameState, filename: str = None) -> bool
def load_game(filename: str = None) -> bool
def quick_save(game_state: GameState) -> bool
def auto_save(game_state: GameState) -> bool
def serialize_game_state(game_state: GameState) -> Dict[str, Any]
def serialize_character(character: Character) -> Dict[str, Any]
def get_save_files() -> List[Dict[str, Any]]
def delete_save_file(filename: str) -> bool
def export_save(filename: str, export_path: str) -> bool
def import_save(import_path: str) -> bool
```

## Enums and Constants

### CrystalType
```python
class CrystalType(Enum):
    FLAME = "flame"
    FROST = "frost"
    LIFE = "life"
    SHADOW = "shadow"
    STORM = "storm"
    MIND = "mind"
```

### Attribute
```python
class Attribute(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
```

### ActionType
```python
class ActionType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    MAGIC = "magic"
    ITEM = "item"
    FLEE = "flee"
```

### QuestStatus
```python
class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
```

### ObjectiveType
```python
class ObjectiveType(Enum):
    KILL = "kill"
    COLLECT = "collect"
    TALK_TO = "talk_to"
    VISIT = "visit"
    DELIVER = "deliver"
    ESCORT = "escort"
    CUSTOM = "custom"
```

## Error Handling

Most methods return boolean success values or None for failures. Key exceptions:

- **FileNotFoundError**: Raised by save system when save files don't exist
- **ValueError**: Raised for invalid parameters
- **AttributeError**: Raised when accessing non-existent properties

## Usage Examples

### Creating a Character
```python
from game.character import PlayerCharacter, Attribute

player = PlayerCharacter("Hero")
player.attributes[Attribute.STRENGTH] = 15
player.update_derived_stats()
```

### Starting Combat
```python
from game.combat import CombatSystem
from game.character import NPC

combat = CombatSystem()
enemy = NPC("Goblin", "enemy", 1)
result = combat.start_combat(player, [enemy])
```

### Creating Items
```python
from game.inventory import InventorySystem

inventory = InventorySystem()
sword = inventory.create_item("iron_sword")
inventory.add_item(player, sword)
```

### Managing Quests
```python
from game.quest import QuestSystem

quest_system = QuestSystem()
quest_system.start_quest("prologue", game_state)
quest_system.trigger_event(game_state, "location_visited", {"location_id": "aethros_docks"})
```

---

*This API reference covers the current implementation. Check the source code for the most up-to-date method signatures and behavior.*