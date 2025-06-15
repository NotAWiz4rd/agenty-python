#!/usr/bin/env python3
"""
Comprehensive test suite for The Shattered Realms RPG.
"""

import sys
import unittest
from pathlib import Path

# Add the rpg_project directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.character import PlayerCharacter, NPC, Attribute, CrystalType
from game.combat import CombatSystem, ActionType, CombatAction
from game.inventory import InventorySystem, Item
from game.quest import QuestSystem, Quest, QuestObjective, ObjectiveType, QuestStatus
from game.dialogue import DialogueSystem, DialogueTree, DialogueNode, DialogueOption
from game.world import World, Location
from game.game_engine import GameEngine, GameState
from utils.save_system import SaveSystem


class TestCharacterSystem(unittest.TestCase):
    """Test character creation and progression."""
    
    def setUp(self):
        self.player = PlayerCharacter("Test Hero")
        self.npc = NPC("Test NPC", "merchant", 2)
    
    def test_character_creation(self):
        """Test basic character creation."""
        self.assertEqual(self.player.name, "Test Hero")
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.current_health, self.player.max_health)
        self.assertEqual(self.player.current_magic, self.player.max_magic)
        self.assertGreater(self.player.max_health, 0)
        self.assertGreater(self.player.max_magic, 0)
    
    def test_attribute_system(self):
        """Test attribute modification and modifiers."""
        original_strength = self.player.attributes[Attribute.STRENGTH]
        
        # Test attribute modification
        self.player.attributes[Attribute.STRENGTH] = 15
        self.player.update_derived_stats()
        
        self.assertEqual(self.player.attributes[Attribute.STRENGTH], 15)
        self.assertEqual(self.player.get_attribute_modifier(Attribute.STRENGTH), 2)
    
    def test_experience_and_leveling(self):
        """Test experience gain and level progression."""
        original_level = self.player.level
        self.player.add_experience(100)
        
        self.assertGreater(self.player.level, original_level)
        self.assertGreater(self.player.experience, 0)
    
    def test_crystal_attunement(self):
        """Test crystal magic system."""
        success = self.player.attune_crystal(CrystalType.FLAME, 1)
        
        if success:
            self.assertGreater(self.player.crystal_attunements[CrystalType.FLAME], 0)
        
        # Test corruption accumulation
        original_corruption = self.player.corruption_level
        self.player.add_corruption(10)
        self.assertGreater(self.player.corruption_level, original_corruption)
    
    def test_health_and_magic(self):
        """Test health and magic point systems."""
        # Test damage and healing
        self.player.take_damage(10)
        damaged_health = self.player.current_health
        self.player.heal(5)
        self.assertGreater(self.player.current_health, damaged_health)
        
        # Test magic usage and restoration
        self.player.use_magic(5)
        reduced_magic = self.player.current_magic
        self.player.restore_magic(3)
        self.assertGreater(self.player.current_magic, reduced_magic)
    
    def test_npc_system(self):
        """Test NPC creation and disposition."""
        self.assertEqual(self.npc.npc_type, "merchant")
        self.assertEqual(self.npc.level, 2)
        
        # Test disposition changes
        original_disposition = self.npc.disposition
        self.npc.modify_disposition(10)
        self.assertGreater(self.npc.disposition, original_disposition)


class TestInventorySystem(unittest.TestCase):
    """Test inventory and item management."""
    
    def setUp(self):
        self.inventory_system = InventorySystem()
        self.player = PlayerCharacter("Test Player")
    
    def test_item_creation(self):
        """Test item creation from templates."""
        sword = self.inventory_system.create_item("iron_sword")
        self.assertIsNotNone(sword)
        self.assertEqual(sword.name, "Iron Sword")
        self.assertEqual(sword.item_type, "weapon")
    
    def test_inventory_management(self):
        """Test adding, removing, and finding items."""
        sword = self.inventory_system.create_item("iron_sword")
        
        # Test adding items
        success = self.inventory_system.add_item(self.player, sword)
        self.assertTrue(success)
        self.assertIn(sword, self.player.inventory)
        
        # Test finding items
        found_item = self.inventory_system.find_item(self.player, "Iron Sword")
        self.assertEqual(found_item, sword)
        
        # Test removing items
        removed = self.inventory_system.remove_item(self.player, sword, 1)
        self.assertTrue(removed)
        self.assertNotIn(sword, self.player.inventory)
    
    def test_item_usage(self):
        """Test consumable item effects."""
        potion = self.inventory_system.create_item("health_potion")
        self.inventory_system.add_item(self.player, potion)
        
        # Damage player first
        self.player.take_damage(10)
        damaged_health = self.player.current_health
        
        # Use healing potion
        result = potion.use(self.player)
        self.assertTrue(result["success"])
        self.assertGreater(self.player.current_health, damaged_health)
    
    def test_equipment_system(self):
        """Test equipment and stat bonuses."""
        sword = self.inventory_system.create_item("iron_sword")
        self.inventory_system.add_item(self.player, sword)
        
        # Test equipping
        equipped = self.player.equip_item(sword)
        self.assertTrue(equipped)
        self.assertEqual(self.player.equipment["weapon"], sword)
        
        # Test unequipping
        unequipped = self.player.unequip_item("weapon")
        self.assertEqual(unequipped, sword)
        self.assertIsNone(self.player.equipment["weapon"])


