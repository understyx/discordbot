# models/item_type.py
from enum import IntEnum

# Keep enum definition as provided
class ItemTypes(IntEnum):
    HEAD = 1
    NECK = 2
    SHOULDER = 3
    BACK = 16
    CHEST = 5
    SHIRT = 4
    TABARD = 19
    WRIST = 9
    GLOVES = 10
    WAIST = 6
    LEGS = 7
    FEET = 8
    RING = 11
    TRINKET = 12
    WEAPON_2H = 17
    WEAPON_1H = 13
    SHIELD = 14
    OFF_HAND = 23 # Corrected from original example which had 23
    RELIC = 28 # Corrected from original example which had 28
    RANGED = 15 # Common value for Bow/Gun/Crossbow/Wand, 26 is Thrown
    THROWN = 26 # Explicitly add Thrown if needed

    # Helper to get type by value, returns None if not found
    @classmethod
    def get_type(cls, value: int):
        try:
            return cls(value)
        except ValueError:
            return None
