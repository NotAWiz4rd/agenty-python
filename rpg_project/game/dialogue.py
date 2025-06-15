"""
Dialogue System for The Shattered Realms RPG.

Manages conversations, dialogue trees, and NPC interactions.
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from game.character import NPC, PlayerCharacter


class DialogueConditionType(Enum):
    """Types of dialogue conditions."""
    FLAG = "flag"
    QUEST_STATUS = "quest_status"
    LEVEL = "level"
    ATTRIBUTE = "attribute"
    ITEM = "item"
    REPUTATION = "reputation"
    CUSTOM = "custom"


class DialogueCondition:
    """Represents a condition for dialogue options."""
    
    def __init__(self, condition_type: DialogueConditionType, 
                 key: str, value: Any, operator: str = "=="):
        self.condition_type = condition_type
        self.key = key
        self.value = value
        self.operator = operator  # ==, !=, >, <, >=, <=
        self.custom_func: Optional[Callable] = None
    
    def check(self, game_state) -> bool:
        """Check if condition is met."""
        if self.condition_type == DialogueConditionType.FLAG:
            actual_value = game_state.get_flag(self.key, False)
        elif self.condition_type == DialogueConditionType.QUEST_STATUS:
            quest = game_state.world.quest_system.get_quest(self.key)
            actual_value = quest.status.value if quest else "not_started"
        elif self.condition_type == DialogueConditionType.LEVEL:
            actual_value = game_state.player.level
        elif self.condition_type == DialogueConditionType.ATTRIBUTE:
            actual_value = game_state.player.attributes.get(self.key, 0)
        elif self.condition_type == DialogueConditionType.ITEM:
            item = game_state.world.inventory_system.find_item(game_state.player, self.key)
            actual_value = item.quantity if item else 0
        elif self.condition_type == DialogueConditionType.REPUTATION:
            actual_value = game_state.player.faction_reputation.get(self.key, 0)
        elif self.condition_type == DialogueConditionType.CUSTOM:
            return self.custom_func(game_state) if self.custom_func else False
        else:
            return False
        
        # Apply operator
        if self.operator == "==":
            return actual_value == self.value
        elif self.operator == "!=":
            return actual_value != self.value
        elif self.operator == ">":
            return actual_value > self.value
        elif self.operator == "<":
            return actual_value < self.value
        elif self.operator == ">=":
            return actual_value >= self.value
        elif self.operator == "<=":
            return actual_value <= self.value
        
        return False


class DialogueEffect:
    """Represents an effect of a dialogue choice."""
    
    def __init__(self, effect_type: str, key: str, value: Any):
        self.effect_type = effect_type  # flag, reputation, item, quest, etc.
        self.key = key
        self.value = value
        self.custom_func: Optional[Callable] = None
    
    def apply(self, game_state, npc: NPC):
        """Apply the dialogue effect."""
        if self.effect_type == "flag":
            game_state.set_flag(self.key, self.value)
        elif self.effect_type == "reputation":
            current = game_state.player.faction_reputation.get(self.key, 0)
            game_state.player.faction_reputation[self.key] = current + self.value
        elif self.effect_type == "npc_disposition":
            npc.modify_disposition(self.value)
        elif self.effect_type == "quest_start":
            game_state.world.quest_system.start_quest(self.key, game_state)
        elif self.effect_type == "quest_complete":
            game_state.world.quest_system.complete_quest(self.key, game_state)
        elif self.effect_type == "give_item":
            item = game_state.world.inventory_system.create_item(self.key, self.value)
            if item:
                game_state.world.inventory_system.add_item(game_state.player, item)
        elif self.effect_type == "custom":
            if self.custom_func:
                self.custom_func(game_state, npc)


class DialogueOption:
    """Represents a dialogue choice option."""
    
    def __init__(self, option_id: str, text: str, next_node: str = ""):
        self.option_id = option_id
        self.text = text
        self.next_node = next_node
        self.conditions: List[DialogueCondition] = []
        self.effects: List[DialogueEffect] = []
        self.closes_dialogue = False
        self.one_time_only = False
        self.used = False
    
    def add_condition(self, condition: DialogueCondition):
        """Add a condition for this option to appear."""
        self.conditions.append(condition)
    
    def add_effect(self, effect: DialogueEffect):
        """Add an effect when this option is chosen."""
        self.effects.append(effect)
    
    def is_available(self, game_state) -> bool:
        """Check if this option is available."""
        if self.one_time_only and self.used:
            return False
        
        for condition in self.conditions:
            if not condition.check(game_state):
                return False
        
        return True
    
    def choose(self, game_state, npc: NPC):
        """Execute this dialogue option."""
        for effect in self.effects:
            effect.apply(game_state, npc)
        
        if self.one_time_only:
            self.used = True


class DialogueNode:
    """Represents a node in a dialogue tree."""
    
    def __init__(self, node_id: str, speaker: str, text: str):
        self.node_id = node_id
        self.speaker = speaker  # "npc" or "player"
        self.text = text
        self.options: List[DialogueOption] = []
        self.conditions: List[DialogueCondition] = []
        
        # Auto-progression (for NPC nodes that don't need player input)
        self.auto_next: Optional[str] = None
        self.auto_delay = 0
    
    def add_option(self, option: DialogueOption):
        """Add a dialogue option to this node."""
        self.options.append(option)
    
    def add_condition(self, condition: DialogueCondition):
        """Add a condition for this node to be accessible."""
        self.conditions.append(condition)
    
    def is_accessible(self, game_state) -> bool:
        """Check if this node can be accessed."""
        for condition in self.conditions:
            if not condition.check(game_state):
                return False
        return True
    
    def get_available_options(self, game_state) -> List[DialogueOption]:
        """Get available options for this node."""
        return [option for option in self.options if option.is_available(game_state)]


class DialogueTree:
    """Represents a complete dialogue tree for an NPC."""
    
    def __init__(self, tree_id: str, npc_name: str):
        self.tree_id = tree_id
        self.npc_name = npc_name
        self.nodes: Dict[str, DialogueNode] = {}
        self.root_node = "start"
        self.current_node = "start"
        
        # Conversation state
        self.conversation_flags = {}
        self.conversation_data = {}
    
    def add_node(self, node: DialogueNode):
        """Add a node to the dialogue tree."""
        self.nodes[node.node_id] = node
    
    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get a dialogue node by ID."""
        return self.nodes.get(node_id)
    
    def reset_conversation(self):
        """Reset conversation to the beginning."""
        self.current_node = self.root_node
        self.conversation_flags = {}
        self.conversation_data = {}
    
    def set_conversation_flag(self, flag: str, value: Any):
        """Set a conversation-specific flag."""
        self.conversation_flags[flag] = value
    
    def get_conversation_flag(self, flag: str, default: Any = False) -> Any:
        """Get a conversation-specific flag."""
        return self.conversation_flags.get(flag, default)


