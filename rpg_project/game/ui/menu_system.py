"""
Menu System for The Shattered Realms RPG.

Handles main menu, character creation, and other UI menus.
"""

import os
import time
from typing import Dict, List, Optional, Any


class MenuSystem:
    """Manages game menus and user interface."""
    
    def __init__(self):
        pass
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("           THE SHATTERED REALMS")
            print("        A Text-Based RPG Adventure")
            print("=" * 60)
            print()
            print("1. New Game")
            print("2. Load Game")
            print("3. Credits")
            print("4. Quit")
            print()
            
            try:
                choice = int(input("Enter your choice (1-4): "))
                
                if choice == 1:
                    return "new_game"
                elif choice == 2:
                    return "load_game"
                elif choice == 3:
                    return "credits"
                elif choice == 4:
                    return "quit"
                else:
                    print("Invalid choice. Please enter 1-4.")
                    input("Press Enter to continue...")
                    
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
    
    def show_credits(self):
        """Display game credits."""
        self.clear_screen()
        print("=" * 60)
        print("                  CREDITS")
        print("=" * 60)
        print()
        print("The Shattered Realms RPG")
        print("A text-based role-playing game")
        print()
        print("Game Design & Programming:")
        print("  AI Assistant")
        print()
        print("Story & World Building:")
        print("  Creative AI Collaboration")
        print()
        print("Special Thanks:")
        print("  To the human who provided the creative challenge")
        print("  and to all future players who will explore")
        print("  the Shattered Realms")
        print()
        print("This game was created as a demonstration of")
        print("AI-driven game development and creative writing.")
        print()
        print("Version 1.0")
        print("=" * 60)
        
        input("\nPress Enter to return to main menu...")
    
    def show_character_creation_menu(self) -> Dict[str, Any]:
        """Show character creation menu."""
        self.clear_screen()
        print("=" * 60)
        print("              CHARACTER CREATION")
        print("=" * 60)
        print()
        
        # This would be expanded in a full implementation
        # For now, it returns basic data structure
        return {
            "name": "",
            "background": "",
            "attributes": {}
        }
    
    def show_pause_menu(self) -> str:
        """Show in-game pause menu."""
        print("\n--- GAME MENU ---")
        print("1. Continue")
        print("2. Character Sheet")
        print("3. Inventory")
        print("4. Quest Log")
        print("5. Save Game")
        print("6. Load Game")
        print("7. Settings")
        print("8. Quit to Main Menu")
        
        while True:
            try:
                choice = int(input("Choose option (1-8): "))
                
                if choice == 1:
                    return "continue"
                elif choice == 2:
                    return "character_sheet"
                elif choice == 3:
                    return "inventory"
                elif choice == 4:
                    return "quest_log"
                elif choice == 5:
                    return "save_game"
                elif choice == 6:
                    return "load_game"
                elif choice == 7:
                    return "settings"
                elif choice == 8:
                    return "quit_to_menu"
                else:
                    print("Invalid choice. Please enter 1-8.")
                    
            except ValueError:
                print("Please enter a valid number.")
    
    def show_inventory_menu(self, player) -> str:
        """Show inventory management menu."""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("              INVENTORY")
            print("=" * 60)
            print()
            
            if not player.inventory:
                print("Your inventory is empty.")
            else:
                print("Items:")
                for i, item in enumerate(player.inventory):
                    print(f"{i + 1}. {item.name} x{item.quantity}")
                    if item.description:
                        print(f"   {item.description}")
                print()
            
            print(f"Capacity: {len(player.inventory)}/{player.max_inventory}")
            print()
            print("1. Use Item")
            print("2. Drop Item")
            print("3. Sort Inventory")
            print("4. Back")
            
            try:
                choice = int(input("Choose option (1-4): "))
                
                if choice == 1:
                    return "use_item"
                elif choice == 2:
                    return "drop_item"
                elif choice == 3:
                    return "sort_inventory"
                elif choice == 4:
                    return "back"
                else:
                    print("Invalid choice. Please enter 1-4.")
                    input("Press Enter to continue...")
                    
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
    
    def show_quest_log_menu(self, quest_system) -> str:
        """Show quest log menu."""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("               QUEST LOG")
            print("=" * 60)
            print()
            
            active_quests = quest_system.get_active_quests()
            completed_quests = quest_system.get_completed_quests()
            
            if active_quests:
                print("ACTIVE QUESTS:")
                for i, quest in enumerate(active_quests):
                    print(f"{i + 1}. {quest.title}")
                print()
            
            if completed_quests:
                print("COMPLETED QUESTS:")
                for quest in completed_quests[-5:]:  # Show last 5
                    print(f"✓ {quest.title}")
                print()
            
            if not active_quests and not completed_quests:
                print("No quests available.")
                print()
            
            print("1. View Quest Details")
            print("2. Back")
            
            try:
                choice = int(input("Choose option (1-2): "))
                
                if choice == 1:
                    return "view_quest_details"
                elif choice == 2:
                    return "back"
                else:
                    print("Invalid choice. Please enter 1-2.")
                    input("Press Enter to continue...")
                    
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
    
    def show_settings_menu(self) -> str:
        """Show settings menu."""
        while True:
            self.clear_screen()
            print("=" * 60)
            print("               SETTINGS")
            print("=" * 60)
            print()
            print("1. Auto-save: ON")  # Would be configurable
            print("2. Combat Speed: Normal")  # Would be configurable
            print("3. Text Speed: Normal")  # Would be configurable
            print("4. Reset Settings")
            print("5. Back")
            
            try:
                choice = int(input("Choose option (1-5): "))
                
                if choice == 1:
                    return "toggle_autosave"
                elif choice == 2:
                    return "change_combat_speed"
                elif choice == 3:
                    return "change_text_speed"
                elif choice == 4:
                    return "reset_settings"
                elif choice == 5:
                    return "back"
                else:
                    print("Invalid choice. Please enter 1-5.")
                    input("Press Enter to continue...")
                    
            except ValueError:
                print("Please enter a valid number.")
                input("Press Enter to continue...")
    
    def confirm_action(self, message: str) -> bool:
        """Show confirmation dialog."""
        print(f"\n{message}")
        while True:
            response = input("Are you sure? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'.")
    
    def show_loading_screen(self, message: str = "Loading..."):
        """Show loading screen with animation."""
        self.clear_screen()
        print("=" * 60)
        print(f"           {message}")
        print("=" * 60)
        print()
        
        # Simple loading animation
        for i in range(3):
            for dots in ["", ".", "..", "..."]:
                print(f"\r{message}{dots}    ", end="", flush=True)
                time.sleep(0.3)
        
        print()
    
    def display_narrative_text(self, text: List[str], auto_advance: bool = False):
        """Display narrative text with proper pacing."""
        for line in text:
            print(line)
            if line.strip():  # Don't pause on empty lines
                if auto_advance:
                    time.sleep(1.5)
                else:
                    input("  [Press Enter to continue...]")
            else:
                print()
    
    def format_health_bar(self, current: int, maximum: int, width: int = 20) -> str:
        """Create a visual health bar."""
        if maximum == 0:
            return "[DEAD]"
        
        ratio = current / maximum
        filled_length = int(width * ratio)
        
        bar = "█" * filled_length + "░" * (width - filled_length)
        return f"[{bar}] {current}/{maximum}"
    
    def format_stat_display(self, name: str, value: int, modifier: int = 0) -> str:
        """Format a stat display with modifier."""
        if modifier != 0:
            return f"{name}: {value} ({modifier:+d})"
        else:
            return f"{name}: {value}"
    
    def create_bordered_text(self, text: str, width: int = 60) -> str:
        """Create text with a border."""
        lines = text.split('\n')
        bordered = []
        
        # Top border
        bordered.append("╔" + "═" * (width - 2) + "╗")
        
        # Content lines
        for line in lines:
            if len(line) > width - 4:
                # Word wrap for long lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= width - 4:
                        current_line += word + " "
                    else:
                        if current_line:
                            bordered.append("║ " + current_line.ljust(width - 4) + " ║")
                        current_line = word + " "
                if current_line:
                    bordered.append("║ " + current_line.ljust(width - 4) + " ║")
            else:
                bordered.append("║ " + line.ljust(width - 4) + " ║")
        
        # Bottom border
        bordered.append("╚" + "═" * (width - 2) + "╝")
        
        return '\n'.join(bordered)
    
    def show_item_details(self, item) -> str:
        """Show detailed item information."""
        details = f"=== {item.name.upper()} ===\n"
        details += f"Type: {item.item_type.title()}\n"
        details += f"Description: {item.description}\n"
        
        if item.quantity > 1:
            details += f"Quantity: {item.quantity}\n"
        
        if item.value > 0:
            details += f"Value: {item.value} gold\n"
        
        if hasattr(item, 'stats') and item.stats:
            details += "\nStats:\n"
            for stat, value in item.stats.items():
                details += f"  {stat.title()}: {value:+d}\n"
        
        if hasattr(item, 'effects') and item.effects:
            details += "\nEffects:\n"
            for effect, value in item.effects.items():
                details += f"  {effect.title()}: {value}\n"
        
        return details
    
    def get_player_input(self, prompt: str, valid_options: List[str] = None) -> str:
        """Get validated player input."""
        while True:
            response = input(f"{prompt}: ").strip().lower()
            
            if valid_options:
                if response in valid_options:
                    return response
                print(f"Please enter one of: {', '.join(valid_options)}")
            else:
                if response:
                    return response
                print("Please enter a valid response.")
    
    def paginate_text(self, text: str, lines_per_page: int = 20):
        """Display text with pagination."""
        lines = text.split('\n')
        
        for i in range(0, len(lines), lines_per_page):
            page_lines = lines[i:i + lines_per_page]
            
            for line in page_lines:
                print(line)
            
            if i + lines_per_page < len(lines):
                input(f"\n--- Page {i // lines_per_page + 1} - Press Enter for next page ---")
                self.clear_screen()
            else:
                input(f"\n--- End - Press Enter to continue ---")