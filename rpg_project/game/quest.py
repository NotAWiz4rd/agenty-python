"""
Quest System for The Shattered Realms RPG.

Manages quests, objectives, and story progression.
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class QuestStatus(Enum):
    """Quest status states."""
    NOT_STARTED = "not_started"
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class ObjectiveType(Enum):
    """Types of quest objectives."""
    KILL = "kill"
    COLLECT = "collect"
    TALK_TO = "talk_to"
    VISIT = "visit"
    DELIVER = "deliver"
    ESCORT = "escort"
    CUSTOM = "custom"


class QuestObjective:
    """Represents a quest objective."""
    
    def __init__(self, objective_id: str, objective_type: ObjectiveType, 
                 description: str, target: str = "", quantity: int = 1):
        self.objective_id = objective_id
        self.objective_type = objective_type
        self.description = description
        self.target = target
        self.quantity = quantity
        self.current_progress = 0
        self.completed = False
        self.optional = False
        
        # Custom validation function for complex objectives
        self.validation_func: Optional[Callable] = None
        
        # Data for complex objectives
        self.data = {}
    
    def update_progress(self, game_state, amount: int = 1) -> bool:
        """Update objective progress."""
        if self.completed:
            return False
        
        self.current_progress = min(self.current_progress + amount, self.quantity)
        
        if self.current_progress >= self.quantity:
            self.completed = True
            return True
        
        return False
    
    def check_completion(self, game_state) -> bool:
        """Check if objective is completed using custom validation."""
        if self.completed:
            return True
        
        if self.validation_func:
            self.completed = self.validation_func(game_state, self)
            return self.completed
        
        return self.current_progress >= self.quantity
    
    def get_progress_text(self) -> str:
        """Get progress text for this objective."""
        if self.completed:
            return f"✓ {self.description}"
        elif self.quantity > 1:
            return f"◦ {self.description} ({self.current_progress}/{self.quantity})"
        else:
            return f"◦ {self.description}"


class Quest:
    """Represents a quest in the game."""
    
    def __init__(self, quest_id: str, title: str, description: str):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.status = QuestStatus.NOT_STARTED
        
        # Quest organization
        self.category = "main"  # main, side, faction, etc.
        self.level_requirement = 1
        self.prerequisites = []  # Quest IDs that must be completed first
        
        # Quest objectives
        self.objectives: List[QuestObjective] = []
        self.current_objective_index = 0
        
        # Quest rewards
        self.experience_reward = 0
        self.gold_reward = 0
        self.item_rewards = []
        self.reputation_rewards = {}
        
        # Quest giver and location info
        self.quest_giver = ""
        self.start_location = ""
        self.turn_in_location = ""
        
        # Story and dialogue
        self.start_dialogue = ""
        self.progress_dialogue = {}
        self.completion_dialogue = ""
        
        # Quest flags and data
        self.quest_flags = {}
        self.quest_data = {}
        
        # Event handlers
        self.on_start_handlers: List[Callable] = []
        self.on_progress_handlers: List[Callable] = []
        self.on_complete_handlers: List[Callable] = []
        self.on_fail_handlers: List[Callable] = []
    
    def can_start(self, game_state) -> bool:
        """Check if quest can be started."""
        if self.status != QuestStatus.NOT_STARTED:
            return False
        
        # Check level requirement
        if game_state.player.level < self.level_requirement:
            return False
        
        # Check prerequisites
        for prereq_id in self.prerequisites:
            prereq_quest = game_state.world.quest_system.get_quest(prereq_id)
            if not prereq_quest or prereq_quest.status != QuestStatus.COMPLETED:
                return False
        
        return True
    
    def start_quest(self, game_state):
        """Start the quest."""
        if not self.can_start(game_state):
            return False
        
        self.status = QuestStatus.ACTIVE
        
        # Run start handlers
        for handler in self.on_start_handlers:
            handler(game_state, self)
        
        # Set initial quest flags
        for flag, value in self.quest_flags.items():
            game_state.set_flag(f"quest_{self.quest_id}_{flag}", value)
        
        print(f"\nQuest Started: {self.title}")
        print(f"{self.description}")
        
        if self.objectives:
            print(f"\nObjective: {self.objectives[0].description}")
        
        return True
    
    def add_objective(self, objective: QuestObjective):
        """Add an objective to the quest."""
        self.objectives.append(objective)
    
    def update_progress(self, game_state, objective_id: str = None, amount: int = 1):
        """Update quest progress."""
        if self.status != QuestStatus.ACTIVE:
            return
        
        updated = False
        
        if objective_id:
            # Update specific objective
            for objective in self.objectives:
                if objective.objective_id == objective_id:
                    if objective.update_progress(game_state, amount):
                        updated = True
                        print(f"Objective completed: {objective.description}")
                    break
        else:
            # Update current objective
            if self.current_objective_index < len(self.objectives):
                current_obj = self.objectives[self.current_objective_index]
                if current_obj.update_progress(game_state, amount):
                    updated = True
                    print(f"Objective completed: {current_obj.description}")
                    self.current_objective_index += 1
                    
                    # Show next objective
                    if self.current_objective_index < len(self.objectives):
                        next_obj = self.objectives[self.current_objective_index]
                        print(f"New objective: {next_obj.description}")
        
        if updated:
            # Run progress handlers
            for handler in self.on_progress_handlers:
                handler(game_state, self)
            
            # Check if quest is complete
            self.check_completion(game_state)
    
    def check_completion(self, game_state):
        """Check if quest is complete."""
        if self.status != QuestStatus.ACTIVE:
            return
        
        # Check if all required objectives are complete
        required_objectives = [obj for obj in self.objectives if not obj.optional]
        completed_required = [obj for obj in required_objectives if obj.completed]
        
        if len(completed_required) == len(required_objectives):
            self.complete_quest(game_state)
    
    def complete_quest(self, game_state):
        """Complete the quest."""
        self.status = QuestStatus.COMPLETED
        
        print(f"\nQuest Completed: {self.title}")
        
        # Award rewards
        if self.experience_reward > 0:
            game_state.player.add_experience(self.experience_reward)
            print(f"Experience gained: {self.experience_reward}")
        
        if self.gold_reward > 0:
            # Would need a currency system
            print(f"Gold reward: {self.gold_reward}")
        
        if self.item_rewards:
            for item_id in self.item_rewards:
                item = game_state.world.inventory_system.create_item(item_id)
                if item and game_state.world.inventory_system.add_item(game_state.player, item):
                    print(f"Item received: {item.name}")
        
        if self.reputation_rewards:
            for faction, amount in self.reputation_rewards.items():
                # Would update faction reputation
                print(f"Reputation with {faction}: {amount:+d}")
        
        # Run completion handlers
        for handler in self.on_complete_handlers:
            handler(game_state, self)
        
        # Set completion flag
        game_state.set_flag(f"quest_{self.quest_id}_completed", True)
    
    def fail_quest(self, game_state, reason: str = ""):
        """Fail the quest."""
        self.status = QuestStatus.FAILED
        
        print(f"\nQuest Failed: {self.title}")
        if reason:
            print(f"Reason: {reason}")
        
        # Run failure handlers
        for handler in self.on_fail_handlers:
            handler(game_state, self)
        
        # Set failure flag
        game_state.set_flag(f"quest_{self.quest_id}_failed", True)
    
    def get_status_text(self) -> str:
        """Get formatted quest status."""
        status_text = f"{self.title} [{self.status.value.replace('_', ' ').title()}]\n"
        status_text += f"{self.description}\n"
        
        if self.status == QuestStatus.ACTIVE:
            status_text += "\nObjectives:\n"
            for i, objective in enumerate(self.objectives):
                if i <= self.current_objective_index or objective.completed:
                    status_text += f"  {objective.get_progress_text()}\n"
        
        return status_text


class QuestSystem:
    """Manages all quests in the game."""
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []
        self.failed_quests: List[Quest] = []
        
        # Create all game quests
        self.create_quests()
    
    def create_quests(self):
        """Create all quests in the game."""
        # Main story quests
        self.create_main_quests()
        
        # Side quests
        self.create_side_quests()
        
        # Faction quests
        self.create_faction_quests()
    
    def create_main_quests(self):
        """Create main story quests."""
        # Prologue quest
        prologue = Quest("prologue", "Arrival at Aethros", 
                        "You've arrived at Port Aethros, the last free trading hub. Learn about your situation and find your bearings.")
        
        # Prologue objectives
        prologue.add_objective(QuestObjective("explore_docks", ObjectiveType.VISIT, 
                                            "Explore the docks area", "aethros_docks"))
        prologue.add_objective(QuestObjective("talk_harbor_master", ObjectiveType.TALK_TO,
                                            "Speak with the Harbor Master", "Harbor Master Jorik"))
        prologue.add_objective(QuestObjective("visit_tavern", ObjectiveType.VISIT,
                                            "Visit the Floating Anchor Tavern", "aethros_tavern"))
        
        prologue.experience_reward = 50
        prologue.category = "main"
        prologue.quest_giver = "None"  # Automatic quest
        
        self.add_quest(prologue)
        
        # First Crystal
        first_crystal = Quest("first_crystal", "The First Attunement",
                            "You must learn to safely attune to crystal magic to survive in this world. Find a suitable crystal and attempt your first attunement.")
        
        first_crystal.add_objective(QuestObjective("find_crystal", ObjectiveType.COLLECT,
                                                 "Find a crystal fragment", "crystal_fragment"))
        first_crystal.add_objective(QuestObjective("attune_crystal", ObjectiveType.CUSTOM,
                                                 "Successfully attune to a crystal"))
        
        # Custom validation for attunement
        def check_attunement(game_state, objective):
            player = game_state.player
            return any(level > 0 for level in player.crystal_attunements.values())
        
        first_crystal.objectives[1].validation_func = check_attunement
        
        first_crystal.prerequisites = ["prologue"]
        first_crystal.experience_reward = 75
        first_crystal.item_rewards = ["basic_flame_crystal"]
        
        self.add_quest(first_crystal)
        
        # The Harmony Mystery
        harmony_mystery = Quest("harmony_mystery", "The Harmony Crystal Mystery",
                              "Ancient texts speak of Harmony Crystals that could reunite the shattered world. Begin investigating these legendary artifacts.")
        
        harmony_mystery.add_objective(QuestObjective("research_harmony", ObjectiveType.VISIT,
                                                   "Research Harmony Crystals at the library", "shadowmere_library"))
        harmony_mystery.add_objective(QuestObjective("speak_scholar", ObjectiveType.TALK_TO,
                                                    "Speak with a crystal scholar"))
        harmony_mystery.add_objective(QuestObjective("find_fragment", ObjectiveType.COLLECT,
                                                    "Find a Harmony Crystal fragment", "harmony_fragment"))
        
        harmony_mystery.prerequisites = ["first_crystal"]
        harmony_mystery.level_requirement = 3
        harmony_mystery.experience_reward = 150
        
        self.add_quest(harmony_mystery)
    
    def create_side_quests(self):
        """Create side quests."""
        # Crystal Trader's Request
        crystal_trade = Quest("crystal_trade", "Crystal Trader's Request",
                            "A crystal trader needs help acquiring rare crystals for their business.")
        
        crystal_trade.add_objective(QuestObjective("collect_crystals", ObjectiveType.COLLECT,
                                                 "Collect 3 different types of crystals", "", 3))
        
        crystal_trade.quest_giver = "Crystal Trader"
        crystal_trade.category = "side"
        crystal_trade.experience_reward = 60
        crystal_trade.gold_reward = 100
        
        self.add_quest(crystal_trade)
        
        # Lost Shipment
        lost_shipment = Quest("lost_shipment", "Lost Shipment",
                            "A merchant's shipment was lost in the void. Help recover the missing goods.")
        
        lost_shipment.add_objective(QuestObjective("search_void", ObjectiveType.VISIT,
                                                 "Search the void crossing", "void_crossing"))
        lost_shipment.add_objective(QuestObjective("recover_goods", ObjectiveType.COLLECT,
                                                 "Recover the lost goods", "lost_cargo"))
        lost_shipment.add_objective(QuestObjective("return_goods", ObjectiveType.DELIVER,
                                                 "Return goods to merchant"))
        
        lost_shipment.category = "side"
        lost_shipment.experience_reward = 80
        lost_shipment.item_rewards = ["health_potion", "magic_potion"]
        
        self.add_quest(lost_shipment)
    
    def create_faction_quests(self):
        """Create faction-specific quests."""
        # Aethros Council Quest
        council_favor = Quest("council_favor", "Council's Favor",
                            "The Aethros Council has a task that requires someone with your unique abilities.")
        
        council_favor.add_objective(QuestObjective("meet_councilor", ObjectiveType.TALK_TO,
                                                 "Meet with a council member"))
        council_favor.add_objective(QuestObjective("investigate_threat", ObjectiveType.CUSTOM,
                                                 "Investigate the reported threat"))
        
        council_favor.category = "faction"
        council_favor.level_requirement = 2
        council_favor.reputation_rewards = {"aethros_council": 50}
        
        self.add_quest(council_favor)
    
    def add_quest(self, quest: Quest):
        """Add a quest to the system."""
        self.quests[quest.quest_id] = quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)
    
    def start_quest(self, quest_id: str, game_state) -> bool:
        """Start a quest."""
        quest = self.get_quest(quest_id)
        if not quest:
            return False
        
        if quest.start_quest(game_state):
            if quest not in self.active_quests:
                self.active_quests.append(quest)
            return True
        
        return False
    
    def update_quest_progress(self, game_state, event_type: str, event_data: Dict[str, Any]):
        """Update quest progress based on game events."""
        for quest in self.active_quests[:]:  # Copy list to avoid modification issues
            self.update_single_quest(game_state, quest, event_type, event_data)
    
    def update_single_quest(self, game_state, quest: Quest, event_type: str, event_data: Dict[str, Any]):
        """Update a single quest's progress."""
        for objective in quest.objectives:
            if objective.completed:
                continue
            
            if self.check_objective_progress(objective, event_type, event_data):
                quest.update_progress(game_state, objective.objective_id)
    
    def check_objective_progress(self, objective: QuestObjective, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Check if an event triggers objective progress."""
        if objective.objective_type == ObjectiveType.KILL and event_type == "enemy_killed":
            return event_data.get("enemy_name") == objective.target or objective.target == ""
        
        elif objective.objective_type == ObjectiveType.COLLECT and event_type == "item_collected":
            return event_data.get("item_name") == objective.target
        
        elif objective.objective_type == ObjectiveType.TALK_TO and event_type == "talked_to_npc":
            return event_data.get("npc_name") == objective.target
        
        elif objective.objective_type == ObjectiveType.VISIT and event_type == "location_visited":
            return event_data.get("location_id") == objective.target
        
        elif objective.objective_type == ObjectiveType.DELIVER and event_type == "item_delivered":
            return (event_data.get("item_name") == objective.target or 
                   event_data.get("recipient") == objective.target)
        
        return False
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return self.active_quests[:]
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return self.completed_quests[:]
    
    def get_available_quests(self, game_state) -> List[Quest]:
        """Get quests that can be started."""
        available = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.NOT_STARTED and quest.can_start(game_state):
                available.append(quest)
        return available
    
    def complete_quest(self, quest_id: str, game_state) -> bool:
        """Manually complete a quest."""
        quest = self.get_quest(quest_id)
        if quest and quest.status == QuestStatus.ACTIVE:
            quest.complete_quest(game_state)
            
            if quest in self.active_quests:
                self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            
            return True
        return False
    
    def fail_quest(self, quest_id: str, game_state, reason: str = "") -> bool:
        """Manually fail a quest."""
        quest = self.get_quest(quest_id)
        if quest and quest.status == QuestStatus.ACTIVE:
            quest.fail_quest(game_state, reason)
            
            if quest in self.active_quests:
                self.active_quests.remove(quest)
            self.failed_quests.append(quest)
            
            return True
        return False
    
    def get_quest_log(self) -> str:
        """Get formatted quest log."""
        log = "=== QUEST LOG ===\n\n"
        
        if self.active_quests:
            log += "ACTIVE QUESTS:\n"
            for quest in self.active_quests:
                log += quest.get_status_text() + "\n"
        
        if self.completed_quests:
            log += "\nCOMPLETED QUESTS:\n"
            for quest in self.completed_quests[-5:]:  # Show last 5 completed
                log += f"✓ {quest.title}\n"
        
        if not self.active_quests and not self.completed_quests:
            log += "No quests available.\n"
        
        return log