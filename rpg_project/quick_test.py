#!/usr/bin/env python3
"""
Quick test of The Shattered Realms RPG components.
"""

import sys
from pathlib import Path

# Add the rpg_project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    
    from game.character import PlayerCharacter, Attribute, CrystalType
    print("✓ Character system imported")
    
    from game.world import World
    print("✓ World system imported")
    
    from game.combat import CombatSystem
    print("✓ Combat system imported")
    
    from game.inventory import InventorySystem, Item
    print("✓ Inventory system imported")
    
    from game.quest import QuestSystem
    print("✓ Quest system imported")
    
    from game.dialogue import DialogueSystem
    print("✓ Dialogue system imported")
    
    from game.game_engine import GameEngine
    print("✓ Game engine imported")
    
    from utils.save_system import SaveSystem
    print("✓ Save system imported")
    
    from game.ui.menu_system import MenuSystem
    print("✓ Menu system imported")
    
    print("\n✓ All imports successful!")
    
    print("\nTesting basic functionality...")
    
    # Test character creation
    player = PlayerCharacter("Test Hero")
    print(f"✓ Created player: {player.name}")
    
    # Test world creation
    world = World()
    print(f"✓ Created world with {len(world.locations)} locations")
    
    # Test inventory system
    inventory = InventorySystem()
    test_item = inventory.create_item("iron_sword")
    if test_item:
        print(f"✓ Created item: {test_item.name}")
    
    # Test systems initialization
    combat = CombatSystem()
    quest_system = QuestSystem()
    dialogue = DialogueSystem()
    save_system = SaveSystem()
    menu_system = MenuSystem()
    
    print("✓ All systems initialized successfully")
    
    print("\n🎉 All tests passed! The game components are working.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some game components may be missing.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("There may be issues with the game code.")