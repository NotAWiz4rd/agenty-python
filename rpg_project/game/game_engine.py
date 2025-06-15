"""
Game Engine for The Shattered Realms RPG.

Manages the main game loop, state transitions, and system integration.
"""

import random
from typing import Dict, List, Optional, Any
from game.character import PlayerCharacter, NPC, CrystalType, Attribute
from game.combat import CombatSystem
from game.world import World, Location
from game.inventory import InventorySystem, Item
from game.quest import QuestSystem
from game.dialogue import DialogueSystem


class GameState:
    """Manages the overall game state."""
    
    def __init__(self):
        self.player: Optional[PlayerCharacter] = None
        self.current_location: Optional[Location] = None
        self.world: Optional[World] = None
        self.turn_count = 0
        self.game_flags = {}
        self.active_npcs = {}
        self.time_of_day = "morning"
        self.day_count = 1
    
    def set_flag(self, flag: str, value: Any = True):
        """Set a game flag."""
        self.game_flags[flag] = value
    
    def get_flag(self, flag: str, default: Any = False) -> Any:
        """Get a game flag."""
        return self.game_flags.get(flag, default)
    
    def advance_time(self):
        """Advance game time."""
        time_progression = ["morning", "afternoon", "evening", "night"]
        current_index = time_progression.index(self.time_of_day)
        
        if current_index == len(time_progression) - 1:
            self.time_of_day = time_progression[0]
            self.day_count += 1
        else:
            self.time_of_day = time_progression[current_index + 1]
        
        self.turn_count += 1