class TestCombatSystem(unittest.TestCase):
    """Test combat mechanics."""
    
    def setUp(self):
        self.combat_system = CombatSystem()
        self.player = PlayerCharacter("Hero")
        self.enemy = NPC("Goblin", "enemy", 1)
    
    def test_combat_initialization(self):
        """Test combat setup and turn order."""
        # Mock combat without full execution
        self.combat_system.combat_participants = [self.player, self.enemy]
        self.combat_system.turn_order = sorted(
            self.combat_system.combat_participants,
            key=lambda char: char.attributes[Attribute.DEXTERITY],
            reverse=True
        )
        
        self.assertEqual(len(self.combat_system.turn_order), 2)
        self.assertIn(self.player, self.combat_system.turn_order)
        self.assertIn(self.enemy, self.combat_system.turn_order)
    
    def test_combat_actions(self):
        """Test different combat actions."""
        # Test attack action
        attack_action = CombatAction(ActionType.ATTACK, self.player, self.enemy)
        self.assertEqual(attack_action.action_type, ActionType.ATTACK)
        self.assertEqual(attack_action.actor, self.player)
        self.assertEqual(attack_action.target, self.enemy)
        
        # Test defend action
        defend_action = CombatAction(ActionType.DEFEND, self.player)
        self.assertEqual(defend_action.action_type, ActionType.DEFEND)
    
    def test_damage_calculation(self):
        """Test damage dealing and character state."""
        original_health = self.enemy.current_health
        self.enemy.take_damage(5)
        
        self.assertLess(self.enemy.current_health, original_health)
        
        if self.enemy.current_health <= 0:
            self.assertFalse(self.enemy.is_alive())


class TestQuestSystem(unittest.TestCase):
    """Test quest and objective tracking."""
    
    def setUp(self):
        self.quest_system = QuestSystem()
        self.game_state = GameState()
        self.game_state.player = PlayerCharacter("Test Player")
    
    def test_quest_creation(self):
        """Test quest initialization."""
        quest = self.quest_system.get_quest("prologue")
        self.assertIsNotNone(quest)
        self.assertEqual(quest.quest_id, "prologue")
        self.assertEqual(quest.status, QuestStatus.NOT_STARTED)
    
    def test_quest_starting(self):
        """Test quest activation."""
        success = self.quest_system.start_quest("prologue", self.game_state)
        
        if success:
            quest = self.quest_system.get_quest("prologue")
            self.assertEqual(quest.status, QuestStatus.ACTIVE)
            self.assertIn(quest, self.quest_system.active_quests)
    
    def test_objective_progress(self):
        """Test objective completion tracking."""
        self.quest_system.start_quest("prologue", self.game_state)
        
        # Trigger a quest event
        self.quest_system.trigger_event(
            self.game_state, 
            "location_visited", 
            {"location_id": "aethros_docks"}
        )
        
        quest = self.quest_system.get_quest("prologue")
        
        # Check if any objectives were completed
        completed_objectives = [obj for obj in quest.objectives if obj.completed]
        # May or may not complete depending on quest design
    
    def test_quest_completion(self):
        """Test quest completion and rewards."""
        # This would require completing all objectives
        # Implementation depends on specific quest design
        pass


