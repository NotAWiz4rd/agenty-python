#!/usr/bin/env python3
"""
The Shattered Realms RPG - Main Game Entry Point

A text-based RPG set in a post-apocalyptic fantasy world where reality 
itself was shattered into floating islands.
"""

import sys
import os
from pathlib import Path

# Add the rpg_project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from game.game_engine import GameEngine
from game.ui.menu_system import MenuSystem
from utils.save_system import SaveSystem


def main():
    """Main game entry point."""
    print("=" * 60)
    print("           THE SHATTERED REALMS")
    print("        A Text-Based RPG Adventure")
    print("=" * 60)
    print()
    
    # Initialize game components
    save_system = SaveSystem()
    menu_system = MenuSystem()
    game_engine = GameEngine(save_system)
    
    # Main menu loop
    while True:
        choice = menu_system.show_main_menu()
        
        if choice == "new_game":
            game_engine.start_new_game()
        elif choice == "load_game":
            if save_system.load_game():
                game_engine.continue_game()
            else:
                print("No saved game found.")
                input("Press Enter to continue...")
        elif choice == "credits":
            menu_system.show_credits()
        elif choice == "quit":
            print("Thank you for playing The Shattered Realms!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Your progress has been saved.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("The game will now exit.")
        sys.exit(1)