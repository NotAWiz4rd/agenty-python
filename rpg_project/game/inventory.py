"""
Inventory System for The Shattered Realms RPG.

Manages items, equipment, and inventory operations.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from game.character import CrystalType, Attribute


class ItemType(Enum):
    """Types of items in the game."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    CRYSTAL = "crystal"
    MATERIAL = "material"
    ITEM = "item"  # Generic items


class Item:
    """Represents an item in the game."""
    
    def __init__(self, name: str, item_type: str, description: str, quantity: int = 1):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.quantity = quantity
        self.value = 0  # Base value for trading
        self.weight = 1  # Weight for inventory management
        
        # Item properties
        self.properties = {}
        self.requirements = {}
        self.effects = {}
        
        # Equipment stats (for weapons/armor)
        self.stats = {}
        
        # Crystal properties (for crystal items)
        self.crystal_type = None
        self.crystal_power = 0
        self.crystal_purity = 100
    
    def can_use(self, character) -> bool:
        """Check if character can use this item."""
        # Check level requirements
        if "level" in self.requirements:
            if character.level < self.requirements["level"]:
                return False
        
        # Check attribute requirements
        for attr_name, required_value in self.requirements.items():
            if attr_name in [attr.value for attr in Attribute]:
                attr = Attribute(attr_name)
                if character.attributes[attr] < required_value:
                    return False
        
        return True
    
    def use(self, character, game_state=None) -> Dict[str, Any]:
        """Use the item on a character."""
        result = {"success": False, "message": "", "consumed": False}
        
        if not self.can_use(character):
            result["message"] = f"You cannot use {self.name}."
            return result
        
        if self.item_type == "consumable":
            result = self.use_consumable(character)
        elif self.item_type == "crystal":
            result = self.use_crystal(character)
        else:
            result["message"] = f"You cannot use {self.name} directly."
        
        return result
    
    def use_consumable(self, character) -> Dict[str, Any]:
        """Use a consumable item."""
        result = {"success": True, "message": "", "consumed": True}
        
        # Apply effects based on item name/properties
        if "healing" in self.name.lower() or "health" in self.name.lower():
            healing = self.effects.get("healing", 20)
            character.heal(healing)
            result["message"] = f"You feel refreshed and recover {healing} health."
        
        elif "magic" in self.name.lower() or "mana" in self.name.lower():
            magic_restore = self.effects.get("magic_restore", 15)
            character.restore_magic(magic_restore)
            result["message"] = f"Your magical energy is restored by {magic_restore} points."
        
        elif "antidote" in self.name.lower():
            # Remove poison effects (would need status effect system)
            result["message"] = "You feel the poison leave your system."
        
        elif "food" in self.name.lower() or "ration" in self.name.lower():
            # Provide small healing and remove hunger (if hunger system existed)
            healing = 5
            character.heal(healing)
            result["message"] = f"The food satisfies your hunger and restores {healing} health."
        
        else:
            # Generic consumable
            result["message"] = f"You consume the {self.name}."
        
        return result
    
    def use_crystal(self, character) -> Dict[str, Any]:
        """Use a crystal item."""
        result = {"success": False, "message": "", "consumed": False}
        
        if not self.crystal_type:
            result["message"] = "This crystal has no usable power."
            return result
        
        # Try to attune to the crystal
        if character.attune_crystal(self.crystal_type, self.crystal_power):
            result["success"] = True
            result["consumed"] = True
            result["message"] = f"You successfully attune to the {self.crystal_type.value} crystal!"
        else:
            result["message"] = f"You fail to attune to the {self.crystal_type.value} crystal and suffer corruption."
        
        return result
    
    def get_info(self) -> str:
        """Get detailed item information."""
        info = f"{self.name}\n"
        info += f"Type: {self.item_type.title()}\n"
        info += f"Description: {self.description}\n"
        
        if self.value > 0:
            info += f"Value: {self.value} gold\n"
        
        if self.requirements:
            info += "Requirements:\n"
            for req, value in self.requirements.items():
                info += f"  {req.title()}: {value}\n"
        
        if self.stats:
            info += "Stats:\n"
            for stat, value in self.stats.items():
                info += f"  {stat.title()}: {value:+d}\n"
        
        if self.crystal_type:
            info += f"Crystal Type: {self.crystal_type.value.title()}\n"
            info += f"Crystal Power: {self.crystal_power}\n"
            info += f"Purity: {self.crystal_purity}%\n"
        
        return info


