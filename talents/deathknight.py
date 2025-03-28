# talents/deathknight.py
from enum import IntEnum
import discord
from typing import List, Tuple, Dict
from utils.constants import OK, ERROR, WARNING, EMBED_COLOR_INFO
from talents.talent_utils import has_talent # Import from new location

# --- Keep Enum Definition ---
class DeathKnight(IntEnum):
    # ... (all enum members as provided) ...
    BLOOD_BUTCHERY          = 0
    BLOOD_SUBVERSION        = 1
    BLOOD_BLADE_BARRIER     = 2
    BLOOD_BLADED_ARMOR      = 3
    BLOOD_SCENT_OF_BLOOD    = 4
    BLOOD_TWO_HAND_WEP_SPEC = 5
    BLOOD_RUNE_TAP          = 6
    BLOOD_DARK_CONVICTION   = 7
    BLOOD_DEATH_RUNE_MASTERY = 8
    BLOOD_IMPROVED_RUNE_TAP = 9
    BLOOD_SPELL_DEFLECTION  = 10
    BLOOD_VENDETTA          = 11
    BLOOD_BLOODY_STRIKES    = 12
    BLOOD_VETERAN_OF_3RD_WAR = 13
    BLOOD_MARK_OF_BLOOD = 14
    BLOOD_BLOODY_VENGANCE = 15
    BLOOD_ABOMINATIONS_MIGHT = 16
    BLOOD_BLOODWORMS = 17
    BLOOD_HYSTERIA = 18
    BLOOD_IMP_BLOOD_PRESENCE = 19
    BLOOD_IMPROVED_DEATH_STRIKE = 20
    BLOOD_SUDDEN_DOOM = 21
    BLOOD_VAMPIRIC_BLOOD = 22
    BLOOD_WILL_OF_THE_NECROPOLIS = 23
    BLOOD_HEART_STRIKE = 24
    BLOOD_MIGHT_OF_MOGRAINE = 25
    BLOOD_BLOOD_GORGED = 26
    BLOOD_DANCING_RUNE_WEAPON = 27

    FROST_IMPROVED_ICY_TOUCH = 28
    FROST_RUNIC_POWER_MASTERY = 29
    FROST_TOUGHNESS = 30
    FROST_ICY_REACH = 31
    FROST_BLACK_ICE = 32
    FROST_NERVES_OF_COLD_STEEL = 33
    FROST_ICY_TALONS = 34
    FROST_LICHBORNE = 35
    FROST_ANNIHILATION = 36
    FROST_KILLING_MACHINE = 37
    FROST_CHILL_OF_THE_GRAVE = 38
    FROST_ENDLESS_WINTER = 39
    FROST_FRIGID_DEATHPLATE = 40
    FROST_GLACIER_ROT = 41
    FROST_DEATHCHILL = 42
    FROST_IMPROVED_ICY_TALONS = 43
    FROST_MERCILESS_COMBAT = 44
    FROST_RIME = 45
    FROST_CHILLBLAINS = 46
    FROST_HUNGERING_COLD = 47
    FROST_IMPROVED_FROST_PRESENCE = 48
    FROST_THREAT_OF_THASSARIAN = 49
    FROST_BLOOD_OF_THE_NORTH = 50
    FROST_UNBREAKABLE_ARMOR = 51
    FROST_ACCLIMATION = 52
    FROST_FROST_STRIKE = 53
    FROST_GUILE_OF_GOREFIEND = 54
    FROST_TUNDRA_STALKER = 55
    FROST_HOWLING_BLAST = 56

    UNHOLY_VICIOUS_STRIKES = 57
    UNHOLY_VIRULENCE = 58
    UNHOLY_ANTICIPATION = 59
    UNHOLY_EPIDEMIC = 60
    UNHOLY_MORBIDITY = 61
    UNHOLY_UNHOLY_COMMAND = 62
    UNHOLY_RAVENOUS_DEAD = 63
    UNHOLY_OUTBREAK = 64
    UNHOLY_NECROSIS = 65
    UNHOLY_CORPSE_EXPLOSION = 66
    UNHOLY_ON_PALE_HORSE = 67
    UNHOLY_BLOOD_CAKED_BLADE = 68
    UNHOLY_NIGHT_OF_THE_DEAD = 69
    UNHOLY_UNHOLY_BLIGHT = 70
    UNHOLY_IMPURITY = 71
    UNHOLY_DIRGE = 72
    UNHOLY_DESECRATION = 73
    UNHOLY_MAGIC_SUPPRESSION = 74
    UNHOLY_REAPING = 75
    UNHOLY_MASTER_OF_GHOULS = 76
    UNHOLY_DESOLATION = 77
    UNHOLY_ANTI_MAGIC_ZONE = 78
    UNHOLY_IMP_UH_PRES = 79
    UNHOLY_GHOUL_FRENZY = 80
    UNHOLY_CRYPT_FEVER = 81
    UNHOLY_BONE_SHIELD = 82
    UNHOLY_WANDERING_PLAGUE = 83
    UNHOLY_EBON_PLAGUEBRINGER = 84
    UNHOLY_SCOURGE_STRIKE = 85
    UNHOLY_RAGE_OF_RIVENDARE = 86
    UNHOLY_SUMMON_GARGOYLE = 87