class GameEngine:
    """Main game engine that coordinates all systems."""
    
    def __init__(self, save_system):
        self.save_system = save_system
        self.game_state = GameState()
        
        # Initialize game systems
        self.combat_system = CombatSystem()
        self.inventory_system = InventorySystem()
        self.quest_system = QuestSystem()
        self.dialogue_system = DialogueSystem()
        
        # Game systems will be initialized when world is created
        self.world: Optional[World] = None
        
        # Game running flag
        self.running = False
    
    def start_new_game(self):
        """Start a new game."""
        print("\n" + "=" * 50)
        print("STARTING NEW GAME")
        print("=" * 50)
        
        # Create player character
        self.create_player_character()
        
        # Initialize world
        self.initialize_world()
        
        # Set starting location
        starting_location = self.world.get_location("aethros_docks")
        self.game_state.current_location = starting_location
        
        # Set initial game flags
        self.game_state.set_flag("game_started", True)
        self.game_state.set_flag("prologue_complete", False)
        
        # Initialize quest system with starting quests
        self.quest_system.auto_start_quests(self.game_state)
        
        # Start main game loop
        self.show_prologue()
        self.main_game_loop()
    
    def continue_game(self):
        """Continue a loaded game."""
        print("\n" + "=" * 50)
        print("CONTINUING GAME")
        print("=" * 50)
        
        # Game state should be loaded by save system
        self.running = True
        self.main_game_loop()
    
    def create_player_character(self):
        """Create the player character through character creation."""
        print("\n--- CHARACTER CREATION ---")
        print("You are a Resonance Walker, one of the few who can safely attune")
        print("to multiple crystal types without immediate corruption.")
        print()
        
        # Get player name
        while True:
            name = input("What is your name? ").strip()
            if name:
                break
            print("Please enter a valid name.")
        
        # Create player character
        player = PlayerCharacter(name)
        
        # Choose starting background
        print(f"\nWelcome, {name}. Choose your background:")
        print("1. Scholar - Starts with higher Intelligence and lore knowledge")
        print("2. Warrior - Starts with higher Strength and combat skills")
        print("3. Diplomat - Starts with higher Charisma and social connections")
        print("4. Survivor - Balanced stats with practical skills")
        
        while True:
            try:
                choice = int(input("Choose your background (1-4): "))
                if 1 <= choice <= 4:
                    break
                print("Please choose a number between 1 and 4.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Apply background bonuses
        if choice == 1:  # Scholar
            player.attributes[Attribute.INTELLIGENCE] += 2
            player.attributes[Attribute.WISDOM] += 1
            player.add_title("The Scholar")
            player.harmony_crystal_knowledge = 2
        elif choice == 2:  # Warrior
            player.attributes[Attribute.STRENGTH] += 2
            player.attributes[Attribute.CONSTITUTION] += 1
            player.add_title("The Warrior")
        elif choice == 3:  # Diplomat
            player.attributes[Attribute.CHARISMA] += 2
            player.attributes[Attribute.WISDOM] += 1
            player.add_title("The Diplomat")
        else:  # Survivor
            player.attributes[Attribute.CONSTITUTION] += 1
            player.attributes[Attribute.DEXTERITY] += 1
            player.add_title("The Survivor")
        
        # Update derived stats
        player.update_derived_stats()
        
        # Assign to game state
        self.game_state.player = player
        
        # Give starting equipment based on background
        self.give_starting_equipment(choice)
        
        print(f"\nCharacter created successfully!")
        print(f"Name: {player.name}")
        print(f"Title: {player.get_primary_title()}")
        print("Press Enter to continue...")
        input()
    
    def give_starting_equipment(self, background_choice: int):
        """Give starting equipment based on chosen background."""
        player = self.game_state.player
        
        # Common starting items
        common_item_ids = [
            "travel_pack",
            "basic_rations", 
            "water_flask",
            "flint_steel",
        ]
        
        # Background-specific items
        if background_choice == 1:  # Scholar
            specific_item_ids = [
                "scholars_robes",
                "crystal_analysis_kit",
                "ancient_map",
            ]
        elif background_choice == 2:  # Warrior
            specific_item_ids = [
                "iron_sword",
                "leather_armor",
                "shield",
            ]
        elif background_choice == 3:  # Diplomat
            specific_item_ids = [
                "fine_clothes",
                "signet_ring",
                "letter_intro",
            ]
        else:  # Survivor
            specific_item_ids = [
                "survival_knife",
                "patched_cloak",
                "emergency_supplies",
            ]
        
        # Add items to inventory using inventory system
        all_item_ids = common_item_ids + specific_item_ids
        for item_id in all_item_ids:
            item = self.inventory_system.create_item(item_id)
            if item:
                self.inventory_system.add_item(player, item)
            else:
                print(f"Warning: Could not create item {item_id}")
    
    def initialize_world(self):
        """Initialize the game world."""
        self.world = World()
        self.game_state.world = self.world
        
        # Register systems with world
        self.world.combat_system = self.combat_system
        self.world.inventory_system = self.inventory_system
        self.world.quest_system = self.quest_system
        self.world.dialogue_system = self.dialogue_system
    
    def show_prologue(self):
        """Show the game's opening story."""
        print("\n" + "=" * 60)
        print("                    PROLOGUE")
        print("=" * 60)
        print()
        
        prologue_text = [
            "The world ended not with fire or flood, but with a single moment",
            "of crystalline harmony gone wrong. The Great Sundering shattered",
            "reality itself, leaving the world as floating islands suspended",
            "in an endless void of swirling energies.",
            "",
            "That was three hundred years ago. Now, the scattered remnants",
            "of civilization cling to these Sky Islands, each one a fragment",
            "of what once was. Between them, the Void churns with chaotic",
            "magic and the dreams of the sleeping earth.",
            "",
            "You are a Resonance Walker, one of the rare few who can safely",
            "channel multiple types of crystal magic. Your kind are both",
            "feared and revered, for you alone might hold the key to",
            "restoring the shattered world... or destroying what remains.",
            "",
            "Your ship has just docked at Port Aethros, the last free",
            "trading hub in the known realms. Whatever brought you here,",
            "there's no turning back now. The winds of change are stirring,",
            "and fate has marked you as its instrument.",
        ]
        
        for line in prologue_text:
            print(line)
            if line:  # Don't pause on empty lines
                input("  [Press Enter to continue...]")
            else:
                print()
        
        print("\n" + "=" * 60)
        print("Your adventure begins...")
        print("=" * 60)
        input("\nPress Enter to start your journey...")
        
        self.game_state.set_flag("prologue_complete", True)
    
    def main_game_loop(self):
        """Main game loop."""
        self.running = True
        
        while self.running:
            try:
                # Show current location
                self.show_location_info()
                
                # Show available actions
                actions = self.get_available_actions()
                choice = self.get_player_choice(actions)
                
                # Process action
                self.process_action(choice)
                
                # Check for random events
                if random.randint(1, 20) == 1:
                    self.trigger_random_event()
                
                # Auto-save periodically
                if self.game_state.turn_count % 10 == 0:
                    self.save_system.auto_save(self.game_state)
                
            except KeyboardInterrupt:
                self.handle_quit()
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("The game will continue, but you may want to save.")
    
    def show_location_info(self):
        """Show information about the current location."""
        location = self.game_state.current_location
        player = self.game_state.player
        
        print("\n" + "=" * 60)
        print(f"LOCATION: {location.name}")
        print("=" * 60)
        print(location.description)
        
        # Show NPCs present
        if location.npcs:
            print(f"\nPeople here: {', '.join([npc.name for npc in location.npcs])}")
        
        # Show exits
        if location.exits:
            print(f"Exits: {', '.join(location.exits.keys())}")
        
        # Show player status
        print(f"\n{player.name} - {player.get_status()}")
        print(f"Health: {player.current_health}/{player.max_health} | "
              f"Magic: {player.current_magic}/{player.max_magic}")
        
        if player.corruption_level > 0:
            print(f"Corruption: {player.corruption_level}/{player.max_corruption}")
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions at current location."""
        actions = ["look", "inventory", "character", "rest"]
        
        location = self.game_state.current_location
        
        # Add movement options
        if location.exits:
            actions.extend([f"go {direction}" for direction in location.exits.keys()])
        
        # Add NPC interactions
        if location.npcs:
            actions.extend([f"talk {npc.name.lower()}" for npc in location.npcs])
        
        # Add location-specific actions
        actions.extend(location.available_actions)
        
        # Add system actions
        actions.extend(["quests", "save", "quit"])
        
        # Add item actions if player has items
        if self.game_state.player.inventory:
            actions.append("use [item]")
            actions.append("equip [item]")
            actions.append("drop [item]")
        
        return actions
    
    def get_player_choice(self, actions: List[str]) -> str:
        """Get and validate player choice."""
        print(f"\nTime: {self.game_state.time_of_day.title()}, Day {self.game_state.day_count}")
        print("What would you like to do?")
        
        # Show some common actions
        common_actions = ["look", "inventory", "character", "rest"]
        print("Common: " + " | ".join(common_actions))
        
        # Show movement options
        location = self.game_state.current_location
        if location.exits:
            print("Go: " + " | ".join([f"go {direction}" for direction in location.exits.keys()]))
        
        print("Type 'help' for all available actions.")
        print()
        
        while True:
            choice = input("> ").strip().lower()
            
            if choice == "help":
                print("Available actions:")
                for action in sorted(actions):
                    print(f"  {action}")
                continue
            
            # Check if choice is valid (allow partial matches for some commands)
            if choice in actions:
                return choice
            
            # Check for partial matches
            matches = [action for action in actions if action.startswith(choice)]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"Ambiguous command. Did you mean: {', '.join(matches)}")
                continue
            
            print("Invalid action. Type 'help' for available actions.")
    
    def process_action(self, action: str):
        """Process the chosen action."""
        if action == "look":
            self.show_location_info()
        elif action == "inventory":
            self.show_inventory()
        elif action == "character":
            self.show_character_sheet()
        elif action == "rest":
            self.rest_action()
        elif action.startswith("go "):
            direction = action[3:]
            self.move_player(direction)
        elif action.startswith("talk "):
            npc_name = action[5:]
            self.talk_to_npc(npc_name)
        elif action == "quests":
            self.show_quest_log()
        elif action.startswith("use "):
            item_name = action[4:]
            self.use_item(item_name)
        elif action.startswith("equip "):
            item_name = action[6:]
            self.equip_item(item_name)
        elif action.startswith("drop "):
            item_name = action[5:]
            self.drop_item(item_name)
        elif action == "save":
            self.save_game()
        elif action == "quit":
            self.handle_quit()
        else:
            # Try location-specific actions
            location = self.game_state.current_location
            if hasattr(location, 'process_action'):
                if not location.process_action(action, self.game_state):
                    print("You can't do that here.")
            else:
                print("You can't do that here.")
    
    def show_inventory(self):
        """Show player inventory."""
        player = self.game_state.player
        print(f"\n=== {player.name}'s INVENTORY ===")
        
        if not player.inventory:
            print("Your inventory is empty.")
        else:
            for item in player.inventory:
                print(f"- {item.name} x{item.quantity}")
                if item.description:
                    print(f"  {item.description}")
        
        print(f"\nCapacity: {len(player.inventory)}/{player.max_inventory}")
        input("\nPress Enter to continue...")
    
    def show_character_sheet(self):
        """Show player character sheet."""
        player = self.game_state.player
        print(player.get_character_sheet())
        input("\nPress Enter to continue...")
    
    def rest_action(self):
        """Handle rest action."""
        player = self.game_state.player
        
        print("\nYou take some time to rest and recover...")
        
        # Restore some health and magic
        health_restored = min(5, player.max_health - player.current_health)
        magic_restored = min(3, player.max_magic - player.current_magic)
        
        player.heal(health_restored)
        player.restore_magic(magic_restored)
        
        # Advance time
        self.game_state.advance_time()
        
        print(f"Health restored: {health_restored}")
        print(f"Magic restored: {magic_restored}")
        print(f"Time advances to {self.game_state.time_of_day}")
        
        input("\nPress Enter to continue...")
    
    def move_player(self, direction: str):
        """Move player in specified direction."""
        location = self.game_state.current_location
        
        if direction not in location.exits:
            print(f"You can't go {direction} from here.")
            return
        
        new_location_id = location.exits[direction]
        new_location = self.world.get_location(new_location_id)
        
        if new_location:
            print(f"\nYou travel {direction}...")
            self.game_state.current_location = new_location
            self.game_state.advance_time()
            
            # Trigger quest events
            self.quest_system.trigger_event(self.game_state, "location_visited", 
                                          {"location_id": new_location_id})
            
            # Trigger location events
            if hasattr(new_location, 'on_enter'):
                new_location.on_enter(self.game_state)
        else:
            print(f"You can't go {direction} right now.")
    
    def talk_to_npc(self, npc_name: str):
        """Initiate conversation with NPC."""
        location = self.game_state.current_location
        
        # Find NPC
        npc = None
        for n in location.npcs:
            if n.name.lower() == npc_name or npc_name in n.name.lower():
                npc = n
                break
        
        if not npc:
            print(f"There's no one here named '{npc_name}'.")
            return
        
        # Trigger quest events
        self.quest_system.trigger_event(self.game_state, "talked_to_npc", 
                                      {"npc_name": npc.name})
        
        # Start dialogue
        self.dialogue_system.start_conversation(npc, self.game_state)
    
    def save_game(self):
        """Save the current game."""
        if self.save_system.save_game(self.game_state):
            print("Game saved successfully.")
        else:
            print("Failed to save game.")
        input("Press Enter to continue...")
    
    def handle_quit(self):
        """Handle quit action."""
        print("\nAre you sure you want to quit?")
        print("1. Save and quit")
        print("2. Quit without saving")
        print("3. Cancel")
        
        while True:
            try:
                choice = int(input("Choose (1-3): "))
                if choice == 1:
                    if self.save_system.save_game(self.game_state):
                        print("Game saved. Goodbye!")
                    else:
                        print("Failed to save, but quitting anyway.")
                    self.running = False
                    break
                elif choice == 2:
                    print("Goodbye!")
                    self.running = False
                    break
                elif choice == 3:
                    print("Continuing game...")
                    break
                else:
                    print("Please choose 1, 2, or 3.")
            except ValueError:
                print("Please enter a valid number.")
    
    def trigger_random_event(self):
        """Trigger a random event."""
        events = [
            "A gentle breeze carries the scent of distant crystals.",
            "You hear the distant sound of sky-ship engines.",
            "A small crystal fragment glints in the light nearby.",
            "The void energies seem to shimmer more brightly.",
            "You feel a brief tingling of magical resonance.",
        ]
        
        event = random.choice(events)
        print(f"\n[Random Event] {event}")
        input("Press Enter to continue...")
    
    def show_quest_log(self):
        """Show the quest log."""
        print(self.quest_system.get_quest_log())
        input("\nPress Enter to continue...")
    
    def use_item(self, item_name: str):
        """Use an item from inventory."""
        player = self.game_state.player
        
        # Find item
        item = self.inventory_system.find_item(player, item_name)
        if not item:
            print(f"You don't have '{item_name}'.")
            return
        
        # Use item
        result = item.use(player, self.game_state)
        print(result["message"])
        
        # Remove item if consumed
        if result.get("consumed", False):
            self.inventory_system.remove_item(player, item, 1)
            
            # Trigger quest events for item use
            self.quest_system.trigger_event(self.game_state, "item_used", 
                                          {"item_name": item.name})
        
        input("\nPress Enter to continue...")
    
    def equip_item(self, item_name: str):
        """Equip an item from inventory."""
        player = self.game_state.player
        
        # Find item
        item = self.inventory_system.find_item(player, item_name)
        if not item:
            print(f"You don't have '{item_name}'.")
            return
        
        # Try to equip item
        if player.equip_item(item):
            print(f"You equip {item.name}.")
        else:
            print(f"You cannot equip {item.name}.")
        
        input("\nPress Enter to continue...")
    
    def drop_item(self, item_name: str):
        """Drop an item from inventory."""
        player = self.game_state.player
        location = self.game_state.current_location
        
        # Find item
        item = self.inventory_system.find_item(player, item_name)
        if not item:
            print(f"You don't have '{item_name}'.")
            return
        
        # Drop item
        if self.inventory_system.drop_item(player, item, 1, location):
            print(f"You drop {item.name}.")
        else:
            print(f"You cannot drop {item.name}.")
        
        input("\nPress Enter to continue...")
    
    def start_combat(self, enemies: List):
        """Start a combat encounter."""
        player = self.game_state.player
        
        print(f"\n{'='*50}")
        print("COMBAT ENCOUNTER!")
        print(f"{'='*50}")
        
        result = self.combat_system.start_combat(player, enemies)
        
        if result.victory:
            print("You are victorious!")
            # Award experience
            if result.experience_gained > 0:
                print(f"Experience gained: {result.experience_gained}")
        elif result.fled:
            print("You managed to escape!")
        else:
            print("You have been defeated...")
            # Handle defeat (could respawn at safe location, etc.)
            
        return result