class Equipment:
    """Manages a character's equipped items."""
    
    def __init__(self):
        self.slots = {
            "weapon": None,
            "armor": None,
            "accessory": None,
            "crystal_focus": None
        }
        
        # Cached stats from equipment
        self.stat_bonuses = {}
        self.special_effects = []
    
    def equip_item(self, item: Item, character) -> Dict[str, Any]:
        """Equip an item to the appropriate slot."""
        result = {"success": False, "message": "", "unequipped_item": None}
        
        if not item.can_use(character):
            result["message"] = f"You cannot equip {item.name}."
            return result
        
        # Determine slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "accessory":
            slot = "accessory"
        elif item.item_type == "crystal" and "focus" in item.name.lower():
            slot = "crystal_focus"
        
        if not slot:
            result["message"] = f"{item.name} cannot be equipped."
            return result
        
        # Unequip current item in slot
        current_item = self.slots[slot]
        if current_item:
            result["unequipped_item"] = current_item
        
        # Equip new item
        self.slots[slot] = item
        self.update_bonuses()
        
        result["success"] = True
        result["message"] = f"You equip {item.name}."
        
        return result
    
    def unequip_slot(self, slot: str) -> Optional[Item]:
        """Unequip item from specified slot."""
        if slot in self.slots and self.slots[slot]:
            item = self.slots[slot]
            self.slots[slot] = None
            self.update_bonuses()
            return item
        return None
    
    def update_bonuses(self):
        """Update stat bonuses from equipped items."""
        self.stat_bonuses = {}
        self.special_effects = []
        
        for slot, item in self.slots.items():
            if item and item.stats:
                for stat, bonus in item.stats.items():
                    self.stat_bonuses[stat] = self.stat_bonuses.get(stat, 0) + bonus
            
            if item and "effects" in item.properties:
                self.special_effects.extend(item.properties["effects"])
    
    def get_stat_bonus(self, stat: str) -> int:
        """Get total stat bonus from equipment."""
        return self.stat_bonuses.get(stat, 0)
    
    def has_effect(self, effect: str) -> bool:
        """Check if equipment provides a specific effect."""
        return effect in self.special_effects
    
    def get_equipment_list(self) -> str:
        """Get formatted list of equipped items."""
        equipment_list = "EQUIPPED ITEMS:\n"
        
        for slot, item in self.slots.items():
            slot_name = slot.replace("_", " ").title()
            if item:
                equipment_list += f"{slot_name}: {item.name}\n"
            else:
                equipment_list += f"{slot_name}: (None)\n"
        
        return equipment_list


