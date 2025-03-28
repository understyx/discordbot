# models/item.py
from typing import List, Optional
from models.item_type import ItemTypes

class Item:
    """Represents an item fetched from the database."""

    def __init__(
        self,
        item_id: int,
        name: str,
        item_level: int,
        quality: int,
        item_type_val: int, # Store the raw value
        requires: Optional[str], # Can be None
        char_class: Optional[str], # Can be None
        subclass: Optional[str], # Can be None
        gem_slots: int, # Number of sockets from DB
        gear_score: float,
        # Data from Armory parsing (can be None if not equipped)
        enchant_id: Optional[str] = None,
        equipped_gems: Optional[List[str]] = None,
    ):
        self.item_id = item_id
        self.name = name
        self.item_level = item_level
        self.quality = quality
        self.item_type: Optional[ItemTypes] = ItemTypes.get_type(item_type_val) # Convert to Enum
        self.requires = requires
        self.char_class = char_class
        self.subclass = subclass
        self.gem_slots = gem_slots if gem_slots is not None else 0 # Default to 0
        self.gear_score = gear_score if gear_score is not None else 0.0 # Default to 0.0
        self.enchant_id = enchant_id
        # Ensure equipped_gems is always a list if provided
        self.equipped_gems: List[str] = equipped_gems if equipped_gems is not None else []

    def __repr__(self):
        return (
            f"<Item id={self.item_id} name='{self.name}' "
            f"ilvl={self.item_level} type={self.item_type}>"
        )

    def has_enchant_slot(self, char_class: str, professions: List[str]) -> bool:
        """Checks if this item type typically requires an enchant."""
        if not self.item_type:
            return False

        # Slots that never need enchants
        if self.item_type in {
            ItemTypes.SHIRT,
            ItemTypes.TABARD,
            ItemTypes.TRINKET,
        }:
            return False

        # Slots that sometimes don't need enchants based on class/prof
        if self.item_type == ItemTypes.NECK: # Usually no enchant
             return False
        if self.item_type == ItemTypes.WAIST: # Usually no enchant (except Eng belt)
             return False # Simplified - add Eng check if needed
        if self.item_type in {ItemTypes.OFF_HAND, ItemTypes.RELIC, ItemTypes.RANGED, ItemTypes.THROWN}:
            # Wands/Relics/Offhands/Ranged for casters/healers usually not enchanted
            if char_class in {"Mage", "Warlock", "Priest", "Druid", "Shaman", "Paladin"}: # Added Shaman/Paladin
                 # Exception: Enhancement Shaman might enchant offhand
                 # Exception: Hunter might enchant ranged
                 # Simplified for now
                 return False
        # Thrown for non-hunters usually not enchanted
        if self.item_type == ItemTypes.THROWN and char_class not in {"Hunter", "Rogue", "Warrior"}:
             return False
        # Rings only if Enchanter
        if self.item_type == ItemTypes.RING and "Enchanting" not in "".join(professions):
            return False

        return True # Assume enchantable otherwise

    def has_gem_slots(self) -> bool:
        """Checks if the item has gem slots based on DB info."""
        return self.gem_slots > 0

    def gems_missing(self) -> bool:
        """Checks if the number of equipped gems matches the available slots."""
        return self.has_gem_slots() and len(self.equipped_gems) < self.gem_slots
