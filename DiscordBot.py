import discord
from discord.ext import commands
from Warmane import QueryWarmaneArmory
import mariadb
from enum import IntEnum

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.bot ', intents=intents)

try:
    conn = mariadb.connect(
        user="<DB_USERNAME>",
        password="<DB_PASSWORD>",
        host="<DB_HOST>",
        port=3306,
        database="<DB_NAME>"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


@bot.command()
async def stalk(ctx, arg1, arg2="Icecrown"):
    await ctx.send(embed=create_stalk_response(arg1, arg2))


def error_char_not_found_embed():
    embed = discord.Embed(title=f"Error!", description="", color=discord.Color.red())
    embed.add_field(name="The character you are looking for does not exist or does not meet the minimum required level.!",value="", inline=False)
    return embed

def create_stalk_response(character,realm):
    profile_html = QueryWarmaneArmory.getHTML(character, realm, "summary")
    if QueryWarmaneArmory.check_for_error(profile_html):
        return error_char_not_found_embed()
    guild = QueryWarmaneArmory.extract_guild_from_profile(profile_html)
    race = QueryWarmaneArmory.extract_class_race_level_from_profile(profile_html)
    profs = QueryWarmaneArmory.extract_professions_from_profile(profile_html)
    specs = QueryWarmaneArmory.extract_specializations_from_profile(profile_html)
    items = QueryWarmaneArmory.extract_items_from_profile(profile_html)
    items_db = get_items_from_db(items)
    talent_html = QueryWarmaneArmory.getHTML(character,realm, "talents")
    glyphs = QueryWarmaneArmory.extract_glyphs_from_talents(talent_html)
    embed = discord.Embed(
        title=f"Character summary for {character.capitalize()}-{realm.capitalize()}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Level, Race, Class", value=f"{race}", inline=True)
    embed.add_field(name="Guild", value=f"{guild}", inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(
        name="Specializations",
        value=f"{format_prof_spec(specs)}",
        inline=True,
    )
    embed.add_field(
        name="Professions",
        value=f"{format_prof_spec(profs)}",
        inline=True,
    )
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(name="GearScore", value=f"{calculate_gearscore(items_db)}", inline=True)
    embed.add_field(name="Average item level", value=f"{calculate_avg_ilvl(items_db)}", inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(name="Enchants", value=f"{check_enchants(items, items_db, race, profs)}", inline=True)
    embed.add_field(name="Gems", value=f"{check_gems(items, items_db, profs)}", inline=True)
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(
        name="[1] Major Glyphs",
        value=f"{format_glyphs(glyphs, 0, "Major Glyphs")}",
        inline=True,
    )
    embed.add_field(
        name="[2] Major Glyphs", 
        value=f"{format_glyphs(glyphs, 1, "Major Glyphs")}", 
        inline=True)  # Empty field
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(
        name="[1] Minor Glyphs", 
        value=f"{format_glyphs(glyphs, "0", "Minor Glyphs")}", 
        inline=True)  # Empty field
    embed.add_field(
        name="[2] Minor Glyphs", 
        value=f"{format_glyphs(glyphs, "1", "Minor Glyphs")}",
        inline=True)  # Empty field
    embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(
        name="Link to Armory",
        value=f"[Armory Link](https://armory.warmane.com/character/{character.capitalize()}/{realm.capitalize()}/summary)",
        inline=False,
    )
    # Send the embed
    return embed

class Item_Types(IntEnum):
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
    OFF_HAND = 23
    RELIC = 28
    RANGED = 26

def format_prof_spec(prof_spec):
    return "\n".join([f"[{i + 1}] {profession}" for i, profession in enumerate(prof_spec)])

def format_glyphs(x, id, glyph_type):
    return "\n".join(x[f"{id}"][glyph_type])

def calculate_gearscore(items):
    gearscore = 0
    for itemid, value in items.items():
        if value[3] == 4 or value[3] == 19:
            continue
        gearscore += int(value[-1])
    return gearscore

def calculate_avg_ilvl(items):
    ilvl_total = 0
    count = 0
    for itemid, value in items.items():
        if value[3] == 4 or value[3] == 19:
            continue
        ilvl_total += int(value[1])
        count += 1
    try:
        return round(ilvl_total / count, 2)
    except ZeroDivisionError:
        return "0"


def check_enchants(items, item_db, class_, prof):
    not_enchanted = list()
    for item, value in items.items():
        db_item = item_db[int(item)]
        item_type = db_item[3]
        print(db_item[0], item_type)
        if item_type == Item_Types.NECK or item_type == Item_Types.SHIRT or item_type == Item_Types.TABARD \
            or item_type == Item_Types.TRINKET or item_type == Item_Types.WAIST:
            continue
        if "Mage" in class_ or "Warlock" in class_ or "Priest" in class_ or "Druid" in class_:
            if item_type == Item_Types.OFF_HAND or item_type == Item_Types.RANGED:
                continue
        if "Druid" in class_ or "Death Knight" in class_ or "Shaman" in class_ or "Paladin" in class_:
            if item_type == Item_Types.RELIC:
                continue
        if "Warrior" in class_ or "Rogue" in class_:
            if item_type == Item_Types.RANGED:
                continue
        if "Enchanting" not in prof:
            if item_type == Item_Types.RING:
                continue
        if value["enchant"] is None:
            not_enchanted.append(item_type)
        
    if len(not_enchanted) == 0:
        return "All items are enchanted!"
    else:
        print("Missing enchants", not_enchanted)
        return missing_enchant_message(not_enchanted)

def missing_enchant_message(missing):
    return_msg = "Enchants missing from: "
    missing_items_str = list()
    ring_counter = 1
    for type_id in missing:
        if type_id == Item_Types.HEAD:
            missing_items_str.append("Head")
        if type_id == Item_Types.SHOULDER:
            missing_items_str.append("Shoulders")
        if type_id == Item_Types.CHEST:
            missing_items_str.append("Chest")
        if type_id == Item_Types.BACK:
            missing_items_str.append("Back")
        if type_id == Item_Types.WRIST:
            missing_items_str.append("Wrist")
        if type_id == Item_Types.GLOVES:
            missing_items_str.append("Hands")
        if type_id == Item_Types.LEGS:
            missing_items_str.append("Legs")
        if type_id == Item_Types.FEET:
            missing_items_str.append("Feet")
        if type_id == Item_Types.RING:
            missing_items_str.append(f"Ring #{ring_counter}")
            ring_counter += 1
        if type_id == Item_Types.WEAPON_1H:
            missing_items_str.append("Weapon")
        if type_id == Item_Types.WEAPON_2H:
            missing_items_str.append("Weapon")
        if type_id == Item_Types.SHIELD:
            missing_items_str.append("Shield")
        if type_id == Item_Types.RANGED:
            missing_items_str.append("Ranged")
    return return_msg + ", ".join(missing_items_str)

def check_gems(items, item_db, profs):
    items_missing_gems = list()
    for item, value in items.items():
        db_item = item_db[int(item)]
        item_type = db_item[3]


        if item_type == Item_Types.WAIST:
            amount_of_gems = db_item[-2] + 1
        else:
            amount_of_gems = db_item[-2]
        
        
        if len(value['gems']) == amount_of_gems:
            continue
        items_missing_gems.append(item_type)
    if len(items_missing_gems) == 0:
        return "All items are gemmed!"
    else:
        print("Missing gems", items_missing_gems)
        return missing_gems_message(items_missing_gems)

def missing_gems_message(missing):
    return_msg = "Gems missing from: "
    missing_items_str = list()
    ring_counter = 1
    for type_id in missing:
        if type_id == Item_Types.HEAD:
            missing_items_str.append("Head")
        if type_id == Item_Types.NECK:
            missing_items_str.append("Neck")
        if type_id == Item_Types.SHOULDER:
            missing_items_str.append("Shoulders")
        if type_id == Item_Types.CHEST:
            missing_items_str.append("Chest")
        if type_id == Item_Types.BACK:
            missing_items_str.append("Back")
        if type_id == Item_Types.WRIST:
            missing_items_str.append("Wrist")
        if type_id == Item_Types.GLOVES:
            missing_items_str.append("Hands")
        if type_id == Item_Types.LEGS:
            missing_items_str.append("Legs")
        if type_id == Item_Types.FEET:
            missing_items_str.append("Feet")
        if type_id == Item_Types.RING:
            missing_items_str.append(f"Ring #{ring_counter}")
            ring_counter += 1
        if type_id == Item_Types.WEAPON_1H:
            missing_items_str.append("Weapon")
        if type_id == Item_Types.WEAPON_2H:
            missing_items_str.append("Weapon")
        if type_id == Item_Types.SHIELD:
            missing_items_str.append("Shield")
        if type_id == Item_Types.RANGED:
            missing_items_str.append("Ranged")
    return return_msg + ", ".join(missing_items_str)

def get_items_from_db(items):
    results = dict()
    for item,_ in items.items():
        cur = conn.cursor()
        cur.execute(
        "SELECT itemID,name,ItemLevel,quality,type,requires,class,subclass,gems,GearScore FROM items WHERE itemID=?", 
        (item,))
        for itemid, name, ilvl, quality, itemtype, requires, class_, sublcass, gems, gs in cur:
            results.update({itemid: [name, ilvl, quality, itemtype, requires, class_, sublcass, gems, gs]})
    return results

bot.run('<BOT_TOKEN')