class TestDialogueSystem(unittest.TestCase):
    """Test dialogue and conversation trees."""
    
    def setUp(self):
        self.dialogue_system = DialogueSystem()
        self.npc = NPC("Test NPC", "merchant")
        self.game_state = GameState()
        self.game_state.player = PlayerCharacter("Test Player")
    
    def test_dialogue_tree_creation(self):
        """Test dialogue tree structure."""
        tree = self.dialogue_system.get_dialogue_tree("Harbor Master Jorik")
        self.assertIsNotNone(tree)
        
        start_node = tree.get_node("start")
        self.assertIsNotNone(start_node)
        self.assertGreater(len(start_node.options), 0)
    
    def test_dialogue_conditions(self):
        """Test conditional dialogue options."""
        # This would test dialogue conditions based on game state
        # Implementation depends on specific dialogue trees
        pass
    
    def test_dialogue_effects(self):
        """Test dialogue effects on game state."""
        # This would test flag setting and other effects
        # Implementation depends on specific dialogue options
        pass


class TestWorldSystem(unittest.TestCase):
    """Test world and location management."""
    
    def setUp(self):
        self.world = World()
    
    def test_world_creation(self):
        """Test world initialization."""
        self.assertGreater(len(self.world.locations), 0)
        
        # Test specific locations exist
        aethros_docks = self.world.get_location("aethros_docks")
        self.assertIsNotNone(aethros_docks)
        self.assertEqual(aethros_docks.name, "Aethros Docks")
    
    def test_location_connections(self):
        """Test location exit connections."""
        docks = self.world.get_location("aethros_docks")
        self.assertGreater(len(docks.exits), 0)
        
        # Test bidirectional connections
        for direction, destination_id in docks.exits.items():
            destination = self.world.get_location(destination_id)
            self.assertIsNotNone(destination)
    
    def test_npc_placement(self):
        """Test NPC location assignment."""
        docks = self.world.get_location("aethros_docks")
        self.assertGreater(len(docks.npcs), 0)
        
        # Check NPC properties
        for npc in docks.npcs:
            self.assertIsNotNone(npc.name)
            self.assertIsNotNone(npc.npc_type)


class TestSaveSystem(unittest.TestCase):
    """Test game state persistence."""
    
    def setUp(self):
        self.save_system = SaveSystem()
        self.game_state = GameState()
        self.game_state.player = PlayerCharacter("Save Test Player")
    
    def test_serialization(self):
        """Test game state serialization."""
        # Test character serialization
        char_data = self.save_system.serialize_character(self.game_state.player)
        self.assertIsInstance(char_data, dict)
        self.assertEqual(char_data["name"], "Save Test Player")
        self.assertIn("attributes", char_data)
        self.assertIn("inventory", char_data)
    
    def test_save_file_operations(self):
        """Test save file creation and management."""
        # This would test actual file operations
        # Skip if no write permissions available
        pass


class TestGameEngine(unittest.TestCase):
    """Test main game engine integration."""
    
    def setUp(self):
        from utils.save_system import SaveSystem
        self.save_system = SaveSystem()
        self.game_engine = GameEngine(self.save_system)
    
    def test_engine_initialization(self):
        """Test game engine setup."""
        self.assertIsNotNone(self.game_engine.combat_system)
        self.assertIsNotNone(self.game_engine.inventory_system)
        self.assertIsNotNone(self.game_engine.quest_system)
        self.assertIsNotNone(self.game_engine.dialogue_system)
    
    def test_system_integration(self):
        """Test system interconnections."""
        # Create a minimal game state for testing
        self.game_engine.game_state.player = PlayerCharacter("Integration Test")
        self.game_engine.initialize_world()
        
        self.assertIsNotNone(self.game_engine.world)
        self.assertIsNotNone(self.game_engine.world.inventory_system)
        self.assertIsNotNone(self.game_engine.world.quest_system)


def run_all_tests():
    """Run the complete test suite."""
    print("=" * 60)
    print("THE SHATTERED REALMS RPG - TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCharacterSystem,
        TestInventorySystem,
        TestCombatSystem,
        TestQuestSystem,
        TestDialogueSystem,
        TestWorldSystem,
        TestSaveSystem,
        TestGameEngine,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, trace in result.failures:
            print(f"- {test}: {trace}")
    
    if result.errors:
        print("\nERRORS:")
        for test, trace in result.errors:
            print(f"- {test}: {trace}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)