class DialogueSystem:
    """Manages all dialogue in the game."""
    
    def __init__(self):
        self.dialogue_trees: Dict[str, DialogueTree] = {}
        self.current_conversation: Optional[DialogueTree] = None
        self.current_npc: Optional[NPC] = None
        
        # Create all dialogue trees
        self.create_dialogue_trees()
    
    def create_dialogue_trees(self):
        """Create dialogue trees for all NPCs."""
        # Harbor Master dialogue
        self.create_harbor_master_dialogue()
        
        # Tavern Keeper dialogue
        self.create_tavern_keeper_dialogue()
        
        # Generic merchant dialogue
        self.create_merchant_dialogue()
    
    def create_harbor_master_dialogue(self):
        """Create dialogue for Harbor Master Jorik."""
        tree = DialogueTree("harbor_master", "Harbor Master Jorik")
        
        # Start node
        start = DialogueNode("start", "npc", 
                           "Welcome to Port Aethros, Resonance Walker. I've been expecting someone like you. "
                           "These are dangerous times, and we need people with your abilities.")
        
        # Player options
        option1 = DialogueOption("ask_about_aethros", 
                               "Tell me about Aethros.", "about_aethros")
        option2 = DialogueOption("ask_about_danger", 
                               "What kind of dangers?", "about_dangers")
        option3 = DialogueOption("ask_travel", 
                               "I need passage to other islands.", "travel_options")
        option4 = DialogueOption("leave", 
                               "Thank you. I should explore the port.", "")
        option4.closes_dialogue = True
        
        start.add_option(option1)
        start.add_option(option2)
        start.add_option(option3)
        start.add_option(option4)
        
        # About Aethros node
        about_aethros = DialogueNode("about_aethros", "npc",
                                   "Aethros is the last truly free trading port in the known realms. "
                                   "We maintain neutrality between the various island factions, "
                                   "which makes us valuable to everyone and trusted by none.")
        
        back_option = DialogueOption("back", "I see. What else can you tell me?", "start")
        about_aethros.add_option(back_option)
        
        # About dangers node
        about_dangers = DialogueNode("about_dangers", "npc",
                                   "The Void Storms are getting stronger, and several islands have "
                                   "gone dark in recent months. There are also reports of corrupted "
                                   "crystals appearing - crystals that drive people mad with power.")
        
        back_option2 = DialogueOption("back", "That does sound dangerous.", "start")
        about_dangers.add_option(back_option2)
        
        # Travel options node
        travel_options = DialogueNode("travel_options", "npc",
                                    "I can arrange passage to any of the major islands we trade with. "
                                    "Verdant Isle for nature magic, Crystalline Peaks for mining, "
                                    "or Shadowmere if you're brave enough.")
        
        travel_option1 = DialogueOption("travel_verdant", 
                                      "Book passage to Verdant Isle.", "book_travel")
        travel_option1.add_effect(DialogueEffect("flag", "destination", "verdant_landing"))
        
        travel_option2 = DialogueOption("travel_peaks", 
                                      "Book passage to Crystalline Peaks.", "book_travel")
        travel_option2.add_effect(DialogueEffect("flag", "destination", "peaks_mining_station"))
        
        travel_option3 = DialogueOption("travel_shadowmere", 
                                      "Book passage to Shadowmere.", "book_travel")
        travel_option3.add_effect(DialogueEffect("flag", "destination", "shadowmere_shore"))
        
        back_option3 = DialogueOption("back", "Let me think about it.", "start")
        
        travel_options.add_option(travel_option1)
        travel_options.add_option(travel_option2)
        travel_options.add_option(travel_option3)
        travel_options.add_option(back_option3)
        
        # Book travel confirmation
        book_travel = DialogueNode("book_travel", "npc",
                                 "Passage booked. The ship will be ready when you are. "
                                 "Just return to the docks when you want to travel.")
        
        confirm_option = DialogueOption("confirm", "Thank you.", "")
        confirm_option.closes_dialogue = True
        book_travel.add_option(confirm_option)
        
        # Add nodes to tree
        tree.add_node(start)
        tree.add_node(about_aethros)
        tree.add_node(about_dangers)
        tree.add_node(travel_options)
        tree.add_node(book_travel)
        
        self.dialogue_trees["Harbor Master Jorik"] = tree
    
    def create_tavern_keeper_dialogue(self):
        """Create dialogue for Mara the Tavern Keeper."""
        tree = DialogueTree("tavern_keeper", "Mara the Tavern Keeper")
        
        # Start node
        start = DialogueNode("start", "npc",
                           "Welcome to the Floating Anchor! What can I get for you, traveler?")
        
        # Options
        food_option = DialogueOption("order_food", "I'd like some food.", "food_menu")
        room_option = DialogueOption("rent_room", "Do you have rooms available?", "room_rental")
        rumors_option = DialogueOption("ask_rumors", "Have you heard any interesting rumors?", "rumors")
        leave_option = DialogueOption("leave", "Just looking around, thanks.", "")
        leave_option.closes_dialogue = True
        
        start.add_option(food_option)
        start.add_option(room_option)
        start.add_option(rumors_option)
        start.add_option(leave_option)
        
        # Food menu
        food_menu = DialogueNode("food_menu", "npc",
                               "We have hearty stew, fresh bread, and crystal-fruit from Verdant Isle. "
                               "A meal costs 5 gold and will restore your health.")
        
        buy_food = DialogueOption("buy_food", "I'll take a meal.", "enjoy_meal")
        buy_food.add_effect(DialogueEffect("give_item", "hearty_meal", 1))
        
        back_food = DialogueOption("back", "Maybe later.", "start")
        food_menu.add_option(buy_food)
        food_menu.add_option(back_food)
        
        # Enjoy meal
        enjoy_meal = DialogueNode("enjoy_meal", "npc",
                                "Enjoy your meal! Come back anytime.")
        
        thanks_option = DialogueOption("thanks", "Thank you.", "")
        thanks_option.closes_dialogue = True
        enjoy_meal.add_option(thanks_option)
        
        # Rumors
        rumors = DialogueNode("rumors", "npc",
                            "Well, there's talk of strange lights seen near the Void Crossing, "
                            "and some say a lost island has been spotted drifting in the deep void. "
                            "Could just be traveler's tales, but you never know in these times.")
        
        back_rumors = DialogueOption("back", "Interesting. Anything else?", "start")
        rumors.add_option(back_rumors)
        
        # Add nodes to tree
        tree.add_node(start)
        tree.add_node(food_menu)
        tree.add_node(enjoy_meal)
        tree.add_node(rumors)
        
        self.dialogue_trees["Mara the Tavern Keeper"] = tree
    
    def create_merchant_dialogue(self):
        """Create generic merchant dialogue."""
        tree = DialogueTree("generic_merchant", "Merchant")
        
        start = DialogueNode("start", "npc",
                           "Greetings, traveler! I have wares for sale if you have coin.")
        
        browse_option = DialogueOption("browse", "Let me see what you have.", "shop")
        leave_option = DialogueOption("leave", "Not interested.", "")
        leave_option.closes_dialogue = True
        
        start.add_option(browse_option)
        start.add_option(leave_option)
        
        # Shop node (placeholder)
        shop = DialogueNode("shop", "npc",
                          "Here are my goods. [Shop interface would open here]")
        
        done_option = DialogueOption("done", "I'm done shopping.", "")
        done_option.closes_dialogue = True
        shop.add_option(done_option)
        
        tree.add_node(start)
        tree.add_node(shop)
        
        self.dialogue_trees["generic_merchant"] = tree
    
    def start_conversation(self, npc: NPC, game_state):
        """Start a conversation with an NPC."""
        # Find appropriate dialogue tree
        dialogue_tree = None
        
        if npc.name in self.dialogue_trees:
            dialogue_tree = self.dialogue_trees[npc.name]
        elif npc.npc_type == "merchant" and "generic_merchant" in self.dialogue_trees:
            dialogue_tree = self.dialogue_trees["generic_merchant"]
        
        if not dialogue_tree:
            print(f"{npc.name} has nothing to say right now.")
            return
        
        # Set up conversation
        self.current_conversation = dialogue_tree
        self.current_npc = npc
        dialogue_tree.reset_conversation()
        
        print(f"\n--- Conversation with {npc.name} ---")
        print(f"Disposition: {npc.get_disposition_text()}")
        
        # Start conversation loop
        self.continue_conversation(game_state)
    
    def continue_conversation(self, game_state):
        """Continue the current conversation."""
        if not self.current_conversation or not self.current_npc:
            return
        
        tree = self.current_conversation
        npc = self.current_npc
        
        # Get current node
        current_node = tree.get_node(tree.current_node)
        if not current_node:
            print("Conversation ended.")
            self.end_conversation()
            return
        
        # Check if node is accessible
        if not current_node.is_accessible(game_state):
            print("Conversation ended.")
            self.end_conversation()
            return
        
        # Display node text
        if current_node.speaker == "npc":
            print(f"\n{npc.name}: {current_node.text}")
        else:
            print(f"\nYou: {current_node.text}")
        
        # Check for auto-progression
        if current_node.auto_next:
            tree.current_node = current_node.auto_next
            self.continue_conversation(game_state)
            return
        
        # Get available options
        available_options = current_node.get_available_options(game_state)
        
        if not available_options:
            print("Conversation ended.")
            self.end_conversation()
            return
        
        # Display options
        print("\nResponse options:")
        for i, option in enumerate(available_options):
            print(f"{i + 1}. {option.text}")
        
        # Get player choice
        while True:
            try:
                choice = int(input("Choose response (number): ")) - 1
                if 0 <= choice < len(available_options):
                    chosen_option = available_options[choice]
                    break
                print(f"Please choose a number between 1 and {len(available_options)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Execute choice
        chosen_option.choose(game_state, npc)
        
        # Check if conversation should end
        if chosen_option.closes_dialogue or not chosen_option.next_node:
            print("Conversation ended.")
            self.end_conversation()
            return
        
        # Move to next node
        tree.current_node = chosen_option.next_node
        self.continue_conversation(game_state)
    
    def end_conversation(self):
        """End the current conversation."""
        self.current_conversation = None
        self.current_npc = None
    
    def add_dialogue_tree(self, tree: DialogueTree):
        """Add a dialogue tree to the system."""
        self.dialogue_trees[tree.npc_name] = tree
    
    def get_dialogue_tree(self, npc_name: str) -> Optional[DialogueTree]:
        """Get a dialogue tree by NPC name."""
        return self.dialogue_trees.get(npc_name)
    
    def create_simple_dialogue(self, npc_name: str, greeting: str, responses: List[str]) -> DialogueTree:
        """Create a simple dialogue tree with basic greeting and responses."""
        tree = DialogueTree(f"simple_{npc_name.lower().replace(' ', '_')}", npc_name)
        
        # Start node
        start = DialogueNode("start", "npc", greeting)
        
        # Add response options
        for i, response in enumerate(responses):
            option = DialogueOption(f"response_{i}", response, "")
            option.closes_dialogue = True
            start.add_option(option)
        
        tree.add_node(start)
        return tree
    
    def set_npc_dialogue_state(self, npc_name: str, state: str):
        """Set an NPC's dialogue state."""
        tree = self.get_dialogue_tree(npc_name)
        if tree:
            tree.current_node = state
    
    def has_conversation_flag(self, flag: str) -> bool:
        """Check if a conversation flag is set."""
        if self.current_conversation:
            return self.current_conversation.get_conversation_flag(flag)
        return False
    
    def set_conversation_flag(self, flag: str, value: Any):
        """Set a conversation flag."""
        if self.current_conversation:
            self.current_conversation.set_conversation_flag(flag, value)
        return self.dialogue_trees.get(npc_name)