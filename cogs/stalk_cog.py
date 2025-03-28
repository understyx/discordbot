# cogs/stalk_cog.py
import discord
from discord.ext import commands
import asyncio
import logging
from typing import List, Dict, Optional
from table2ascii import table2ascii as t2a, PresetStyle

# Service and Model Imports
from services.warmane_client import WarmaneClient
from services.warmane_parser import WarmaneParser, WarmaneParserError
from services.database_service import DatabaseService
from models.character import Character
from models.item import Item
from models.item_type import ItemTypes

# Util Imports
from utils.helpers import (
    normalize_realm_name, format_prof_spec, format_glyphs,
    clean_data_for_table
)
from utils.embeds import create_error_embed, create_char_not_found_embed
from utils.constants import (
    DEFAULT_REALM, ONYXIA_REALM, EMBED_COLOR_INFO, OK, ERROR
)

# Talent Imports
from talents import deathknight as dk_talents
from talents import paladin as paladin_talents

logger = logging.getLogger(__name__)

# --- Helper function to build Character object ---
async def _fetch_and_build_character(
    char_name: str,
    realm: str,
    warmane_client: WarmaneClient,
    db_service: DatabaseService,
    fetch_talents: bool = True, # Option to skip talent fetching
) -> Optional[Character]:
    """Fetches data from Armory and DB, then builds a Character object."""
    tasks = [warmane_client.get_profile_html(char_name, realm)]
    if fetch_talents:
        tasks.append(warmane_client.get_talents_html(char_name, realm))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    profile_html = results[0]
    talent_html = results[1] if fetch_talents and len(results) > 1 else None

    # Handle potential exceptions during fetching
    if isinstance(profile_html, Exception):
        logger.error(f"Failed to fetch profile for {char_name}-{realm}: {profile_html}")
        return None # Cannot proceed without profile
    if fetch_talents and isinstance(talent_html, Exception):
        logger.warning(f"Failed to fetch talents for {char_name}-{realm}: {talent_html}")
        talent_html = None # Continue without talents if fetch failed

    # Basic check if character exists before parsing
    if not profile_html or not WarmaneParser.check_character_exists(profile_html):
        logger.info(f"Character {char_name}-{realm} not found or profile HTML empty.")
        return None # Character not found

    # --- Parse Profile HTML ---
    try:
        guild = WarmaneParser.extract_guild(profile_html)
        level, race, char_class = WarmaneParser.extract_level_race_class(profile_html)
        professions = WarmaneParser.extract_professions(profile_html)
        specializations, active_spec_id = WarmaneParser.extract_specializations(profile_html)
        equipped_items_data, item_ids_to_fetch = WarmaneParser.extract_equipped_items_data(profile_html)
    except WarmaneParserError as e:
        logger.error(f"Parsing error for {char_name}-{realm} profile: {e}")
        return None # Critical parsing error
    except Exception as e:
        logger.exception(f"Unexpected error parsing profile for {char_name}-{realm}: {e}")
        return None

    # --- Fetch Item Data from DB ---
    db_item_data = await db_service.get_items_by_ids(item_ids_to_fetch)
    if not db_item_data and item_ids_to_fetch:
         logger.warning(f"No item data found in DB for {char_name}-{realm}, calculations might be inaccurate.")

    # --- Build Item Objects ---
    character_items: Dict[int, List[Item]] = {}
    for item_id, equipped_list in equipped_items_data.items():
        db_entries = db_item_data.get(item_id)
        if not db_entries:
            logger.warning(f"Item ID {item_id} not found in DB for {char_name}-{realm}.")
            continue # Skip item if not in DB

        # Match equipped items with DB data (handle multiple rings/trinkets)
        # Assume order matches or use heuristics if needed
        for i, equipped_data in enumerate(equipped_list):
            # Try to find a matching DB entry (usually the first one, or based on index for rings)
            db_entry = db_entries[i] if i < len(db_entries) else db_entries[0]

            try:
                item_obj = Item(
                    item_id=item_id,
                    name=db_entry['name'],
                    item_level=db_entry['ItemLevel'],
                    quality=db_entry['quality'],
                    item_type_val=db_entry['type'],
                    requires=db_entry['requires'],
                    char_class=db_entry['class'],
                    subclass=db_entry['subclass'],
                    gem_slots=db_entry['gems'],
                    gear_score=db_entry['GearScore'],
                    enchant_id=equipped_data['enchant'],
                    equipped_gems=equipped_data['gems']
                )
                if item_id not in character_items:
                    character_items[item_id] = []
                character_items[item_id].append(item_obj)
            except (KeyError, TypeError) as e:
                 logger.error(f"Error creating Item object for ID {item_id} from DB data: {e}")
                 continue # Skip this specific item instance

    # --- Parse Talents/Glyphs HTML ---
    glyphs = {}
    talent_strings = {}
    if talent_html:
        try:
            glyphs = WarmaneParser.extract_glyphs(talent_html)
            # Also extract talent string if needed for checks later
            talent_strings = WarmaneParser.extract_talent_points_string(talent_html, char_class)
        except Exception as e:
            logger.exception(f"Unexpected error parsing talents/glyphs for {char_name}-{realm}: {e}")
            # Continue without glyphs/talents if parsing failed

    # --- Perform Calculations ---
    gear_score = WarmaneParser.calculate_gear_score(character_items)
    avg_ilvl = WarmaneParser.calculate_avg_ilvl(character_items)

    # --- Create Character Object ---
    character = Character(
        name=char_name,
        realm=realm,
        level=level,
        race=race,
        char_class=char_class,
        guild=guild,
        professions=professions,
        specializations=specializations,
        items=character_items,
        glyphs=glyphs,
        active_spec_id=active_spec_id,
        gear_score=gear_score,
        avg_item_level=avg_ilvl,
        # Store talent strings if needed later
        # talent_strings=talent_strings
    )

    return character


