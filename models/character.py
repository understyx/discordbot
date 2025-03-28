# models/character.py
from typing import List, Dict, Optional
from models.item import Item

class Character:
    """Represents a World of Warcraft character."""

    def __init__(
        self,
        name: str,
        realm: str,
        level: Optional[int] = None,
        race: Optional[str] = None,
        char_class: Optional[str] = None, # Renamed from _class
        guild: Optional[str] = None,
        professions: Optional[List[str]] = None,
        specializations: Optional[List[str]] = None,
        # Store items keyed by ItemType for easier access
        items: Optional[Dict[int, List[Item]]] = None, # item_id -> list of Items (for rings/trinkets)
        # Store glyphs keyed by spec_id ('0', '1')
        glyphs: Optional[Dict[str, Dict[str, List[str]]]] = None,
        active_spec_id: Optional[str] = None, # '0' or '1'
        gear_score: float = 0.0,
        avg_item_level: float = 0.0,
    ):
        self.name = name
        self.realm = realm
        self.level = level
        self.race = race
        self.char_class = char_class
        self.guild = guild if guild else "No Guild"
        self.professions = professions if professions else []
        self.specializations = specializations if specializations else []
        self.items = items if items else {}
        self.glyphs = glyphs if glyphs else {}
        self.active_spec_id = active_spec_id
        self.gear_score = gear_score
        self.avg_item_level = avg_item_level

    def get_level_race_class_str(self) -> str:
        """Returns a formatted string for level, race, class."""
        parts = []
        if self.level:
            parts.append(f"Level {self.level}")
        if self.race:
            parts.append(self.race)
        if self.char_class:
            parts.append(self.char_class)
        return " ".join(parts) if parts else "N/A"

    def get_armory_link(self) -> str:
        """Generates the Warmane Armory link."""
        from utils.constants import WARMANE_ARMORY_URL # Local import
        return f"{WARMANE_ARMORY_URL}/{self.name.capitalize()}/{self.realm.capitalize()}/summary"

    def __repr__(self):
        return f"<Character name='{self.name}' realm='{self.realm}' class='{self.char_class}'>"