# --- Talent Spec Definitions ---
# Format: [required_bool, TalentEnum, Error/Warning String, Expected Points, Mode, Justification]
TalentCheckList = List[Tuple[bool, DeathKnight, str, int, str, str]]

# TODO: Fill these lists accurately
dk_unholy_dps: TalentCheckList = [
     # Example:
     [True, DeathKnight.UNHOLY_SUMMON_GARGOYLE, ERROR + " Summon Gargoyle (Expected 1/1)", 1, "exact", "Core Unholy DPS cooldown."],
     [True, DeathKnight.UNHOLY_SCOURGE_STRIKE, ERROR + " Scourge Strike (Expected 1/1)", 1, "exact", "Main Unholy Strike."],
     [True, DeathKnight.UNHOLY_EBON_PLAGUEBRINGER, ERROR + " Ebon Plaguebringer (Expected 3/3)", 3, "exact", "Increases disease damage and provides raid magic debuff."],
     # ... Add all other relevant checks for Unholy DPS
]
dk_blood_tank: TalentCheckList = [
    # Keep the existing detailed list for Blood Tank
    [True, DeathKnight.BLOOD_BUTCHERY, ERROR + " Blood Butchery (Expected 0/5)", 0, "exact", "Does almost nothing for a Blood DK Tank."],
    [True, DeathKnight.BLOOD_SUBVERSION, ERROR + " Subversion (Expected 0/5)", 0, "exact", "Your main threat abilities are Icy Touches and Rune Strikes. DK Tanks have naturally lowest DPS, so this is extremely wasted talent point"],
    [True, DeathKnight.BLOOD_BLADE_BARRIER, ERROR + " Blade Barrer (Expected 5/5)", 5, "exact", "You gain 5% damage reduction for 10 sec when both of your blood runes go on CD."],
    [True, DeathKnight.BLOOD_BLADED_ARMOR, WARNING + " Bladed Armor (Expected 5/5)", 5, "exact", "Extra attack power. More damage for your icy touches and rune strikes"],
    [True, DeathKnight.BLOOD_SCENT_OF_BLOOD, WARNING + " Scent of Blood (Expected 1/3)", 1, "exact", "One point in this talent gives you enough runic power. You will be overcapping if you go for more points"],
    [True, DeathKnight.BLOOD_TWO_HAND_WEP_SPEC, WARNING + " Two-Handed Weapon Specialization (Expected 2/2)", 2, "exact", "Note: This talent will buff damage of spells that use weapon to hit enemy. Like rune strike. Icy touch is unaffected, because its damage is not based on weapon damage"],
    [True, DeathKnight.BLOOD_RUNE_TAP, ERROR + " Rune Tap (Expected 1/1)", 1, "exact", "Powerful self heal. Incredibly useful."],
    [True, DeathKnight.BLOOD_DARK_CONVICTION, ERROR + " Dark Conviction (Expected 5/5)", 5, "exact", "5% critical strike to all your attacks and abilities."],
    [True, DeathKnight.BLOOD_DEATH_RUNE_MASTERY, ERROR + " Death Rune Master (Expected 3/3)", 3, "exact", "Converts Frost and Unholy runes to death runes with Death Strike. Can be incredibly powerful"],
    [True, DeathKnight.BLOOD_IMPROVED_RUNE_TAP, ERROR + " Improved Rune Tap (Expected 3/3)", 3, "exact", "Increases rune taps healing done by 100% and reduces CD by 30 sec. Very strong talent"],
    [True, DeathKnight.BLOOD_SPELL_DEFLECTION, ERROR + " Spell Deflection (Expected 3/3)", 3, "exact", "Very powerful defensive talent vs enemies that cast spells."],
    #[True, DeathKnight.BLOOD_VENDETTA, ERROR +  0, "exact"], # Missing details
    [True, DeathKnight.BLOOD_BLOODY_STRIKES, ERROR + " Bloody Strikes (Expected 0/3)", 0, "exact", "You won't be using Blood Strike or Blood Boil enough for this to ever become better than other talents in the tree.."],
    [True, DeathKnight.BLOOD_VETERAN_OF_3RD_WAR, ERROR + " Veteran of the Third War (Expected 3/3)", 3, "exact", "Gives all good stats a tank needs."],
    [True, DeathKnight.BLOOD_MARK_OF_BLOOD, ERROR + " Mark of Blood (Expected 0/1)", 0, "exact", "It sounds like a strong heal, but it is incredibly deceiving. A mob can't auto attack you 20 times in 20 sec and on AoE proc it is roughly 1k * raid / party members heal on 3 min CD "],
    [True, DeathKnight.BLOOD_BLOODY_VENGANCE,ERROR + " Blood Vengance (Expected 3/3)", 3, "exact", "Buffs your melee damage (incl. rune strike) by upto 9%."],
    [True, DeathKnight.BLOOD_ABOMINATIONS_MIGHT, ERROR + " Abomination's Might (Expected 2/2)", 2, "exact", "Brings one of the two raid buffs Blood DK tanks are known for. Mandatory."],
    [True, DeathKnight.BLOOD_BLOODWORMS, ERROR + " Bloodworms (Expected 0/3)", 0, "exact", "Both the damage done and healing done by worms is incredibly low for a DK Tank. They also soak up AoE heals like hpala glyph, rshaman chain heal etc."],
    [True, DeathKnight.BLOOD_HYSTERIA, ERROR + " Hysteria (Expected 1/1)", 1, "exact", "Powerful offensive CD. 20% increased physical damage. Assuming equal gear / dps / skill: Feral > Rogue > Hunter > Fury"],
    [True, DeathKnight.BLOOD_IMP_BLOOD_PRESENCE, ERROR + " Improved Blood Presence (Expected 0/2)", 0, "exact", "Massive bait talent. Heal ends up being about ~40-60 HPS. Absolutely worthless talent."],
    [True, DeathKnight.BLOOD_IMPROVED_DEATH_STRIKE, ERROR + " Improved Death Strike (Expected 2/2)", 2, "exact", "Increases healing done by Death Strike by 50%. Very strong."],
    [True, DeathKnight.BLOOD_SUDDEN_DOOM, ERROR + " Sudden Doom (Expected 0/2)", 0, "exact", "Weak talent for extra damage. No other use."],
    [True, DeathKnight.BLOOD_VAMPIRIC_BLOOD, ERROR + " Vampiric Blood (Expected 1/1)", 1, "exact", "One of your strongest defensives when combiend with AMS."],
    [True, DeathKnight.BLOOD_WILL_OF_THE_NECROPOLIS, ERROR + " Will of the Necropolis (Expected 3/3)", 3, "exact", "Weaker version of Protection Paladins Ardent Defender. Still very strong talent. Especially useful on fights, where you take big hits like LK."],
    [True, DeathKnight.BLOOD_HEART_STRIKE,ERROR + " Heart Strike (Expecpted 0/1)", 0, "exact", "If you want to hold aggro on two targets, tabbing between them and icy touching is literally 10x more aggro than doing 10x heart strikes."],
    [True, DeathKnight.BLOOD_MIGHT_OF_MOGRAINE,ERROR + " Might of Mograine (Expected 0/3)", 0, "exact", "Increases the damage of your Death Strike, Heart Strike critical strike damage. You won't have enough critical strike for this to ever be useful"],
    [True, DeathKnight.BLOOD_BLOOD_GORGED, ERROR + " Blood Gorged (Expected 0/5)", 0, "exact", "To get this talent you need to give up points in the frost tree. Not worth it"],
    [True, DeathKnight.BLOOD_DANCING_RUNE_WEAPON, ERROR + " Dancing Rune Weapon (Expected 0/1)", 0, "exact", "Useless for a tank, only used for damage. The weapon's threat isn't copied to DK."],
    [True, DeathKnight.FROST_IMPROVED_ICY_TOUCH, ERROR + " Improved Icy Touch (Expected 3/3)", 3, "exact", "Increases the damage of your main threat generating ability and increases the attack speed slow that is applied to enemies infected by your frost fever."],
    [True, DeathKnight.FROST_TOUGHNESS, ERROR + " Toughness (Expected 5/5)", 5, "exact", "Increased armor."],
    [True, DeathKnight.FROST_ICY_TALONS, ERROR + " Icy Talons (Expected 5/5)", 5, "exact", "Increases your attack speed by 20%"],
    [True, DeathKnight.FROST_FRIGID_DEATHPLATE, ERROR + " Frigid Deathplate (Expected 3/3)", 3, "exact", "Reduces the attacks will hit you by 3%. Think of it as dodge that also applies to (some) spells."], # Note: Original had 5/5, likely typo, 3/3 is max
    [True, DeathKnight.FROST_IMPROVED_ICY_TALONS, ERROR + " Improved Icy Talons (Expected 1/1)", 1, "exact", "The second main raid wide buff that is brought by a Blood DK tank."]
]
dk_frost_dps: TalentCheckList = [
     # TODO: Add checks for Frost DPS (DW and 2H variants if needed)
     [True, DeathKnight.FROST_HOWLING_BLAST, ERROR + " Howling Blast (Expected 1/1)", 1, "exact", "Core Frost AoE and single target ability."],
     [True, DeathKnight.FROST_FROST_STRIKE, ERROR + " Frost Strike (Expected 1/1)", 1, "exact", "Main Runic Power spender for Frost."],
     # ...
]

