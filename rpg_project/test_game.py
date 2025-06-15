#!/usr/bin/env python3
"""
Test script for The Shattered Realms RPG.
"""

import sys
from pathlib import Path

# Add the rpg_project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from game.character import PlayerCharacter
from game.game_engine import GameEngine
from utils.save_system import SaveSystem

def test_character_creation():
    """Test character creation."""
    print("Testing character creation...")
    
    player = PlayerCharacter("Test Hero")
    print(f"Created character: {player.name}")
    print(f"Starting health: {player.current_health}/{player.max_health}")
    print(f"Starting magic: {player.current_magic}/{player.max_magic}")
    
    # Test attribute modification
    player.attributes[player.attributes.__class__.__members__['STRENGTH']] = 15
    player.update_derived_stats()
    print(f"Updated stats: Health {player.current_health}/{player.max_health}")
    
    return True

def test_game_engine_init():
    """Test game engine initialization."""
    print("Testing game engine initialization...")
    
    save_system = SaveSystem()
    engine = GameEngine(save_system)
    
    print("Game engine created successfully")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("THE SHATTERED REALMS - COMPONENT TESTS")
    print("=" * 50)
    
    tests = [
        test_character_creation,
        test_game_engine_init,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                print("✓ PASSED\n")
                passed += 1
            else:
                print("✗ FAILED\n")
        except Exception as e:
            print(f"✗ ERROR: {e}\n")
    
    print(f"Tests passed: {passed}/{len(tests)}")