# --- Cog Definition ---
class StalkCog(commands.Cog):
    def __init__(self, bot: commands.Bot, warmane_client: WarmaneClient, db_service: DatabaseService):
        self.bot = bot
        self.warmane_client = warmane_client
        self.db_service = db_service
        logger.info("StalkCog initialized.")

    def _create_stalk_embed(self, character: Character) -> discord.Embed:
        """Builds the Discord embed from a Character object."""
        embed = discord.Embed(
            title=f"Summary: {character.name.capitalize()}-{character.realm.capitalize()}",
            color=EMBED_COLOR_INFO,
            url=character.get_armory_link() # Add link to title
        )
        embed.set_thumbnail(url="https://www.warmane.com/images/icons/expansion-wotlk.png") # Generic WotLK icon

        # --- Basic Info ---
        embed.add_field(name="Level | Race | Class", value=character.get_level_race_class_str(), inline=True)
        embed.add_field(name="Guild", value=character.guild, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer

        # --- Specs & Profs ---
        embed.add_field(
            name="Specializations",
            value=format_prof_spec(character.specializations),
            inline=True,
        )
        embed.add_field(
            name="Professions",
            value=format_prof_spec(character.professions),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer

        # --- Gear Stats ---
        embed.add_field(name="GearScore", value=f"{character.gear_score:.2f}", inline=True)
        embed.add_field(name="Avg Item Level", value=f"{character.avg_item_level:.2f}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer

        # --- Enchants & Gems ---
        # Perform checks here using the character object
        enchant_status = WarmaneParser.check_enchants(character.items, character.char_class, character.professions)
        gem_status = WarmaneParser.check_gems(character.items)
        embed.add_field(name="Enchants", value=enchant_status, inline=True)
        embed.add_field(name="Gems", value=gem_status, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer

        # --- Glyphs (Only if not Onyxia and glyphs available) ---
        if character.realm != ONYXIA_REALM and character.glyphs and character.active_spec_id:
            active_glyphs = character.glyphs.get(character.active_spec_id, {})
            major_glyphs = active_glyphs.get("Major Glyphs", [])
            minor_glyphs = active_glyphs.get("Minor Glyphs", [])

            # Format glyphs into two columns if possible
            major_str = "\n".join([f"- {g}" for g in major_glyphs]) if major_glyphs else "None"
            minor_str = "\n".join([f"- {g}" for g in minor_glyphs]) if minor_glyphs else "None"

            embed.add_field(name="Major Glyphs", value=major_str, inline=True)
            embed.add_field(name="Minor Glyphs", value=minor_str, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer
        elif character.realm != ONYXIA_REALM:
             embed.add_field(name="Glyphs", value="Could not parse glyphs.", inline=False)
             embed.add_field(name="\u200b", value="\u200b", inline=False) # Spacer


        # --- Armory Link Footer ---
        embed.set_footer(text=f"Click the title for Armory link | Data fetched from Warmane Armory")

        return embed

    @commands.command(aliases=['summary', 'query'])
    async def stalk(self, ctx: commands.Context, character_name: str, realm_name: str = DEFAULT_REALM):
        """Shows a summary of a character from Warmane Armory."""
        async with ctx.typing():
            norm_realm = normalize_realm_name(realm_name)
            if not norm_realm:
                await ctx.send(embed=create_error_embed(
                    "Invalid Realm",
                    f"Could not recognize realm '{realm_name}'. Use Icecrown, Lordaeron, Blackrock, or Onyxia."
                ))
                return

            try:
                character = await _fetch_and_build_character(
                    character_name, norm_realm, self.warmane_client, self.db_service
                )

                if character:
                    embed = self._create_stalk_embed(character)
                    await ctx.send(embed=embed)
                else:
                    # Character not found or critical error during fetch/parse
                    await ctx.send(embed=create_char_not_found_embed(character_name, norm_realm))

            except Exception as e:
                logger.exception(f"Error in stalk command for {character_name}-{norm_realm}: {e}")
                await ctx.send(embed=create_error_embed(description="An unexpected error occurred while processing the stalk command."))

    @commands.command(aliases=['stalkmulti', 'querymulti', 'multistalk'])
    async def multistalk(self, ctx: commands.Context, *args: str):
        """Shows basic GearScore, Enchants, Gems, Spec, Profs for multiple characters (Default: Icecrown)."""
        if not args:
            await ctx.send("Please provide at least one character name.")
            return
        if len(args) > 15: # Limit requests
             await ctx.send("Please request fewer than 15 characters at a time.")
             return

        async with ctx.typing():
            tasks = []
            char_realm_pairs = []
            for name_input in args:
                # Basic check for format: Name or Name-Realm
                parts = name_input.split('-', 1)
                char_name = parts[0]
                realm_input = parts[1] if len(parts) > 1 else DEFAULT_REALM
                norm_realm = normalize_realm_name(realm_input)

                if not char_name.isalpha():
                     await ctx.send(f"Skipping invalid character name format: '{name_input}'")
                     continue
                if not norm_realm:
                     await ctx.send(f"Skipping '{name_input}': Invalid realm '{realm_input}'")
                     continue

                # Don't fetch talents for multi-stalk to save time/resources
                tasks.append(
                    _fetch_and_build_character(
                        char_name, norm_realm, self.warmane_client, self.db_service, fetch_talents=False
                    )
                )
                char_realm_pairs.append((char_name, norm_realm))

            results: List[Optional[Character]] = await asyncio.gather(*tasks, return_exceptions=True)

            body_data = []
            for i, result in enumerate(results):
                char_name, norm_realm = char_realm_pairs[i]
                char_row = [f"{char_name.capitalize()}-{norm_realm}"] # Start row with name-realm

                if isinstance(result, Exception):
                    logger.error(f"Error fetching/building character {char_name}-{norm_realm} in multistalk: {result}")
                    char_row.extend(["Error", "Error", "Error", "Error", "Error"])
                elif result is None:
                    # Character not found
                    char_row.extend(["Not Found", "-", "-", "-", "-"])
                else:
                    # Character found, extract data
                    character = result
                    enchant_status = WarmaneParser.check_enchants(character.items, character.char_class, character.professions)
                    gem_status = WarmaneParser.check_gems(character.items)
                    # Simplify status for table
                    enchant_icon = OK if OK in enchant_status else ERROR if ERROR in enchant_status else "?"
                    gem_icon = OK if OK in gem_status else ERROR if ERROR in gem_status else "?"

                    spec_str = clean_data_for_table(character.specializations)
                    prof_str = clean_data_for_table(character.professions)

                    char_row.extend([
                        f"{character.gear_score:.0f}", # GS without decimals
                        enchant_icon,
                        gem_icon,
                        spec_str,
                        prof_str
                    ])

                body_data.append(char_row)

            if not body_data:
                await ctx.send("No valid characters found or processed.")
                return

            # --- Create ASCII Table ---
            try:
                output_table = t2a(
                    header=["Character", "GS", "E", "G", "Specialization", "Professions"],
                    body=body_data,
                    style=PresetStyle.thin_compact # Simple style
                )

                # Send in chunks if too long
                max_len = 1990 # Max length for code block
                if len(output_table) <= max_len:
                    await ctx.send(f"```\n{output_table}\n```")
                else:
                    await ctx.send("Output too long, sending in chunks:")
                    for i in range(0, len(output_table), max_len):
                         chunk = output_table[i:i + max_len]
                         await ctx.send(f"```\n{chunk}\n```")

            except Exception as e:
                logger.exception(f"Error generating table for multistalk: {e}")
                await ctx.send(embed=create_error_embed(description="Failed to generate the results table."))


    @commands.command(aliases=['talents', 'checktalents'])
    async def checkTalents(self, ctx: commands.Context, character_name: str, realm_name: str = DEFAULT_REALM):
        """Checks a character's talents against predefined templates (DK, Paladin supported)."""
        async with ctx.typing():
            norm_realm = normalize_realm_name(realm_name)
            if not norm_realm:
                await ctx.send(embed=create_error_embed("Invalid Realm", f"Could not recognize realm '{realm_name}'."))
                return

            # We need profile for class and talents page for points
            tasks = [
                self.warmane_client.get_profile_html(character_name, norm_realm),
                self.warmane_client.get_talents_html(character_name, norm_realm)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            profile_html = results[0]
            talent_html = results[1]

            # --- Error Handling ---
            if isinstance(profile_html, Exception) or isinstance(talent_html, Exception):
                logger.error(f"Failed to fetch data for talent check {character_name}-{norm_realm}")
                await ctx.send(embed=create_error_embed(description="Could not fetch required Armory pages."))
                return
            if not profile_html or not talent_html or not WarmaneParser.check_character_exists(profile_html):
                 await ctx.send(embed=create_char_not_found_embed(character_name, norm_realm))
                 return

            # --- Parsing ---
            try:
                _, _, char_class = WarmaneParser.extract_level_race_class(profile_html)
                talent_strings_dict = WarmaneParser.extract_talent_points_string(talent_html, char_class) # Dict: spec_id -> string
                _, active_spec_id = WarmaneParser.extract_specializations(profile_html) # Get active spec
            except Exception as e:
                logger.exception(f"Error parsing for talent check {character_name}-{norm_realm}: {e}")
                await ctx.send(embed=create_error_embed(description="Failed to parse Armory data for talent check."))
                return

            if not char_class:
                 await ctx.send(embed=create_error_embed(description="Could not determine character class."))
                 return
            if not talent_strings_dict:
                 await ctx.send(embed=create_error_embed(description="Could not parse talent points string(s)."))
                 return

            # --- Select Talent Checker ---
            talent_checker = None
            if "Death Knight" in char_class:
                talent_checker = dk_talents.check_talents
            elif "Paladin" in char_class:
                talent_checker = paladin_talents.check_talents
            elif "Druid" in char_class:
                talent_checker = druid_talents.check_talents
            elif "Hunter" in char_class:
                talent_checker = hunter_talents.check_talents
            elif "Mage" in char_class:
                talent_checker = mage_talents.check_talents
            elif "Priest" in char_class:
                talent_checker = priest_talents.check_talents
            elif "Rogue" in char_class:
                talent_checker = rogue_talents.check_talents
            elif "Shaman" in char_class:
                talent_checker = shaman_talents.check_talents
            elif "Warlock" in char_class:
                talent_checker = warlock_talents.check_talents
            elif "Warrior" in char_class:
                talent_checker = warrior_talents.check_talents
            else:
                # Handle unsupported class
                await ctx.send(embed=create_info_embed(
                    title="Unsupported Class",
                    description=f"Talent checks for '{char_class}' are not implemented yet."
                ))
                return

            # --- Perform Check and Send Embed ---
            # Check the active spec if possible, otherwise check all found specs
            specs_to_check = []
            if active_spec_id and active_spec_id in talent_strings_dict:
                 specs_to_check.append(talent_strings_dict[active_spec_id])
            else:
                 # If active spec unknown or string missing, check all available
                 specs_to_check.extend(talent_strings_dict.values())

            if not specs_to_check:
                 await ctx.send(embed=create_error_embed(description="No valid talent strings found to check."))
                 return

            for talent_string in specs_to_check:
                 try:
                     result_embed = talent_checker(talent_string, character_name, norm_realm)
                     await ctx.send(embed=result_embed)
                 except Exception as e:
                      logger.exception(f"Error running talent check for {char_class}: {e}")
                      await ctx.send(embed=create_error_embed(description=f"An error occurred while checking {char_class} talents."))
                 await asyncio.sleep(0.5) # Small delay between embeds if checking multiple specs


# --- Setup Function ---
async def setup(bot: commands.Bot):
    # Get loop for DB service
    loop = asyncio.get_running_loop()
    db_service = DatabaseService(loop)

    # Create shared aiohttp session
    http_session = aiohttp.ClientSession(loop=loop)

    # Create client service
    warmane_client = WarmaneClient(http_session)

    # Add cog with dependencies
    await bot.add_cog(StalkCog(bot, warmane_client, db_service))

    # Store session and db_service on bot for potential cleanup if needed
    # Or handle cleanup in Cog's unload method
    bot.http_session = http_session # Example: store session
    bot.db_service = db_service # Example: store db service

    # Connect DB after adding cog (or before, depending on preference)
    try:
        await db_service.connect()
    except Exception:
         # Bot should probably not start if DB fails
         logger.critical("DATABASE CONNECTION FAILED. StalkCog may not function.")
         # Optionally raise an error to stop bot startup
         # raise ConnectionError("Failed to connect to the database.")

async def teardown(bot: commands.Bot):
     # Clean up resources
     logger.info("Tearing down StalkCog resources...")
     if hasattr(bot, 'http_session') and bot.http_session:
          await bot.http_session.close()
          logger.info("aiohttp session closed.")
     if hasattr(bot, 'db_service') and bot.db_service:
          await bot.db_service.close()
          logger.info("Database pool closed.")