# Map spec names to their talent check lists
SPEC_MAP: Dict[str, TalentCheckList] = {
    "Blood Tank": dk_blood_tank,
    "Frost DPS": dk_frost_dps,
    "Unholy DPS": dk_unholy_dps,
}

# --- Spec Detection ---
def detect_spec(talent_string: str) -> str:
    """Detects the likely DK spec based on key talents."""
    if not talent_string or len(talent_string) < DeathKnight.UNHOLY_SUMMON_GARGOYLE:
        return "Unknown" # Not enough points allocated or invalid string

    # Check deepest talents first
    if has_talent(talent_string, DeathKnight.UNHOLY_SUMMON_GARGOYLE, 1, "exact"):
        return "Unholy DPS"
    if has_talent(talent_string, DeathKnight.FROST_HOWLING_BLAST, 1, "exact"):
        return "Frost DPS"
    if has_talent(talent_string, DeathKnight.BLOOD_DANCING_RUNE_WEAPON, 1, "exact"):
         # Could be Blood DPS, less common. Need more checks if supporting this.
         return "Blood DPS (Uncommon)" # Placeholder
    if has_talent(talent_string, DeathKnight.BLOOD_WILL_OF_THE_NECROPOLIS, 1, "at_least"): # Check WotN for tank
        return "Blood Tank"

    # Fallback guess based on highest tree (less reliable)
    # blood_pts = sum(int(p) for p in talent_string[0:DeathKnight.FROST_IMPROVED_ICY_TOUCH])
    # frost_pts = sum(int(p) for p in talent_string[DeathKnight.FROST_IMPROVED_ICY_TOUCH:DeathKnight.UNHOLY_VICIOUS_STRIKES])
    # unholy_pts = sum(int(p) for p in talent_string[DeathKnight.UNHOLY_VICIOUS_STRIKES:])
    # if unholy_pts > frost_pts and unholy_pts > blood_pts: return "Unholy DPS"
    # if frost_pts > unholy_pts and frost_pts > blood_pts: return "Frost DPS"
    # if blood_pts > frost_pts and blood_pts > unholy_pts: return "Blood Tank" # Assume tank if blood is highest

    return "Unknown" # Cannot determine spec

