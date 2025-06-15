"""
World System for The Shattered Realms RPG.

Defines locations, world state, and environmental interactions.
"""

from typing import Dict, List, Optional, Any, Callable
from game.character import NPC, Character
from game.inventory import Item


class Location:
    """Represents a game location."""
    
    def __init__(self, location_id: str, name: str, description: str):
        self.location_id = location_id
        self.name = name
        self.description = description
        self.exits: Dict[str, str] = {}  # direction -> location_id
        self.npcs: List[NPC] = []
        self.items: List[Item] = []
        self.available_actions: List[str] = []
        self.environmental_effects: List[str] = []
        self.discovery_flags: Dict[str, bool] = {}
        
        # Event handlers
        self.on_enter_handlers: List[Callable] = []
        self.on_exit_handlers: List[Callable] = []
        self.action_handlers: Dict[str, Callable] = {}
        
        # Location-specific data
        self.location_data: Dict[str, Any] = {}
    
    def add_exit(self, direction: str, destination: str, bidirectional: bool = False):
        """Add an exit to another location."""
        self.exits[direction] = destination
        
        # For bidirectional exits, we'd need a reference to the world
        # This is handled by the World class
    
    def add_npc(self, npc: NPC):
        """Add an NPC to this location."""
        self.npcs.append(npc)
        npc.location = self.location_id
    
    def remove_npc(self, npc: NPC):
        """Remove an NPC from this location."""
        if npc in self.npcs:
            self.npcs.remove(npc)
            npc.location = None
    
    def add_item(self, item: Item):
        """Add an item to this location."""
        self.items.append(item)
    
    def remove_item(self, item: Item):
        """Remove an item from this location."""
        if item in self.items:
            self.items.remove(item)
    
    def add_action(self, action: str, handler: Optional[Callable] = None):
        """Add an available action to this location."""
        if action not in self.available_actions:
            self.available_actions.append(action)
        
        if handler:
            self.action_handlers[action] = handler
    
    def process_action(self, action: str, game_state) -> bool:
        """Process a location-specific action."""
        if action in self.action_handlers:
            return self.action_handlers[action](game_state)
        return False
    
    def on_enter(self, game_state):
        """Called when player enters this location."""
        for handler in self.on_enter_handlers:
            handler(game_state)
    
    def on_exit(self, game_state):
        """Called when player leaves this location."""
        for handler in self.on_exit_handlers:
            handler(game_state)
    
    def get_full_description(self, game_state) -> str:
        """Get full location description including dynamic elements."""
        desc = self.description
        
        # Add environmental effects
        if self.environmental_effects:
            desc += "\n\n" + " ".join(self.environmental_effects)
        
        # Add visible items
        if self.items:
            item_names = [item.name for item in self.items]
            desc += f"\n\nYou can see: {', '.join(item_names)}"
        
        return desc