class InventorySystem:
    """Manages inventory operations for characters."""
    
    def __init__(self):
        self.item_templates = {}
        self.create_item_templates()
    
    def create_item_templates(self):
        """Create templates for all game items."""
        # Weapons
        self.create_weapon_templates()
        
        # Armor
        self.create_armor_templates()
        
        # Consumables
        self.create_consumable_templates()
        
        # Crystals
        self.create_crystal_templates()
        
        # Quest items
        self.create_quest_templates()
        
        # Materials and misc items
        self.create_misc_templates()
    
    def create_weapon_templates(self):
        """Create weapon item templates."""
        # Basic weapons
        iron_sword = Item("Iron Sword", "weapon", "A reliable iron blade.")
        iron_sword.stats = {"attack": 8, "accuracy": 5}
        iron_sword.value = 50
        iron_sword.weight = 3
        self.item_templates["iron_sword"] = iron_sword
        
        survival_knife = Item("Survival Knife", "weapon", "A versatile tool and weapon.")
        survival_knife.stats = {"attack": 4, "accuracy": 8}
        survival_knife.value = 20
        survival_knife.weight = 1
        self.item_templates["survival_knife"] = survival_knife
        
        crystal_blade = Item("Crystal-Forged Blade", "weapon", "A sword infused with crystal energy.")
        crystal_blade.stats = {"attack": 12, "magic_power": 3}
        crystal_blade.requirements = {"level": 5}
        crystal_blade.value = 200
        crystal_blade.weight = 3
        self.item_templates["crystal_blade"] = crystal_blade
    
    def create_armor_templates(self):
        """Create armor item templates."""
        leather_armor = Item("Leather Armor", "armor", "Sturdy leather protection.")
        leather_armor.stats = {"defense": 5, "dexterity": -1}
        leather_armor.value = 40
        leather_armor.weight = 5
        self.item_templates["leather_armor"] = leather_armor
        
        scholars_robes = Item("Scholar's Robes", "armor", "Simple robes that aid concentration.")
        scholars_robes.stats = {"magic_defense": 3, "intelligence": 1}
        scholars_robes.value = 30
        scholars_robes.weight = 2
        self.item_templates["scholars_robes"] = scholars_robes
        
        fine_clothes = Item("Fine Clothes", "armor", "Well-made clothes that impress.")
        fine_clothes.stats = {"charisma": 2}
        fine_clothes.value = 60
        fine_clothes.weight = 1
        self.item_templates["fine_clothes"] = fine_clothes
        
        patched_cloak = Item("Patched Cloak", "armor", "A well-worn but serviceable cloak.")
        patched_cloak.stats = {"defense": 2, "weather_resistance": 1}
        patched_cloak.value = 15
        patched_cloak.weight = 2
        self.item_templates["patched_cloak"] = patched_cloak
    
    def create_consumable_templates(self):
        """Create consumable item templates."""
        health_potion = Item("Health Potion", "consumable", "Restores health when consumed.")
        health_potion.effects = {"healing": 25}
        health_potion.value = 30
        self.item_templates["health_potion"] = health_potion
        
        magic_potion = Item("Magic Potion", "consumable", "Restores magical energy.")
        magic_potion.effects = {"magic_restore": 20}
        magic_potion.value = 40
        self.item_templates["magic_potion"] = magic_potion
        
        basic_rations = Item("Basic Rations", "consumable", "Simple food that keeps well.")
        basic_rations.effects = {"healing": 5}
        basic_rations.value = 5
        basic_rations.quantity = 3
        self.item_templates["basic_rations"] = basic_rations
        
        emergency_supplies = Item("Emergency Supplies", "consumable", "Extra supplies for tough times.")
        emergency_supplies.effects = {"healing": 10, "magic_restore": 5}
        emergency_supplies.value = 20
        emergency_supplies.quantity = 2
        self.item_templates["emergency_supplies"] = emergency_supplies
    
    def create_crystal_templates(self):
        """Create crystal item templates."""
        for crystal_type in CrystalType:
            # Basic crystals
            basic_crystal = Item(f"Basic {crystal_type.value.title()} Crystal", "crystal",
                               f"A small {crystal_type.value} crystal with minor power.")
            basic_crystal.crystal_type = crystal_type
            basic_crystal.crystal_power = 1
            basic_crystal.value = 25
            self.item_templates[f"basic_{crystal_type.value}_crystal"] = basic_crystal
            
            # Pure crystals
            pure_crystal = Item(f"Pure {crystal_type.value.title()} Crystal", "crystal",
                              f"A high-quality {crystal_type.value} crystal.")
            pure_crystal.crystal_type = crystal_type
            pure_crystal.crystal_power = 3
            pure_crystal.crystal_purity = 95
            pure_crystal.value = 100
            self.item_templates[f"pure_{crystal_type.value}_crystal"] = pure_crystal
        
        # Special crystals
        harmony_fragment = Item("Harmony Crystal Fragment", "crystal",
                              "A fragment of the legendary Harmony Crystal.")
        harmony_fragment.crystal_power = 5
        harmony_fragment.value = 500
        self.item_templates["harmony_fragment"] = harmony_fragment
    
    def create_quest_templates(self):
        """Create quest item templates."""
        ancient_map = Item("Ancient Map Fragment", "quest",
                          "A fragment of an old map showing unknown locations.")
        ancient_map.value = 0  # Quest items have no trade value
        self.item_templates["ancient_map"] = ancient_map
        
        letter_intro = Item("Letter of Introduction", "quest",
                           "A letter from a minor noble providing introduction.")
        self.item_templates["letter_intro"] = letter_intro
        
        signet_ring = Item("Signet Ring", "accessory",
                          "A ring showing noble connections.")
        signet_ring.stats = {"charisma": 1}
        signet_ring.value = 75
        self.item_templates["signet_ring"] = signet_ring
    
    def create_misc_templates(self):
        """Create miscellaneous item templates."""
        travel_pack = Item("Travel Pack", "item", "A sturdy pack for carrying supplies.")
        travel_pack.properties = {"inventory_bonus": 5}
        travel_pack.value = 25
        self.item_templates["travel_pack"] = travel_pack
        
        water_flask = Item("Water Flask", "item", "A flask of clean water.")
        water_flask.value = 5
        self.item_templates["water_flask"] = water_flask
        
        flint_steel = Item("Flint and Steel", "item", "For starting fires.")
        flint_steel.value = 10
        self.item_templates["flint_steel"] = flint_steel
        
        crystal_analysis_kit = Item("Crystal Analysis Kit", "item",
                                   "Tools for studying crystals safely.")
        crystal_analysis_kit.value = 150
        self.item_templates["crystal_analysis_kit"] = crystal_analysis_kit
        
        shield = Item("Shield", "item", "A wooden shield reinforced with metal.")
        shield.stats = {"defense": 3, "block_chance": 10}
        shield.value = 35
        shield.weight = 4
        self.item_templates["shield"] = shield
    
    def create_item(self, template_id: str, quantity: int = 1) -> Optional[Item]:
        """Create an item from a template."""
        if template_id not in self.item_templates:
            return None
        
        template = self.item_templates[template_id]
        
        # Create a new item based on the template
        new_item = Item(template.name, template.item_type, template.description, quantity)
        new_item.value = template.value
        new_item.weight = template.weight
        new_item.properties = template.properties.copy()
        new_item.requirements = template.requirements.copy()
        new_item.effects = template.effects.copy()
        new_item.stats = template.stats.copy()
        new_item.crystal_type = template.crystal_type
        new_item.crystal_power = template.crystal_power
        new_item.crystal_purity = template.crystal_purity
        
        return new_item
    
    def add_item(self, character, item: Item) -> bool:
        """Add an item to character's inventory."""
        # Check for existing stack
        for existing_item in character.inventory:
            if (existing_item.name == item.name and 
                existing_item.item_type == item.item_type):
                existing_item.quantity += item.quantity
                return True
        
        # Check inventory space
        if len(character.inventory) >= character.max_inventory:
            return False
        
        # Add new item
        character.inventory.append(item)
        return True
    
    def remove_item(self, character, item: Item, quantity: int = 1) -> bool:
        """Remove items from character's inventory."""
        if item not in character.inventory:
            return False
        
        if item.quantity > quantity:
            item.quantity -= quantity
            return True
        elif item.quantity == quantity:
            character.inventory.remove(item)
            return True
        else:
            return False  # Not enough items
    
    def find_item(self, character, item_name: str) -> Optional[Item]:
        """Find an item in character's inventory by name."""
        item_name_lower = item_name.lower()
        for item in character.inventory:
            if item.name.lower() == item_name_lower:
                return item
            # Partial match
            if item_name_lower in item.name.lower():
                return item
        return None
    
    def get_inventory_value(self, character) -> int:
        """Get total value of character's inventory."""
        return sum(item.value * item.quantity for item in character.inventory)
    
    def get_inventory_weight(self, character) -> int:
        """Get total weight of character's inventory."""
        return sum(item.weight * item.quantity for item in character.inventory)
    
    def sort_inventory(self, character, sort_by: str = "name"):
        """Sort character's inventory."""
        if sort_by == "name":
            character.inventory.sort(key=lambda item: item.name)
        elif sort_by == "type":
            character.inventory.sort(key=lambda item: item.item_type)
        elif sort_by == "value":
            character.inventory.sort(key=lambda item: item.value, reverse=True)
        elif sort_by == "quantity":
            character.inventory.sort(key=lambda item: item.quantity, reverse=True)
        elif sort_by == "weight":
            character.inventory.sort(key=lambda item: item.weight, reverse=True)
    
    def get_item_templates(self) -> Dict[str, Item]:
        """Get all item templates."""
        return self.item_templates.copy()
    
    def get_template_by_id(self, template_id: str) -> Optional[Item]:
        """Get a specific item template by ID."""
        return self.item_templates.get(template_id)
    
    def get_items_by_type(self, character, item_type: str) -> List[Item]:
        """Get all items of a specific type from character's inventory."""
        return [item for item in character.inventory if item.item_type == item_type]
    
    def get_usable_items(self, character) -> List[Item]:
        """Get all usable items from character's inventory."""
        return [item for item in character.inventory 
                if item.item_type in ["consumable", "crystal"] and item.can_use(character)]
    
    def get_equipment_items(self, character) -> List[Item]:
        """Get all equippable items from character's inventory."""
        return [item for item in character.inventory 
                if item.item_type in ["weapon", "armor", "accessory"] and item.can_use(character)]
    
    def transfer_item(self, from_character, to_character, item: Item, quantity: int = 1) -> bool:
        """Transfer item between characters."""
        if self.remove_item(from_character, item, quantity):
            # Create new item with specified quantity
            new_item = Item(item.name, item.item_type, item.description, quantity)
            new_item.value = item.value
            new_item.weight = item.weight
            new_item.properties = item.properties.copy()
            new_item.requirements = item.requirements.copy()
            new_item.effects = item.effects.copy()
            new_item.stats = item.stats.copy()
            new_item.crystal_type = item.crystal_type
            new_item.crystal_power = item.crystal_power
            new_item.crystal_purity = item.crystal_purity
            
            return self.add_item(to_character, new_item)
        
        return False
    
    def drop_item(self, character, item: Item, quantity: int = 1, location=None) -> bool:
        """Drop item from character's inventory."""
        if self.remove_item(character, item, quantity):
            if location:
                # Create new item for location
                dropped_item = Item(item.name, item.item_type, item.description, quantity)
                dropped_item.value = item.value
                dropped_item.weight = item.weight
                dropped_item.properties = item.properties.copy()
                dropped_item.requirements = item.requirements.copy()
                dropped_item.effects = item.effects.copy()
                dropped_item.stats = item.stats.copy()
                dropped_item.crystal_type = item.crystal_type
                dropped_item.crystal_power = item.crystal_power
                dropped_item.crystal_purity = item.crystal_purity
                
                location.add_item(dropped_item)
            
            return True
        
        return False
    
    def pick_up_item(self, character, item: Item, location=None) -> bool:
        """Pick up item from location."""
        if location and item in location.items:
            if self.add_item(character, item):
                location.remove_item(item)
                return True
        
        return False
            character.inventory.sort(key=lambda item: item.quantity, reverse=True)