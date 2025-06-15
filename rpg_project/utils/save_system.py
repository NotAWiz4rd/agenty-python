"""
Save System for The Shattered Realms RPG.

Handles saving and loading game state.
"""

import json
import pickle
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class SaveSystem:
    """Manages game saving and loading."""
    
    def __init__(self):
        self.save_directory = Path("saves")
        self.save_directory.mkdir(exist_ok=True)
        
        self.quicksave_file = self.save_directory / "quicksave.json"
        self.autosave_file = self.save_directory / "autosave.json"
        
        # Save file format version for compatibility
        self.save_version = "1.0"
    
    def save_game(self, game_state, filename: str = None) -> bool:
        """Save the current game state."""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"save_{timestamp}.json"
            
            save_path = self.save_directory / filename
            
            # Convert game state to serializable format
            save_data = self.serialize_game_state(game_state)
            
            # Add metadata
            save_data["metadata"] = {
                "save_version": self.save_version,
                "timestamp": datetime.now().isoformat(),
                "player_name": game_state.player.name if game_state.player else "Unknown",
                "player_level": game_state.player.level if game_state.player else 1,
                "location": game_state.current_location.name if game_state.current_location else "Unknown",
                "play_time": game_state.turn_count,
            }
            
            # Write save file
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2, default=self.json_serializer)
            
            print(f"Game saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str = None) -> bool:
        """Load a game state."""
        try:
            if filename is None:
                # Load most recent save
                save_files = list(self.save_directory.glob("save_*.json"))
                if not save_files:
                    return False
                save_path = max(save_files, key=os.path.getctime)
            else:
                save_path = self.save_directory / filename
            
            if not save_path.exists():
                print(f"Save file {filename} not found.")
                return False
            
            # Load save data
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Check version compatibility
            if "metadata" in save_data:
                save_version = save_data["metadata"].get("save_version", "unknown")
                if save_version != self.save_version:
                    print(f"Warning: Save file version {save_version} may not be compatible with current version {self.save_version}")
            
            # Deserialize game state
            game_state = self.deserialize_game_state(save_data)
            
            print(f"Game loaded from {save_path.name}")
            return True
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return False
    
    def quick_save(self, game_state) -> bool:
        """Quick save the game."""
        try:
            save_data = self.serialize_game_state(game_state)
            save_data["metadata"] = {
                "save_version": self.save_version,
                "timestamp": datetime.now().isoformat(),
                "save_type": "quicksave"
            }
            
            with open(self.quicksave_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=self.json_serializer)
            
            return True
            
        except Exception as e:
            print(f"Quick save failed: {e}")
            return False
    
    def auto_save(self, game_state) -> bool:
        """Auto save the game."""
        try:
            save_data = self.serialize_game_state(game_state)
            save_data["metadata"] = {
                "save_version": self.save_version,
                "timestamp": datetime.now().isoformat(),
                "save_type": "autosave"
            }
            
            with open(self.autosave_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=self.json_serializer)
            
            return True
            
        except Exception as e:
            # Auto save failures should be silent
            return False
    
    def serialize_game_state(self, game_state) -> Dict[str, Any]:
        """Convert game state to serializable format."""
        data = {}
        
        # Player data
        if game_state.player:
            data["player"] = self.serialize_character(game_state.player)
        
        # Current location
        if game_state.current_location:
            data["current_location"] = game_state.current_location.location_id
        
        # Game state
        data["game_state"] = {
            "turn_count": game_state.turn_count,
            "time_of_day": game_state.time_of_day,
            "day_count": game_state.day_count,
            "game_flags": game_state.game_flags,
        }
        
        # World state
        if game_state.world:
            data["world"] = {
                "global_flags": game_state.world.global_flags,
                "world_time": game_state.world.world_time,
                "weather": game_state.world.weather,
                "void_storm_intensity": game_state.world.void_storm_intensity,
            }
        
        # Quest system state (if available)
        if hasattr(game_state.world, 'quest_system') and game_state.world.quest_system:
            data["quests"] = self.serialize_quest_system(game_state.world.quest_system)
        
        return data
    
    def serialize_character(self, character) -> Dict[str, Any]:
        """Serialize a character object."""
        data = {
            "name": character.name,
            "level": character.level,
            "experience": character.experience,
            "experience_to_next": character.experience_to_next,
            "current_health": character.current_health,
            "max_health": character.max_health,
            "current_magic": character.current_magic,
            "max_magic": character.max_magic,
            "corruption_level": character.corruption_level,
            "max_corruption": character.max_corruption,
        }
        
        # Attributes
        data["attributes"] = {attr.value: value for attr, value in character.attributes.items()}
        
        # Crystal attunements
        data["crystal_attunements"] = {crystal.value: level for crystal, level in character.crystal_attunements.items()}
        
        # Inventory
        data["inventory"] = []
        for item in character.inventory:
            item_data = {
                "name": item.name,
                "item_type": item.item_type,
                "description": item.description,
                "quantity": item.quantity,
                "value": item.value,
                "weight": item.weight,
            }
            if hasattr(item, 'stats') and item.stats:
                item_data["stats"] = item.stats
            if hasattr(item, 'effects') and item.effects:
                item_data["effects"] = item.effects
            if hasattr(item, 'crystal_type') and item.crystal_type:
                item_data["crystal_type"] = item.crystal_type.value
                item_data["crystal_power"] = item.crystal_power
                item_data["crystal_purity"] = item.crystal_purity
            
            data["inventory"].append(item_data)
        
        # Player-specific data
        if hasattr(character, 'titles'):
            data["titles"] = character.titles
        if hasattr(character, 'story_flags'):
            data["story_flags"] = character.story_flags
        if hasattr(character, 'faction_reputation'):
            data["faction_reputation"] = character.faction_reputation
        if hasattr(character, 'memory_fragments'):
            data["memory_fragments"] = character.memory_fragments
        if hasattr(character, 'harmony_crystal_knowledge'):
            data["harmony_crystal_knowledge"] = character.harmony_crystal_knowledge
        
        return data
    
    def serialize_quest_system(self, quest_system) -> Dict[str, Any]:
        """Serialize quest system state."""
        data = {
            "active_quests": [],
            "completed_quests": [],
            "failed_quests": []
        }
        
        # Active quests
        for quest in quest_system.active_quests:
            quest_data = {
                "quest_id": quest.quest_id,
                "status": quest.status.value,
                "current_objective_index": quest.current_objective_index,
                "quest_flags": quest.quest_flags,
                "quest_data": quest.quest_data,
            }
            
            # Objective progress
            quest_data["objectives"] = []
            for obj in quest.objectives:
                obj_data = {
                    "objective_id": obj.objective_id,
                    "current_progress": obj.current_progress,
                    "completed": obj.completed,
                    "used": getattr(obj, 'used', False)
                }
                quest_data["objectives"].append(obj_data)
            
            data["active_quests"].append(quest_data)
        
        # Completed quests (just IDs)
        data["completed_quests"] = [quest.quest_id for quest in quest_system.completed_quests]
        
        # Failed quests (just IDs)
        data["failed_quests"] = [quest.quest_id for quest in quest_system.failed_quests]
        
        return data
    
    def deserialize_game_state(self, data: Dict[str, Any]):
        """Convert serialized data back to game state."""
        # This would be implemented to reconstruct the game state
        # from the saved data. For now, just a placeholder.
        print("Game state deserialization not fully implemented yet.")
        return None
    
    def json_serializer(self, obj):
        """Custom JSON serializer for unsupported types."""
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Custom objects
            return obj.__dict__
        else:
            return str(obj)
    
    def get_save_files(self) -> List[Dict[str, Any]]:
        """Get list of available save files."""
        save_files = []
        
        for save_path in self.save_directory.glob("save_*.json"):
            try:
                with open(save_path, 'r') as f:
                    save_data = json.load(f)
                
                metadata = save_data.get("metadata", {})
                
                file_info = {
                    "filename": save_path.name,
                    "path": save_path,
                    "timestamp": metadata.get("timestamp", "Unknown"),
                    "player_name": metadata.get("player_name", "Unknown"),
                    "player_level": metadata.get("player_level", 1),
                    "location": metadata.get("location", "Unknown"),
                    "play_time": metadata.get("play_time", 0),
                }
                
                save_files.append(file_info)
                
            except Exception as e:
                print(f"Error reading save file {save_path.name}: {e}")
        
        return sorted(save_files, key=lambda x: x["timestamp"], reverse=True)
    
    def delete_save_file(self, filename: str) -> bool:
        """Delete a save file."""
        try:
            save_path = self.save_directory / filename
            if save_path.exists():
                save_path.unlink()
                print(f"Save file {filename} deleted.")
                return True
            else:
                print(f"Save file {filename} not found.")
                return False
        except Exception as e:
            print(f"Failed to delete save file: {e}")
            return False
    
    def export_save(self, filename: str, export_path: str) -> bool:
        """Export a save file to another location."""
        try:
            source = self.save_directory / filename
            destination = Path(export_path)
            
            if not source.exists():
                print(f"Save file {filename} not found.")
                return False
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(source, destination)
            
            print(f"Save file exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"Failed to export save file: {e}")
            return False
    
    def import_save(self, import_path: str) -> bool:
        """Import a save file from another location."""
        try:
            source = Path(import_path)
            
            if not source.exists():
                print(f"Import file {import_path} not found.")
                return False
            
            # Validate it's a valid save file
            with open(source, 'r') as f:
                save_data = json.load(f)
            
            if "metadata" not in save_data:
                print("Invalid save file format.")
                return False
            
            # Copy to save directory
            destination = self.save_directory / source.name
            import shutil
            shutil.copy2(source, destination)
            
            print(f"Save file imported as {destination.name}")
            return True
            
        except Exception as e:
            print(f"Failed to import save file: {e}")
            return False