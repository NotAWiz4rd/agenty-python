"""
Character system for The Shattered Realms RPG.

Defines the Player Character and NPC classes, including attributes,
skills, equipment, and progression mechanics.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class CrystalType(Enum):
    """Types of magical crystals in the game."""
    FLAME = "flame"
    FROST = "frost"
    LIFE = "life"
    SHADOW = "shadow"
    STORM = "storm"
    MIND = "mind"


class Attribute(Enum):
    """Character attributes."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class Character:
    """Base character class for both players and NPCs."""
    
    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.experience = 0
        self.experience_to_next = 100
        
        # Basic attributes (3-18 scale)
        self.attributes = {
            Attribute.STRENGTH: 10,
            Attribute.DEXTERITY: 10,
            Attribute.CONSTITUTION: 10,
            Attribute.INTELLIGENCE: 10,
            Attribute.WISDOM: 10,
            Attribute.CHARISMA: 10
        }
        
        # Health and magic
        self.max_health = 20
        self.current_health = self.max_health
        self.max_magic = 10
        self.current_magic = self.max_magic
        
        # Crystal resonance system
        self.crystal_attunements = {crystal: 0 for crystal in CrystalType}
        self.corruption_level = 0
        self.max_corruption = 100
        
        # Equipment slots
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None,
            "crystal_focus": None
        }
        
        # Inventory
        self.inventory = []
        self.max_inventory = 20
        
        # Reputation and relationships
        self.faction_reputation = {}
        self.character_relationships = {}
        
        # Combat stats (calculated from attributes)
        self.update_derived_stats()
    
    def update_derived_stats(self):
        """Update calculated stats based on attributes."""
        # Health based on Constitution
        self.max_health = 20 + (self.get_attribute_modifier(Attribute.CONSTITUTION) * 2)
        
        # Magic based on Intelligence and Wisdom
        int_mod = self.get_attribute_modifier(Attribute.INTELLIGENCE)
        wis_mod = self.get_attribute_modifier(Attribute.WISDOM)
        self.max_magic = 10 + int_mod + wis_mod
        
        # Ensure current values don't exceed max
        self.current_health = min(self.current_health, self.max_health)
        self.current_magic = min(self.current_magic, self.max_magic)
    
    def get_attribute_modifier(self, attribute: Attribute) -> int:
        """Get the modifier for an attribute (standard D&D style)."""
        return (self.attributes[attribute] - 10) // 2
    
    def add_experience(self, amount: int):
        """Add experience and handle level ups."""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Handle character level up."""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.2)  # Exponential growth
        
        # Gain attribute points
        available_points = 2
        print(f"\n{self.name} has reached level {self.level}!")
        print(f"You have {available_points} attribute points to distribute.")
        
        # In a real implementation, this would be handled by the UI
        # For now, just distribute randomly for NPCs
        if isinstance(self, PlayerCharacter):
            self.distribute_attribute_points(available_points)
        else:
            self.auto_distribute_attributes(available_points)
        
        # Update derived stats
        self.update_derived_stats()
        
        # Full heal on level up
        self.current_health = self.max_health
        self.current_magic = self.max_magic
    
    def auto_distribute_attributes(self, points: int):
        """Automatically distribute attribute points (for NPCs)."""
        attributes = list(Attribute)
        for _ in range(points):
            attr = random.choice(attributes)
            if self.attributes[attr] < 18:
                self.attributes[attr] += 1
    
    def attune_crystal(self, crystal_type: CrystalType, power: int) -> bool:
        """Attempt to attune to a crystal type."""
        current_attunement = self.crystal_attunements[crystal_type]
        new_attunement = current_attunement + power
        
        # Check corruption risk
        corruption_risk = self.calculate_corruption_risk(crystal_type, power)
        
        if random.randint(1, 100) <= corruption_risk:
            self.add_corruption(power)
            return False
        
        self.crystal_attunements[crystal_type] = min(new_attunement, 10)
        return True
    
    def calculate_corruption_risk(self, crystal_type: CrystalType, power: int) -> int:
        """Calculate the risk of corruption when using crystals."""
        base_risk = power * 5
        
        # Multiple attunements increase risk
        active_attunements = sum(1 for level in self.crystal_attunements.values() if level > 0)
        if active_attunements > 1:
            base_risk += (active_attunements - 1) * 10
        
        # Current corruption level affects risk
        corruption_modifier = self.corruption_level // 10
        base_risk += corruption_modifier
        
        # Wisdom reduces risk
        wisdom_modifier = self.get_attribute_modifier(Attribute.WISDOM)
        base_risk -= wisdom_modifier * 2
        
        return max(0, min(95, base_risk))
    
    def add_corruption(self, amount: int):
        """Add corruption to the character."""
        self.corruption_level = min(self.corruption_level + amount, self.max_corruption)
        
        if self.corruption_level >= self.max_corruption:
            print(f"{self.name} has been overcome by corruption!")
            # Handle corruption effects
    
    def heal(self, amount: int):
        """Heal the character."""
        self.current_health = min(self.current_health + amount, self.max_health)
    
    def restore_magic(self, amount: int):
        """Restore magic points."""
        self.current_magic = min(self.current_magic + amount, self.max_magic)
    
    def take_damage(self, amount: int):
        """Take damage."""
        self.current_health = max(0, self.current_health - amount)
    
    def use_magic(self, amount: int) -> bool:
        """Use magic points."""
        if self.current_magic >= amount:
            self.current_magic -= amount
            return True
        return False
    
    def is_alive(self) -> bool:
        """Check if character is alive."""
        return self.current_health > 0
    
    def get_status(self) -> str:
        """Get character status string."""
        status = []
        
        # Health status
        health_pct = (self.current_health / self.max_health) * 100
        if health_pct > 75:
            status.append("Healthy")
        elif health_pct > 50:
            status.append("Wounded")
        elif health_pct > 25:
            status.append("Badly Wounded")
        else:
            status.append("Critical")
        
        # Corruption status
        if self.corruption_level > 80:
            status.append("Heavily Corrupted")
        elif self.corruption_level > 50:
            status.append("Corrupted")
        elif self.corruption_level > 25:
            status.append("Slightly Corrupted")
        
        return ", ".join(status) if status else "Normal"


class PlayerCharacter(Character):
    """Player character class with additional features."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.is_player = True
        self.titles = ["The Unnamed"]
        self.origin_story = ""
        self.moral_alignment = {"order": 0, "chaos": 0, "good": 0, "evil": 0}
        self.story_flags = {}
        self.current_location = "aethros_arrival"
        
        # Player-specific attributes
        self.resonance_walker_level = 1  # Special ability level
        self.memory_fragments = []  # Recovered memories
        self.harmony_crystal_knowledge = 0  # Understanding of harmony crystals
    
    def distribute_attribute_points(self, points: int):
        """Allow player to distribute attribute points."""
        # This would be handled by the UI system
        # For now, just print what would happen
        print(f"Distributing {points} attribute points...")
        # In actual implementation, this would call the UI
    
    def add_title(self, title: str):
        """Add a new title to the character."""
        if title not in self.titles:
            self.titles.append(title)
            print(f"You have earned the title: {title}")
    
    def modify_alignment(self, order: int = 0, chaos: int = 0, good: int = 0, evil: int = 0):
        """Modify character's moral alignment."""
        self.moral_alignment["order"] += order
        self.moral_alignment["chaos"] += chaos
        self.moral_alignment["good"] += good
        self.moral_alignment["evil"] += evil
    
    def add_memory_fragment(self, fragment: dict):
        """Add a recovered memory fragment."""
        self.memory_fragments.append(fragment)
        print(f"You remember: {fragment.get('description', 'Something important')}")
    
    def set_story_flag(self, flag: str, value: bool = True):
        """Set a story flag."""
        self.story_flags[flag] = value
    
    def get_story_flag(self, flag: str) -> bool:
        """Get a story flag."""
        return self.story_flags.get(flag, False)
    
    def get_primary_title(self) -> str:
        """Get the character's primary title."""
        return self.titles[-1] if self.titles else "The Unnamed"
    
    def get_character_sheet(self) -> str:
        """Get formatted character sheet."""
        sheet = f"""
=== CHARACTER SHEET ===
Name: {self.name}
Title: {self.get_primary_title()}
Level: {self.level}
Experience: {self.experience}/{self.experience_to_next}

ATTRIBUTES:
Strength: {self.attributes[Attribute.STRENGTH]} ({self.get_attribute_modifier(Attribute.STRENGTH):+d})
Dexterity: {self.attributes[Attribute.DEXTERITY]} ({self.get_attribute_modifier(Attribute.DEXTERITY):+d})
Constitution: {self.attributes[Attribute.CONSTITUTION]} ({self.get_attribute_modifier(Attribute.CONSTITUTION):+d})
Intelligence: {self.attributes[Attribute.INTELLIGENCE]} ({self.get_attribute_modifier(Attribute.INTELLIGENCE):+d})
Wisdom: {self.attributes[Attribute.WISDOM]} ({self.get_attribute_modifier(Attribute.WISDOM):+d})
Charisma: {self.attributes[Attribute.CHARISMA]} ({self.get_attribute_modifier(Attribute.CHARISMA):+d})

VITALS:
Health: {self.current_health}/{self.max_health}
Magic: {self.current_magic}/{self.max_magic}
Corruption: {self.corruption_level}/{self.max_corruption}

CRYSTAL ATTUNEMENTS:
"""
        for crystal, level in self.crystal_attunements.items():
            if level > 0:
                sheet += f"{crystal.value.title()}: {level}/10\n"
        
        sheet += f"\nStatus: {self.get_status()}"
        
        return sheet


