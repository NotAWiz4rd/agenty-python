"""
Combat System for The Shattered Realms RPG.

Handles turn-based combat, including actions, damage calculation,
and crystal magic integration.
"""

import random
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from game.character import Character, PlayerCharacter, NPC, CrystalType, Attribute


class ActionType(Enum):
    """Types of combat actions."""
    ATTACK = "attack"
    DEFEND = "defend"
    MAGIC = "magic"
    ITEM = "item"
    FLEE = "flee"


class CombatAction:
    """Represents a combat action."""
    
    def __init__(self, action_type: ActionType, actor: Character, 
                 target: Optional[Character] = None, data: Dict[str, Any] = None):
        self.action_type = action_type
        self.actor = actor
        self.target = target
        self.data = data or {}


class CombatResult:
    """Results of a combat encounter."""
    
    def __init__(self, victory: bool, participants: List[Character], 
                 experience_gained: int = 0, items_found: List = None):
        self.victory = victory
        self.participants = participants
        self.experience_gained = experience_gained
        self.items_found = items_found or []
        self.fled = False


class CombatSystem:
    """Manages combat encounters."""
    
    def __init__(self):
        self.active_combat = False
        self.combat_participants = []
        self.turn_order = []
        self.current_turn_index = 0
        self.combat_round = 0
        
        # Combat state
        self.environmental_effects = []
        self.combat_log = []
    
    def start_combat(self, player: PlayerCharacter, enemies: List[Character]) -> CombatResult:
        """Start a combat encounter."""
        self.active_combat = True
        self.combat_participants = [player] + enemies
        self.combat_round = 0
        self.combat_log = []
        
        # Determine turn order (based on Dexterity)
        self.turn_order = sorted(
            self.combat_participants,
            key=lambda char: char.attributes[Attribute.DEXTERITY] + random.randint(1, 6),
            reverse=True
        )
        
        self.current_turn_index = 0
        
        print("\n" + "=" * 50)
        print("COMBAT BEGINS!")
        print("=" * 50)
        
        # Show participants
        print("Combatants:")
        for char in self.combat_participants:
            status = "Player" if isinstance(char, PlayerCharacter) else "Enemy"
            print(f"  {char.name} ({status}) - Health: {char.current_health}/{char.max_health}")
        
        print("\nTurn order:")
        for i, char in enumerate(self.turn_order):
            print(f"  {i+1}. {char.name}")
        
        input("\nPress Enter to begin combat...")
        
        # Main combat loop
        while self.active_combat:
            result = self.process_combat_round()
            if result:
                return result
        
        # This shouldn't be reached, but just in case
        return CombatResult(False, self.combat_participants)
    
    def process_combat_round(self) -> Optional[CombatResult]:
        """Process a single combat round."""
        self.combat_round += 1
        print(f"\n--- ROUND {self.combat_round} ---")
        
        for turn_index in range(len(self.turn_order)):
            current_character = self.turn_order[turn_index]
            
            # Skip dead characters
            if not current_character.is_alive():
                continue
            
            print(f"\n{current_character.name}'s turn:")
            
            # Get action
            if isinstance(current_character, PlayerCharacter):
                action = self.get_player_action(current_character)
            else:
                action = self.get_ai_action(current_character)
            
            # Process action
            action_result = self.process_action(action)
            
            # Check for combat end conditions
            end_result = self.check_combat_end()
            if end_result:
                return end_result
            
            # Brief pause between turns
            if not isinstance(current_character, PlayerCharacter):
                input("Press Enter to continue...")
        
        # Apply end-of-round effects
        self.apply_round_end_effects()
        
        return None
    
    def get_player_action(self, player: PlayerCharacter) -> CombatAction:
        """Get action from player."""
        while True:
            print(f"\nHealth: {player.current_health}/{player.max_health}")
            print(f"Magic: {player.current_magic}/{player.max_magic}")
            
            print("\nAvailable actions:")
            print("1. Attack")
            print("2. Defend")
            print("3. Use Magic")
            print("4. Use Item")
            print("5. Flee")
            
            try:
                choice = int(input("Choose action (1-5): "))
                
                if choice == 1:
                    target = self.select_target(player, "enemy")
                    if target:
                        return CombatAction(ActionType.ATTACK, player, target)
                
                elif choice == 2:
                    return CombatAction(ActionType.DEFEND, player)
                
                elif choice == 3:
                    magic_action = self.select_magic_action(player)
                    if magic_action:
                        return magic_action
                
                elif choice == 4:
                    item_action = self.select_item_action(player)
                    if item_action:
                        return item_action
                
                elif choice == 5:
                    return CombatAction(ActionType.FLEE, player)
                
                else:
                    print("Invalid choice. Please choose 1-5.")
                    
            except ValueError:
                print("Please enter a valid number.")
    
    def get_ai_action(self, npc: Character) -> CombatAction:
        """Get AI action for NPC."""
        # Simple AI logic
        alive_enemies = [char for char in self.combat_participants 
                        if char.is_alive() and isinstance(char, PlayerCharacter)]
        
        if not alive_enemies:
            return CombatAction(ActionType.DEFEND, npc)
        
        # Basic AI decision making
        if npc.current_health < npc.max_health * 0.3:
            # Try to flee or defend when low on health
            if random.random() < 0.3:
                return CombatAction(ActionType.FLEE, npc)
            else:
                return CombatAction(ActionType.DEFEND, npc)
        
        # Use magic if available and suitable
        if npc.current_magic > 5 and random.random() < 0.4:
            target = random.choice(alive_enemies)
            magic_type = random.choice(list(CrystalType))
            return CombatAction(ActionType.MAGIC, npc, target, 
                              {"crystal_type": magic_type, "power": 2})
        
        # Default to attack
        target = random.choice(alive_enemies)
        return CombatAction(ActionType.ATTACK, npc, target)
    
    def select_target(self, actor: Character, target_type: str) -> Optional[Character]:
        """Select a combat target."""
        if target_type == "enemy":
            targets = [char for char in self.combat_participants 
                      if char.is_alive() and char != actor and not isinstance(char, type(actor))]
        else:  # ally
            targets = [char for char in self.combat_participants 
                      if char.is_alive() and isinstance(char, type(actor))]
        
        if not targets:
            print("No valid targets available.")
            return None
        
        if len(targets) == 1:
            return targets[0]
        
        print("Select target:")
        for i, target in enumerate(targets):
            health_bar = self.get_health_bar(target)
            print(f"{i+1}. {target.name} {health_bar}")
        
        while True:
            try:
                choice = int(input(f"Choose target (1-{len(targets)}): ")) - 1
                if 0 <= choice < len(targets):
                    return targets[choice]
                print(f"Please choose a number between 1 and {len(targets)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def select_magic_action(self, player: PlayerCharacter) -> Optional[CombatAction]:
        """Select a magic action."""
        available_crystals = [(crystal, level) for crystal, level in player.crystal_attunements.items() 
                             if level > 0]
        
        if not available_crystals:
            print("You have no crystal attunements.")
            return None
        
        print("Available crystal magic:")
        for i, (crystal, level) in enumerate(available_crystals):
            magic_cost = 3
            print(f"{i+1}. {crystal.value.title()} Magic (Level {level}, Cost: {magic_cost} MP)")
        
        try:
            choice = int(input(f"Choose magic (1-{len(available_crystals)}): ")) - 1
            if 0 <= choice < len(available_crystals):
                crystal, level = available_crystals[choice]
                
                # Select power level
                max_power = min(level, player.current_magic // 3)
                if max_power == 0:
                    print("Not enough magic points.")
                    return None
                
                power = 1
                if max_power > 1:
                    power = int(input(f"Power level (1-{max_power}): ") or "1")
                    power = max(1, min(power, max_power))
                
                # Select target based on magic type
                if crystal in [CrystalType.FLAME, CrystalType.FROST, CrystalType.STORM, CrystalType.SHADOW]:
                    target = self.select_target(player, "enemy")
                else:  # Life and Mind magic can target allies
                    print("1. Target enemy")
                    print("2. Target ally")
                    choice = int(input("Choose (1-2): ") or "1")
                    target_type = "enemy" if choice == 1 else "ally"
                    target = self.select_target(player, target_type)
                
                if target:
                    return CombatAction(ActionType.MAGIC, player, target,
                                      {"crystal_type": crystal, "power": power})
        
        except ValueError:
            pass
        
        return None
    
    def select_item_action(self, player: PlayerCharacter) -> Optional[CombatAction]:
        """Select an item to use."""
        usable_items = [item for item in player.inventory 
                       if item.item_type in ["consumable", "magic"]]
        
        if not usable_items:
            print("You have no usable items.")
            return None
        
        print("Available items:")
        for i, item in enumerate(usable_items):
            print(f"{i+1}. {item.name} x{item.quantity}")
        
        try:
            choice = int(input(f"Choose item (1-{len(usable_items)}): ")) - 1
            if 0 <= choice < len(usable_items):
                item = usable_items[choice]
                return CombatAction(ActionType.ITEM, player, player, {"item": item})
        except ValueError:
            pass
        
        return None
    
    def process_action(self, action: CombatAction) -> Dict[str, Any]:
        """Process a combat action."""
        result = {"success": False, "message": "", "damage": 0}
        
        if action.action_type == ActionType.ATTACK:
            result = self.process_attack(action)
        elif action.action_type == ActionType.DEFEND:
            result = self.process_defend(action)
        elif action.action_type == ActionType.MAGIC:
            result = self.process_magic(action)
        elif action.action_type == ActionType.ITEM:
            result = self.process_item_use(action)
        elif action.action_type == ActionType.FLEE:
            result = self.process_flee(action)
        
        # Log the action
        self.combat_log.append(result["message"])
        print(result["message"])
        
        return result
    
    def process_attack(self, action: CombatAction) -> Dict[str, Any]:
        """Process an attack action."""
        attacker = action.actor
        target = action.target
        
        # Calculate hit chance
        hit_chance = 70  # Base hit chance
        hit_chance += attacker.get_attribute_modifier(Attribute.DEXTERITY) * 5
        hit_chance -= target.get_attribute_modifier(Attribute.DEXTERITY) * 3
        
        # Roll for hit
        roll = random.randint(1, 100)
        
        if roll > hit_chance:
            return {"success": False, "message": f"{attacker.name} attacks {target.name} but misses!", "damage": 0}
        
        # Calculate damage
        base_damage = 5 + attacker.get_attribute_modifier(Attribute.STRENGTH)
        damage = max(1, base_damage + random.randint(1, 6))
        
        # Apply damage
        target.take_damage(damage)
        
        message = f"{attacker.name} attacks {target.name} for {damage} damage!"
        if not target.is_alive():
            message += f" {target.name} is defeated!"
        
        return {"success": True, "message": message, "damage": damage}
    
    def process_defend(self, action: CombatAction) -> Dict[str, Any]:
        """Process a defend action."""
        defender = action.actor
        
        # Defending provides temporary bonuses for the rest of the round
        # This would be tracked in a more complete implementation
        
        # Recover some magic
        defender.restore_magic(2)
        
        message = f"{defender.name} takes a defensive stance and recovers 2 MP."
        return {"success": True, "message": message, "damage": 0}
    
    def process_magic(self, action: CombatAction) -> Dict[str, Any]:
        """Process a magic action."""
        caster = action.actor
        target = action.target
        crystal_type = action.data["crystal_type"]
        power = action.data["power"]
        
        magic_cost = power * 3
        
        # Check if caster has enough magic
        if not caster.use_magic(magic_cost):
            return {"success": False, "message": f"{caster.name} doesn't have enough magic!", "damage": 0}
        
        # Check for corruption
        if not caster.attune_crystal(crystal_type, power):
            corruption_message = f"{caster.name} suffers magical corruption!"
            return {"success": False, "message": corruption_message, "damage": 0}
        
        # Apply magic effects
        if crystal_type == CrystalType.FLAME:
            damage = power * 8 + random.randint(1, 6)
            target.take_damage(damage)
            message = f"{caster.name} unleashes flame magic at {target.name} for {damage} damage!"
        
        elif crystal_type == CrystalType.FROST:
            damage = power * 6 + random.randint(1, 4)
            target.take_damage(damage)
            # Could add slow effect here
            message = f"{caster.name} strikes {target.name} with frost magic for {damage} damage!"
        
        elif crystal_type == CrystalType.LIFE:
            healing = power * 10 + random.randint(1, 8)
            target.heal(healing)
            message = f"{caster.name} heals {target.name} for {healing} health!"
        
        elif crystal_type == CrystalType.SHADOW:
            damage = power * 7 + random.randint(1, 5)
            target.take_damage(damage)
            # Could add fear effect here
            message = f"{caster.name} strikes {target.name} with shadow magic for {damage} damage!"
        
        elif crystal_type == CrystalType.STORM:
            damage = power * 9 + random.randint(1, 7)
            target.take_damage(damage)
            # Could add stun chance here
            message = f"{caster.name} blasts {target.name} with storm magic for {damage} damage!"
        
        elif crystal_type == CrystalType.MIND:
            # Mind magic could have various effects
            if target == caster:
                # Self-buff
                caster.restore_magic(power * 5)
                message = f"{caster.name} uses mind magic to restore {power * 5} MP!"
            else:
                # Confusion or damage
                damage = power * 5 + random.randint(1, 3)
                target.take_damage(damage)
                message = f"{caster.name} assaults {target.name}'s mind for {damage} damage!"
        
        if not target.is_alive() and crystal_type != CrystalType.LIFE:
            message += f" {target.name} is defeated!"
        
        return {"success": True, "message": message, "damage": damage if crystal_type != CrystalType.LIFE else 0}
    
    def process_item_use(self, action: CombatAction) -> Dict[str, Any]:
        """Process item use action."""
        user = action.actor
        item = action.data["item"]
        
        # Simple item effects
        if "healing" in item.name.lower() or "potion" in item.name.lower():
            healing = 15 + random.randint(1, 10)
            user.heal(healing)
            message = f"{user.name} uses {item.name} and recovers {healing} health!"
        elif "magic" in item.name.lower() or "mana" in item.name.lower():
            magic_restore = 10 + random.randint(1, 5)
            user.restore_magic(magic_restore)
            message = f"{user.name} uses {item.name} and recovers {magic_restore} magic!"
        else:
            message = f"{user.name} uses {item.name}."
        
        # Remove item from inventory
        item.quantity -= 1
        if item.quantity <= 0:
            user.inventory.remove(item)
        
        return {"success": True, "message": message, "damage": 0}
    
    def process_flee(self, action: CombatAction) -> Dict[str, Any]:
        """Process flee action."""
        fleeing_character = action.actor
        
        # Calculate flee chance based on Dexterity
        flee_chance = 50 + fleeing_character.get_attribute_modifier(Attribute.DEXTERITY) * 10
        
        if random.randint(1, 100) <= flee_chance:
            message = f"{fleeing_character.name} successfully flees from combat!"
            
            # Remove from combat if it's the player
            if isinstance(fleeing_character, PlayerCharacter):
                self.active_combat = False
                self.flee_result = True
            
            return {"success": True, "message": message, "damage": 0}
        else:
            message = f"{fleeing_character.name} tries to flee but can't escape!"
            return {"success": False, "message": message, "damage": 0}
    
    def check_combat_end(self) -> Optional[CombatResult]:
        """Check if combat should end."""
        alive_players = [char for char in self.combat_participants 
                        if char.is_alive() and isinstance(char, PlayerCharacter)]
        alive_enemies = [char for char in self.combat_participants 
                        if char.is_alive() and not isinstance(char, PlayerCharacter)]
        
        # Check for player defeat
        if not alive_players:
            print("\n" + "=" * 50)
            print("DEFEAT!")
            print("=" * 50)
            print("You have been defeated in combat.")
            return CombatResult(False, self.combat_participants)
        
        # Check for victory
        if not alive_enemies:
            print("\n" + "=" * 50)
            print("VICTORY!")
            print("=" * 50)
            
            # Calculate experience
            experience = sum(enemy.level * 10 for enemy in self.combat_participants 
                           if not enemy.is_alive() and not isinstance(enemy, PlayerCharacter))
            
            # Award experience
            for player in alive_players:
                player.add_experience(experience)
                print(f"{player.name} gains {experience} experience!")
            
            self.active_combat = False
            return CombatResult(True, self.combat_participants, experience)
        
        # Check for flee
        if hasattr(self, 'flee_result') and self.flee_result:
            result = CombatResult(False, self.combat_participants)
            result.fled = True
            return result
        
        return None
    
    def apply_round_end_effects(self):
        """Apply effects at the end of each round."""
        # Apply any ongoing effects like poison, regeneration, etc.
        for char in self.combat_participants:
            if char.is_alive():
                # Natural magic regeneration
                if char.current_magic < char.max_magic:
                    char.restore_magic(1)
    
    def get_health_bar(self, character: Character) -> str:
        """Get a visual health bar for a character."""
        if character.max_health == 0:
            return "[DEAD]"
        
        health_pct = character.current_health / character.max_health
        bar_length = 10
        filled_length = int(bar_length * health_pct)
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        return f"[{bar}] {character.current_health}/{character.max_health}"