# --- Talent Check Function ---
def check_talents(
    talent_string: str, character_name: str, realm_name: str
) -> discord.Embed:
    """Checks talents against predefined spec templates."""

    detected_spec = detect_spec(talent_string)
    talents_to_check = SPEC_MAP.get(detected_spec)

    embed = discord.Embed(
        title=f"Talent Check: {character_name.capitalize()} ({detected_spec})",
        color=EMBED_COLOR_INFO,
    )
    embed.set_footer(text=f"Realm: {realm_name.capitalize()}")

    if not talents_to_check:
        embed.description = f"Could not determine specialization or spec '{detected_spec}' is not supported for checks yet."
        embed.color = WARNING
        return embed

    issues_found = 0
    for required, talent, check_str, points, mode, justification in talents_to_check:
        is_met = has_talent(talent_string, talent, points, mode)

        # Check if the requirement matches the actual state
        if required != is_met:
            issues_found += 1
            # Add field with the pre-formatted error/warning string and justification
            embed.add_field(name=check_str, value=justification, inline=False)

    if issues_found == 0:
        embed.add_field(
            name=f"Looks good! {OK}",
            value="No major issues detected based on the template.",
            inline=False,
        )
    else:
         embed.description = f"Found {issues_found} potential issue(s) with the '{detected_spec}' talents."
         # Optionally change color if errors were found
         if any(ERROR in field.name for field in embed.fields):
              embed.color = discord.Color.red()
         elif any(WARNING in field.name for field in embed.fields):
              embed.color = discord.Color.orange()


    return embed