class NPC(Character):
    """Non-player character class."""
    
    def __init__(self, name: str, npc_type: str, level: int = 1):
        super().__init__(name, level)
        self.npc_type = npc_type  # "merchant", "guard", "noble", etc.
        self.disposition = 50  # 0-100, how they feel about the player
        self.dialogue_state = "initial"
        self.quests_available = []
        self.faction_affiliation = None
        self.location = None
        
        # NPC-specific attributes
        self.conversation_topics = []
        self.trade_inventory = []
        self.services_offered = []
    
    def modify_disposition(self, change: int):
        """Modify NPC's disposition toward the player."""
        self.disposition = max(0, min(100, self.disposition + change))
    
    def get_disposition_text(self) -> str:
        """Get text description of NPC's disposition."""
        if self.disposition >= 80:
            return "Friendly"
        elif self.disposition >= 60:
            return "Positive"
        elif self.disposition >= 40:
            return "Neutral"
        elif self.disposition >= 20:
            return "Unfriendly"
        else:
            return "Hostile"


def create_character_from_template(template: dict) -> Character:
    """Create a character from a template dictionary."""
    char_type = template.get("type", "npc")
    name = template.get("name", "Unknown")
    level = template.get("level", 1)
    
    if char_type == "player":
        character = PlayerCharacter(name)
    else:
        npc_type = template.get("npc_type", "civilian")
        character = NPC(name, npc_type, level)
    
    # Set attributes if provided
    if "attributes" in template:
        for attr_name, value in template["attributes"].items():
            if hasattr(Attribute, attr_name.upper()):
                character.attributes[Attribute[attr_name.upper()]] = value
    
    # Set other properties
    if "crystal_attunements" in template:
        for crystal_name, level in template["crystal_attunements"].items():
            if hasattr(CrystalType, crystal_name.upper()):
                character.crystal_attunements[CrystalType[crystal_name.upper()]] = level
    
    character.update_derived_stats()
    return character