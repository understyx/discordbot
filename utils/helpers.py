# utils/helpers.py
import re
from typing import List, Dict, Optional
from models.item_type import ItemTypes
from utils.constants import SUPPORTED_REALMS, OK, ERROR, WARNING

def normalize_realm_name(user_input: str) -> Optional[str]:
    """
    Normalizes realm names to their full names.

    :param user_input: Input string to be normalized.
    :return: Full capitalized realm name, or None if not found.
    """
    cap_input = user_input.capitalize()
    for realm in SUPPORTED_REALMS:
        if realm.startswith(cap_input):
            return realm
    # Special case for common short names
    if "Lord" in cap_input:
        return "Lordaeron"
    if "Ony" in cap_input:
        return "Onyxia"
    if "Black" in cap_input or "Block" in cap_input: # Added "Block"
        return "Blackrock"
    return None

def format_prof_spec(prof_spec: List[str]) -> str:
    """Formats professions or specializations list for embed."""
    if not prof_spec or prof_spec == [""]:
        return "None"
    return "\n".join(
        [f"[{i + 1}] {item}" for i, item in enumerate(prof_spec)]
    )

def format_glyphs(
    glyph_data: Dict[str, Dict[str, List[str]]], spec_id: str, glyph_type: str
) -> str:
    """Formats glyphs for a specific spec and type."""
    try:
        glyphs = glyph_data.get(spec_id, {}).get(glyph_type, [])
        if not glyphs:
            return "None"
        return "\n".join([f"- {g}" for g in glyphs])
    except Exception:
        return "Error parsing glyphs" # Basic error handling

def clean_data_for_table(lines: List[str]) -> str:
    """Cleans profession/spec data for the multi-stalk table."""
    fixed = list()
    for line in lines:
        # Remove brackets, quotes, and parenthesized values
        line = line.replace("[", "").replace("]", "").replace("'", "")
        line = re.sub(r"\s*\([^)]*\)", "", line).strip()
        if line:
            fixed.append(line)
    return ", ".join(fixed) if fixed else "None"

def _format_missing_list(items: List[ItemTypes], item_category: str) -> str:
    """Helper to format lists of missing enchants/gems."""
    if not items:
        return f"All relevant items have {item_category}! {OK}"

    # Count occurrences
    counts = {}
    for item in items:
        try:
            name = item.name # Get enum name
        except AttributeError:
            name = "Unknown Slot"
        counts[name] = counts.get(name, 0) + 1

    # Create string
    parts = []
    for name, count in counts.items():
        parts.append(f"{name} ({count})" if count > 1 else name)

    return f"{ERROR} Missing {item_category} on: {', '.join(parts)}"


def missing_enchant_message(not_enchanted: List[ItemTypes]) -> str:
    """Creates a message listing items missing enchants."""
    return _format_missing_list(not_enchanted, "enchants")


def missing_gems_message(missing_gems_slots: List[ItemTypes]) -> str:
    """Creates a message listing items with missing gems."""
    return _format_missing_list(missing_gems_slots, "gems")
