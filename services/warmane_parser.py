# services/warmane_parser.py
import re
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Set
from models.item import Item
from models.item_type import ItemTypes
from utils.helpers import missing_enchant_message, missing_gems_message

logger = logging.getLogger(__name__)

class WarmaneParserError(Exception):
    """Custom exception for parsing errors."""
    pass

class WarmaneParser:

    @staticmethod
    def check_character_exists(html: str) -> bool:
        """Checks if the HTML indicates a 'character not found' error."""
        if not html:
            return False # No HTML means we can't check
        # More robust check - look for the specific error div
        parser = BeautifulSoup(html, 'html.parser')
        error_div = parser.find('div', class_='error-page')
        if error_div and "does not exist" in error_div.get_text():
            logger.warning("Character not found message detected in HTML.")
            return False
        # Fallback check if structure changes
        if "The character you are looking for does not exist" in html:
             logger.warning("Fallback 'character not found' text detected.")
             return False
        return True

    @staticmethod
    def extract_equipped_items_data(html: str) -> Tuple[Dict[int, List[Dict]], Set[int]]:
        """
        Parses the profile HTML to extract equipped item IDs, enchants, and gems.
        Returns a dict {item_id: [{'enchant': id, 'gems': [ids]}, ...]} and a set of all item_ids.
        Handles multiple items with the same ID (rings, trinkets).
        """
        if not html:
            raise WarmaneParserError("Cannot parse empty HTML for items.")

        parser = BeautifulSoup(html, 'html.parser')
        # Find all tags with 'rel' attribute, common for item tooltips
        rel_tags = parser.find_all(attrs={'rel': True})
        if not rel_tags:
            logger.warning("No 'rel' tags found in HTML for item extraction.")
            return {}, set()

        # Structure: {item_id: [{'enchant': str|None, 'gems': [str]}, ...]}
        equipped_items: Dict[int, List[Dict]] = {}
        all_item_ids: Set[int] = set()

        for tag in rel_tags:
            rel_value = tag['rel']
            # Ensure rel_value is a list, handle single string case
            if isinstance(rel_value, str):
                rel_value = [rel_value]

            # Process each part of the rel attribute (e.g., "item=123&ench=456")
            for rel_part in rel_value:
                if not rel_part.startswith("item="):
                    continue # Skip non-item rel parts

                components = rel_part.split('&')
                item_id_str: Optional[str] = None
                enchant_id: Optional[str] = None
                gem_ids: List[str] = []

                try:
                    for component in components:
                        if component.startswith("item="):
                            item_id_str = component.split("=")[1]
                        elif component.startswith("ench="):
                            enchant_id = component.split("=")[1]
                        elif component.startswith("gems="):
                            raw_gems = component.split("=")[1]
                            # Filter out '0' which represents empty slots
                            gem_ids = [gem for gem in raw_gems.split(":") if gem != "0"]

                    if item_id_str:
                        item_id = int(item_id_str)
                        all_item_ids.add(item_id)
                        item_data = {"enchant": enchant_id, "gems": gem_ids}

                        if item_id not in equipped_items:
                            equipped_items[item_id] = []
                        equipped_items[item_id].append(item_data)

                except (ValueError, IndexError, TypeError) as e:
                    logger.warning(f"Failed to parse item rel component '{rel_part}': {e}")
                    continue # Skip this component on error

        return equipped_items, all_item_ids


    @staticmethod
    def extract_guild(html: str) -> Optional[str]:
        """Extracts the guild name."""
        if not html: return None
        try:
            parser = BeautifulSoup(html, 'html.parser')
            guild_span = parser.find('span', class_='guild-name')
            if guild_span and guild_span.a:
                return guild_span.a.text.strip()
            return None # No guild found
        except Exception as e:
            logger.warning(f"Error parsing guild: {e}")
            return None

    @staticmethod
    def extract_professions(html: str) -> List[str]:
        """Extracts professions and their levels."""
        if not html: return []
        results = []
        try:
            parser = BeautifulSoup(html, 'html.parser')
            prof_div = parser.find('div', class_='profskills')
            if not prof_div: return []

            text_divs = prof_div.find_all('div', class_='text')
            for div in text_divs:
                prof_name = div.contents[0].strip()
                value_span = div.find('span', class_='value')
                prof_value = value_span.text.strip() if value_span else "N/A"
                results.append(f"{prof_name} ({prof_value})")
        except Exception as e:
            logger.warning(f"Error parsing professions: {e}")
            # Return potentially partial results or empty list
        return results

    @staticmethod
    def extract_specializations(html: str) -> Tuple[List[str], Optional[str]]:
        """Extracts specializations, points, and determines active spec."""
        if not html: return [], None
        results = []
        active_spec_id = None
        try:
            parser = BeautifulSoup(html, 'html.parser')
            # Find spec containers which usually have data-id="0" or data-id="1"
            spec_containers = parser.find_all('div', class_='talents-block') # Adjust class if needed

            for i, container in enumerate(spec_containers):
                 # Attempt to find the name and points within the container
                 name_tag = container.find('div', class_='name')
                 points_tag = container.find('span', class_='points') # Or 'div' with points

                 if name_tag:
                     spec_name = name_tag.get_text(strip=True)
                     spec_value = points_tag.get_text(strip=True) if points_tag else "0/0/0"
                     results.append(f"{spec_name} ({spec_value})")

                     # Check if this spec is marked as active
                     # The 'active' class might be on the container or a child
                     if 'active' in container.get('class', []):
                          active_spec_id = str(i) # Assuming 0 or 1 based on order

                 # Fallback if structure is simpler (like original code)
                 elif i == 0: # Assume first is primary if blocks aren't distinct
                     spec_div = parser.find('div', class_='specialization')
                     if spec_div:
                         text_divs = spec_div.find_all('div', class_='text')
                         for div in text_divs:
                             spec_name = div.contents[0].strip()
                             value_span = div.find('span', class_='value')
                             spec_value = value_span.text.strip() if value_span else "0/0/0"
                             results.append(f"{spec_name} ({spec_value})")
                         # Cannot reliably determine active spec in this fallback
                         break # Stop after processing the old structure

            # If active spec wasn't found via class, try data-id on talent tree itself
            if active_spec_id is None:
                 talent_tree = parser.find('div', attrs={'data-id': True, 'class': 'talent-tree'}) # Example selector
                 if talent_tree:
                      active_spec_id = talent_tree.get('data-id')


        except Exception as e:
            logger.warning(f"Error parsing specializations: {e}")

        # If still no active spec, default to '0' if specs exist
        if active_spec_id is None and results:
             active_spec_id = '0'
             logger.info("Could not determine active spec, defaulting to '0'.")

        return results, active_spec_id


    @staticmethod
    def extract_level_race_class(html: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """Extracts Level, Race, and Class."""
        if not html: return None, None, None
        try:
            parser = BeautifulSoup(html, 'html.parser')
            data_div = parser.find("div", class_="level-race-class")
            if not data_div: return None, None, None

            text = data_div.get_text(strip=True) # e.g., "80 Blood Elf Paladin"
            parts = text.split() # Split by space

            level = None
            race = None
            char_class = None

            if len(parts) >= 3:
                try:
                    level = int(parts[0])
                except ValueError:
                    logger.warning(f"Could not parse level from '{parts[0]}'")
                # Race can be multi-word (Blood Elf), Class is usually last
                char_class = parts[-1]
                race = " ".join(parts[1:-1])
            elif len(parts) == 2: # Handle cases like "80 Paladin" if race is missing
                 try:
                    level = int(parts[0])
                 except ValueError:
                    logger.warning(f"Could not parse level from '{parts[0]}'")
                 char_class = parts[1]
            else:
                 logger.warning(f"Unexpected format for level-race-class: '{text}'")


            return level, race, char_class
        except Exception as e:
            logger.warning(f"Error parsing level/race/class: {e}")
            return None, None, None

    @staticmethod
    def extract_glyphs(html: str) -> Dict[str, Dict[str, List[str]]]:
        """Extracts Major and Minor glyphs for each spec (0 and 1)."""
        if not html: return {}
        glyph_data: Dict[str, Dict[str, List[str]]] = {}
        try:
            parser = BeautifulSoup(html, 'html.parser')
            # Find containers for each spec, usually identified by data-glyphs attribute
            glyph_sections = parser.find_all('div', attrs={'data-glyphs': True})

            if not glyph_sections:
                 # Fallback: Maybe glyphs are just listed without spec separation?
                 # This requires inspecting the HTML structure if the above fails.
                 logger.warning("Could not find glyph sections with 'data-glyphs'. Glyph parsing might fail.")
                 # Try finding all glyph divs directly (less reliable)
                 all_major = parser.find_all('div', class_='glyph major')
                 all_minor = parser.find_all('div', class_='glyph minor')
                 if all_major or all_minor:
                      glyph_data['0'] = {"Major Glyphs": [], "Minor Glyphs": []} # Assume spec 0
                      for glyph in all_major:
                           link = glyph.find('a')
                           if link: glyph_data['0']["Major Glyphs"].append(link.text.strip())
                      for glyph in all_minor:
                           link = glyph.find('a')
                           if link: glyph_data['0']["Minor Glyphs"].append(link.text.strip())
                 return glyph_data # Return whatever was found in fallback


            for section in glyph_sections:
                spec_id = section.get('data-glyphs') # Should be '0' or '1'
                if spec_id not in ['0', '1']:
                    logger.warning(f"Unexpected data-glyphs ID found: {spec_id}")
                    continue

                glyph_data[spec_id] = {"Major Glyphs": [], "Minor Glyphs": []}

                major_glyphs = section.find_all('div', class_='glyph major')
                for glyph in major_glyphs:
                    link = glyph.find('a')
                    if link:
                        glyph_name = link.text.strip()
                        glyph_data[spec_id]["Major Glyphs"].append(glyph_name)

                minor_glyphs = section.find_all('div', class_='glyph minor')
                for glyph in minor_glyphs:
                    link = glyph.find('a')
                    if link:
                        glyph_name = link.text.strip()
                        glyph_data[spec_id]["Minor Glyphs"].append(glyph_name)

        except Exception as e:
            logger.warning(f"Error parsing glyphs: {e}")
            # Return potentially partial data
        return glyph_data

    @staticmethod
    def calculate_gear_score(items: Dict[int, List[Item]]) -> float:
        """Calculates GearScore from a dictionary of Item objects."""
        gearscore = 0.0
        two_handed_scores = []
        main_hand_score = 0.0
        off_hand_score = 0.0

        processed_slots = set()

        for item_list in items.values():
            # Handle multiple items (rings/trinkets) - use the highest GS for that slot type
            # Group by item type first
            items_by_type: Dict[Optional[ItemTypes], List[Item]] = {}
            for item in item_list:
                if item.item_type not in items_by_type:
                    items_by_type[item.item_type] = []
                items_by_type[item.item_type].append(item)

            for item_type, items_in_slot in items_by_type.items():
                if not item_type or item_type in processed_slots:
                    continue # Skip unknown types or already processed slots

                # Find the best item for this slot type
                best_item = max(items_in_slot, key=lambda i: i.gear_score, default=None)
                if not best_item:
                    continue

                # Skip non-contributing slots
                if item_type in {ItemTypes.SHIRT, ItemTypes.TABARD}:
                    continue

                # Handle weapon logic carefully
                if item_type == ItemTypes.WEAPON_2H:
                    # Average GS for 2H (treat as MH+OH)
                    two_handed_scores.append(best_item.gear_score)
                elif item_type == ItemTypes.WEAPON_1H:
                    # Take the highest 1H as main hand for now
                    main_hand_score = max(main_hand_score, best_item.gear_score)
                elif item_type in {ItemTypes.SHIELD, ItemTypes.OFF_HAND}:
                    off_hand_score = max(off_hand_score, best_item.gear_score)
                else:
                    # Add GS for other slots
                    gearscore += best_item.gear_score

                # Mark slot type as processed (handles rings/trinkets correctly)
                processed_slots.add(item_type)


        # Final weapon GS calculation
        if two_handed_scores:
            # If any 2H equipped, average its GS for MH/OH contribution
            avg_2h_gs = sum(two_handed_scores) / len(two_handed_scores)
            gearscore += avg_2h_gs # Add average 2H score (counts as MH+OH)
        else:
            # If only 1H/OH, add their scores
            gearscore += main_hand_score + off_hand_score

        return round(gearscore, 2)


    @staticmethod
    def calculate_avg_ilvl(items: Dict[int, List[Item]]) -> float:
        """Calculates Average Item Level."""
        ilvl_total = 0
        count = 0
        processed_slots = set()

        for item_list in items.values():
            items_by_type: Dict[Optional[ItemTypes], List[Item]] = {}
            for item in item_list:
                if item.item_type not in items_by_type:
                    items_by_type[item.item_type] = []
                items_by_type[item.item_type].append(item)

            for item_type, items_in_slot in items_by_type.items():
                if not item_type or item_type in processed_slots:
                    continue

                best_item = max(items_in_slot, key=lambda i: i.item_level, default=None)
                if not best_item:
                    continue

                if item_type in {ItemTypes.SHIRT, ItemTypes.TABARD}:
                    continue

                # Special handling for 2H vs 1H/OH might be needed depending on exact avg ilvl definition
                # Standard definition usually counts 2H as one slot, 1H+OH as two.
                # Let's count equipped slots.
                ilvl_total += best_item.item_level
                count += 1
                processed_slots.add(item_type)

                # If it's a 1H, and there's also an OH/Shield equipped, count increases by 1 implicitly later.
                # If it's a 2H, count increases by 1.

        return round(ilvl_total / count, 2) if count else 0.0

    @staticmethod
    def check_enchants(
        items: Dict[int, List[Item]], char_class: Optional[str], professions: List[str]
    ) -> str:
        """Checks for missing enchants on relevant gear pieces."""
        not_enchanted: List[ItemTypes] = []
        if not char_class: char_class = "" # Default if class not found

        processed_slots = set()

        for item_list in items.values():
            items_by_type: Dict[Optional[ItemTypes], List[Item]] = {}
            for item in item_list:
                if item.item_type not in items_by_type:
                    items_by_type[item.item_type] = []
                items_by_type[item.item_type].append(item)

            for item_type, items_in_slot in items_by_type.items():
                 if not item_type or item_type in processed_slots:
                     continue

                 # Check the highest ilvl item for the slot
                 best_item = max(items_in_slot, key=lambda i: i.item_level, default=None)
                 if not best_item:
                     continue

                 # Check if this slot *should* be enchanted
                 if best_item.has_enchant_slot(char_class, professions):
                     # Check if it *is* enchanted
                     if best_item.enchant_id is None:
                         not_enchanted.append(item_type)

                 processed_slots.add(item_type)


        return missing_enchant_message(not_enchanted)

    @staticmethod
    def check_gems(items: Dict[int, List[Item]]) -> str:
        """Checks for missing gems in socketed gear pieces."""
        missing_gems_slots: List[ItemTypes] = []

        processed_slots = set()

        for item_list in items.values():
            items_by_type: Dict[Optional[ItemTypes], List[Item]] = {}
            for item in item_list:
                if item.item_type not in items_by_type:
                    items_by_type[item.item_type] = []
                items_by_type[item.item_type].append(item)

            for item_type, items_in_slot in items_by_type.items():
                 if not item_type or item_type in processed_slots:
                     continue

                 best_item = max(items_in_slot, key=lambda i: i.item_level, default=None)
                 if not best_item:
                     continue

                 # Check if the item has gem slots and if they are filled
                 if best_item.gems_missing():
                     missing_gems_slots.append(item_type)

                 processed_slots.add(item_type)

        return missing_gems_message(missing_gems_slots)

    @staticmethod
    def extract_talent_points_string(html: str, class_name: Optional[str]) -> Dict[str, str]:
        """
        Extracts the talent points string (e.g., "0500...") for each spec.
        Returns a dictionary mapping spec_id ('0', '1') to the talent string.
        """
        if not html or not class_name: return {}
        talent_strings = {}
        try:
            soup = BeautifulSoup(html, "html.parser")
            # Find talent containers, often marked by class and maybe data-id
            # Adjust selector based on actual Warmane HTML structure
            containers = soup.find_all("div", class_=lambda x: x and 'talents-container' in x) # Flexible class match

            if not containers:
                 logger.warning("Could not find talent containers.")
                 return {}

            for i, container in enumerate(containers):
                spec_id = container.get('data-id', str(i)) # Get spec ID or use index

                # Find individual talent point divs within this container
                talent_divs = container.find_all("div", class_="talent-points") # Adjust if needed
                if not talent_divs:
                     # Try another common pattern
                     talent_divs = container.find_all("span", class_="points") # e.g., <span class="points">5/5</span>

                talent_numbers = []
                for div in talent_divs:
                    text = div.get_text(strip=True)  # e.g., "0/5" or "5/5"
                    try:
                        allocated = text.split("/")[0]
                        talent_numbers.append(allocated)
                    except IndexError:
                        logger.warning(f"Could not parse talent points from: '{text}'")
                        talent_numbers.append("0") # Append '0' on error

                if talent_numbers:
                    talent_strings[spec_id] = "".join(talent_numbers)
                else:
                     logger.warning(f"No talent points found for spec_id {spec_id}")


        except Exception as e:
            logger.exception(f"Error parsing talent points string: {e}")

        # Basic validation: Check length based on class (approximate)
        # This is highly approximate and needs adjustment per class
        expected_lengths = {
             "Death Knight": 88, "Paladin": 78, # Add other classes
        }
        expected_len = expected_lengths.get(class_name, 70) # Default guess

        final_talent_strings = {}
        for spec_id, t_str in talent_strings.items():
             if len(t_str) >= expected_len - 10: # Allow some flexibility
                  final_talent_strings[spec_id] = t_str
             else:
                  logger.warning(f"Talent string for spec {spec_id} seems too short ({len(t_str)} points). Discarding.")


        return final_talent_strings