class World:
    """Manages the game world, locations, and global state."""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.global_flags: Dict[str, Any] = {}
        self.world_time = 0
        self.weather = "clear"
        self.void_storm_intensity = 0
        
        # System references (set by game engine)
        self.combat_system = None
        self.inventory_system = None
        self.quest_system = None
        self.dialogue_system = None
        
        # Initialize the world
        self.create_world()
    
    def create_world(self):
        """Create all game locations and connect them."""
        # Aethros - The Trading Hub
        self.create_aethros_locations()
        
        # Verdant Isle - The Living Island
        self.create_verdant_isle_locations()
        
        # Crystalline Peaks - The Mining Colony
        self.create_crystalline_peaks_locations()
        
        # Shadowmere - The Mysterious Island
        self.create_shadowmere_locations()
        
        # The Void - Areas between islands
        self.create_void_locations()
        
        # Connect locations
        self.connect_locations()
        
        # Populate with NPCs and items
        self.populate_world()
    
    def create_aethros_locations(self):
        """Create locations for Aethros, the trading hub."""
        # Aethros Docks
        docks = Location(
            "aethros_docks",
            "Aethros Docks",
            "The bustling docks of Port Aethros stretch out before you, filled with "
            "sky-ships of all sizes. Crystalline engines hum with contained energy, "
            "and the air shimmers with void energies. Dock workers move cargo while "
            "merchants haggle over exotic goods from distant islands."
        )
        docks.add_action("examine ships")
        docks.add_action("talk to dock workers")
        docks.environmental_effects.append("The sound of crystal engines creates a constant, soothing hum.")
        
        # Aethros Market
        market = Location(
            "aethros_market",
            "Grand Bazaar",
            "The heart of Aethros commerce, the Grand Bazaar is a maze of stalls "
            "and shops selling everything from basic supplies to rare crystal artifacts. "
            "Merchants from across the known realms hawk their wares while customers "
            "from dozens of different islands browse the offerings."
        )
        market.add_action("browse stalls")
        market.add_action("look for rare items")
        
        # Aethros Tavern
        tavern = Location(
            "aethros_tavern",
            "The Floating Anchor Tavern",
            "A warm, welcoming tavern popular with travelers and locals alike. "
            "The common room is filled with the chatter of patrons sharing tales "
            "of their journeys between the islands. A large fireplace crackles "
            "merrily, and the smell of hearty food fills the air."
        )
        tavern.add_action("order food")
        tavern.add_action("listen to stories")
        tavern.add_action("ask about rumors")
        
        # Aethros Council Hall
        council_hall = Location(
            "aethros_council_hall",
            "Council Hall",
            "The seat of Aethros governance, this imposing building houses the "
            "Merchant Council that rules the trading hub. Guards in practical "
            "armor stand at attention, and the walls are decorated with maps "
            "of the known Sky Islands and trade routes."
        )
        council_hall.add_action("speak with guards")
        council_hall.add_action("request audience")
        
        # Crystal Quarter
        crystal_quarter = Location(
            "aethros_crystal_quarter",
            "Crystal Quarter",
            "A specialized district where crystal researchers and artificers work. "
            "The buildings here are reinforced against magical accidents, and "
            "the air tingles with residual magical energy. Strange lights dance "
            "in windows as experiments are conducted within."
        )
        crystal_quarter.add_action("visit artificer")
        crystal_quarter.add_action("examine crystal research")
        
        # Add locations to world
        for location in [docks, market, tavern, council_hall, crystal_quarter]:
            self.locations[location.location_id] = location
    
    def create_verdant_isle_locations(self):
        """Create locations for Verdant Isle, the living island."""
        # Verdant Landing
        landing = Location(
            "verdant_landing",
            "Verdant Landing",
            "The docking area of Verdant Isle is carved into the living rock of "
            "the island itself. Vines and flowers grow from every surface, and "
            "the air is sweet with the scent of exotic blooms. Even the dock "
            "structures seem to be grown rather than built."
        )
        landing.environmental_effects.append("Flower petals drift gently on the breeze.")
        
        # Grove of Whispers
        grove = Location(
            "verdant_grove",
            "Grove of Whispers",
            "An ancient grove where the trees themselves seem to be aware of "
            "your presence. The leaves rustle with no wind, and occasionally "
            "you hear what sounds almost like voices speaking in an unknown "
            "language. Life crystals pulse gently in the tree trunks."
        )
        grove.add_action("listen to whispers")
        grove.add_action("touch life crystal")
        grove.environmental_effects.append("The trees seem to sway toward you as you move.")
        
        # Druid Circle
        druid_circle = Location(
            "verdant_druid_circle",
            "Circle of the Green Wardens",
            "A sacred space where the druids of Verdant Isle gather to commune "
            "with the island's life force. Standing stones covered in living "
            "moss form a perfect circle around a pool of crystal-clear water "
            "that reflects not the sky, but the island's dreams."
        )
        druid_circle.add_action("approach the pool")
        druid_circle.add_action("speak with druids")
        
        # Living Maze
        maze = Location(
            "verdant_maze",
            "The Living Maze",
            "A maze of hedges that grows and changes according to the island's "
            "whims. What was a dead end moments ago might now be a passage, and "
            "new paths appear while others close. The very walls pulse with "
            "green energy and seem to watch your progress."
        )
        maze.add_action("follow the green glow")
        maze.add_action("wait for paths to change")
        
        # Add locations to world
        for location in [landing, grove, druid_circle, maze]:
            self.locations[location.location_id] = location
    
    def create_crystalline_peaks_locations(self):
        """Create locations for Crystalline Peaks, the mining colony."""
        # Mining Station
        station = Location(
            "peaks_mining_station",
            "Crystalpeak Mining Station",
            "A utilitarian settlement built around the richest crystal deposits "
            "in the known realms. Mining equipment and refineries dot the "
            "landscape, while workers in protective gear extract precious "
            "crystals from the living rock. The air shimmers with raw magic."
        )
        station.add_action("speak with miners")
        station.add_action("examine equipment")
        
        # Crystal Caverns
        caverns = Location(
            "peaks_crystal_caverns",
            "Deep Crystal Caverns",
            "Natural caverns filled with crystal formations of every type and "
            "size. The walls themselves are made of crystallized magic, and "
            "rainbow light dances across every surface. The deeper passages "
            "glow with an inner light that pulses like a heartbeat."
        )
        caverns.add_action("mine crystals")
        caverns.add_action("explore deeper")
        caverns.environmental_effects.append("Crystal formations sing softly in harmony.")
        
        # Refinery
        refinery = Location(
            "peaks_refinery",
            "Crystal Refinery",
            "A complex facility where raw crystals are processed and refined "
            "into usable forms. Magical furnaces burn with cold fire, and "
            "specialized equipment separates and purifies different crystal "
            "types. The work here is dangerous but highly profitable."
        )
        refinery.add_action("observe refining process")
        refinery.add_action("speak with artificers")
        
        # Add locations to world
        for location in [station, caverns, refinery]:
            self.locations[location.location_id] = location
    
    def create_shadowmere_locations(self):
        """Create locations for Shadowmere, the mysterious island."""
        # Shadowmere Shore
        shore = Location(
            "shadowmere_shore",
            "Shadowmere Shore",
            "The dark shore of Shadowmere is shrouded in perpetual twilight. "
            "Black sand beaches stretch beneath a sky of roiling shadow clouds, "
            "and the very air seems to whisper secrets. Shadow crystals jut "
            "from the ground like obsidian fingers."
        )
        shore.environmental_effects.append("Shadows move independently of their sources.")
        
        # Whispering Library
        library = Location(
            "shadowmere_library",
            "The Whispering Library",
            "An ancient library carved into the heart of Shadowmere, filled "
            "with books that write themselves and scrolls that contain living "
            "memories. The knowledge here is vast but dangerous, and some "
            "books are chained shut for good reason."
        )
        library.add_action("read ancient texts")
        library.add_action("search for specific knowledge")
        library.add_action("speak with the librarian")
        
        # Shadow Temple
        temple = Location(
            "shadowmere_temple",
            "Temple of Forgotten Dreams",
            "A haunting temple dedicated to memories lost and dreams abandoned. "
            "The walls are covered in murals that seem to shift and change "
            "when you're not looking directly at them. At the center stands "
            "an altar of pure shadow crystal."
        )
        temple.add_action("approach the altar")
        temple.add_action("study the murals")
        
        # Add locations to world
        for location in [shore, library, temple]:
            self.locations[location.location_id] = location
    
    def create_void_locations(self):
        """Create locations representing the void between islands."""
        # Void Crossing
        crossing = Location(
            "void_crossing",
            "Void Crossing",
            "You find yourself in the space between islands, where reality "
            "becomes fluid and the normal rules don't apply. Fragments of "
            "lost islands drift past like ghostly memories, and the void "
            "energies swirl in hypnotic patterns."
        )
        crossing.add_action("collect void fragments")
        crossing.add_action("navigate carefully")
        crossing.environmental_effects.append("The void energies make your skin tingle with power.")
        
        self.locations[crossing.location_id] = crossing
    
    def connect_locations(self):
        """Connect all locations with appropriate exits."""
        # Aethros connections
        self.add_bidirectional_exit("aethros_docks", "north", "aethros_market", "south")
        self.add_bidirectional_exit("aethros_market", "west", "aethros_tavern", "east")
        self.add_bidirectional_exit("aethros_market", "north", "aethros_council_hall", "south")
        self.add_bidirectional_exit("aethros_market", "east", "aethros_crystal_quarter", "west")
        
        # Inter-island connections (via sky-ship)
        self.locations["aethros_docks"].add_exit("board ship to verdant isle", "verdant_landing")
        self.locations["aethros_docks"].add_exit("board ship to crystalline peaks", "peaks_mining_station")
        self.locations["aethros_docks"].add_exit("board ship to shadowmere", "shadowmere_shore")
        
        # Return trips
        self.locations["verdant_landing"].add_exit("board ship to aethros", "aethros_docks")
        self.locations["peaks_mining_station"].add_exit("board ship to aethros", "aethros_docks")
        self.locations["shadowmere_shore"].add_exit("board ship to aethros", "aethros_docks")
        
        # Verdant Isle internal connections
        self.add_bidirectional_exit("verdant_landing", "north", "verdant_grove", "south")
        self.add_bidirectional_exit("verdant_grove", "east", "verdant_druid_circle", "west")
        self.add_bidirectional_exit("verdant_druid_circle", "north", "verdant_maze", "south")
        
        # Crystalline Peaks internal connections
        self.add_bidirectional_exit("peaks_mining_station", "down", "peaks_crystal_caverns", "up")
        self.add_bidirectional_exit("peaks_mining_station", "east", "peaks_refinery", "west")
        
        # Shadowmere internal connections
        self.add_bidirectional_exit("shadowmere_shore", "north", "shadowmere_library", "south")
        self.add_bidirectional_exit("shadowmere_library", "east", "shadowmere_temple", "west")
    
    def add_bidirectional_exit(self, loc1_id: str, dir1: str, loc2_id: str, dir2: str):
        """Add exits in both directions between two locations."""
        if loc1_id in self.locations:
            self.locations[loc1_id].add_exit(dir1, loc2_id)
        if loc2_id in self.locations:
            self.locations[loc2_id].add_exit(dir2, loc1_id)
    
    def populate_world(self):
        """Populate the world with NPCs and items."""
        # This would be a large function in a complete implementation
        # For now, we'll add a few key NPCs and items
        
        # Aethros NPCs
        dock_master = NPC("Harbor Master Jorik", "official", 3)
        dock_master.dialogue_state = "initial"
        dock_master.services_offered = ["ship_passage", "information"]
        self.locations["aethros_docks"].add_npc(dock_master)
        
        tavern_keeper = NPC("Mara the Tavern Keeper", "merchant", 2)
        tavern_keeper.services_offered = ["food", "rooms", "rumors"]
        self.locations["aethros_tavern"].add_npc(tavern_keeper)
        
        # Add some starting items
        crystal_fragment = Item("Crystal Fragment", "quest", "A small fragment of unknown crystal type.", 1)
        self.locations["aethros_docks"].add_item(crystal_fragment)
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        return self.locations.get(location_id)
    
    def set_global_flag(self, flag: str, value: Any):
        """Set a global world flag."""
        self.global_flags[flag] = value
    
    def get_global_flag(self, flag: str, default: Any = False) -> Any:
        """Get a global world flag."""
        return self.global_flags.get(flag, default)
    
    def advance_world_time(self, hours: int = 1):
        """Advance world time and trigger time-based events."""
        self.world_time += hours
        
        # Trigger time-based events
        if self.world_time % 24 == 0:  # Daily events
            self.trigger_daily_events()
        
        if self.world_time % 168 == 0:  # Weekly events
            self.trigger_weekly_events()
    
    def trigger_daily_events(self):
        """Trigger daily world events."""
        # Refresh shop inventories, reset daily NPCs, etc.
        pass
    
    def trigger_weekly_events(self):
        """Trigger weekly world events."""
        # Major world state changes, story progression, etc.
        pass
    
    def get_nearby_locations(self, location_id: str) -> List[str]:
        """Get locations accessible from the given location."""
        location = self.get_location(location_id)
        if location:
            return list(location.exits.values())
        return []
    
    def can_travel_to(self, from_location: str, to_location: str) -> bool:
        """Check if travel is possible between two locations."""
        location = self.get_location(from_location)
        if location:
            return to_location in location.exits.values()
        return False