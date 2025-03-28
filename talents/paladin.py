# talents/paladin.py
from enum import IntEnum
import discord
from typing import List, Tuple, Dict
from utils.constants import OK, ERROR, WARNING, EMBED_COLOR_INFO
from talents.talent_utils import has_talent

# --- Keep Enum Definition ---
class Paladin(IntEnum):
    # ... (all enum members as provided) ...
    HOLY_SPIRITUAL_FOCUS    = 0
    HOLY_SEALS_OF_THE_PURE  = 1
    HOLY_HEALING_LIGHT      = 2
    HOLY_DIVINE_INTELLECT   = 3
    HOLY_UNYIELDING_FAITH   = 4
    HOLY_AURA_MASTERY       = 5
    HOLY_ILLUMINATION       = 6
    HOLY_IMP_LAY_ON_HANDS   = 7
    HOLY_IMP_CONC_AURA      = 8
    HOLY_IMP_WISDOM          = 9
    HOLY_BLESSED_HANDS          = 10
    HOLY_PURE_OF_HEART          = 11
    HOLY_DIVINE_FAVOR          = 12
    HOLY_SANCTIFIED_LIGHT          = 13
    HOLY_PURIFYING_POWER          = 14
    HOLY_HOLY_POWER          = 15
    HOLY_LIGHTS_GRACE          = 16
    HOLY_HOLY_SHOCK          = 17
    HOLY_BLESSED_LIFE          = 18
    HOLY_SACRED_CLEANSING         = 19
    HOLY_HOLY_GUIDANCE          = 20
    HOLY_DIVINE_ILLUMINATION          = 21
    HOLY_JUDGEMENTS_OF_THE_PURE          = 22
    HOLY_INFUSION_OF_LIGHT          = 23
    HOLY_ENLIGHTENED_JUDGEMENT          = 24
    HOLY_BEACON_OF_LIGHT          = 25

    PROTECTION_DIVINITY     = 26
    PROTECTION_DIVINE_STR     = 27
    PROTECTION_STOICISM     = 28
    PROTECTION_GUARDIANS_FAVOR     = 29
    PROTECTION_ANTICIPATION     = 30
    PROTECTION_DIVINE_SACRIFICE     = 31
    PROTECTION_IMP_RF     = 32
    PROTECTION_TOUGHNESS     = 33
    PROTECTION_DIVINE_GUARDIAN     = 34
    PROTECTION_IMP_HOJ    = 35
    PROTECTION_IMP_DEVO    = 36
    PROTECTION_BLESSING_OF_SANC    = 37
    PROTECTION_RECKONING    = 38
    PROTECTION_SACRED_DUTY    = 39
    PROTECTION_ONE_HAND_WEP    = 40
    PROTECTION_SPIRITUAL_ATTUNEMENT    = 41
    PROTECTION_HOLY_SHIELD    = 42
    PROTECTION_ARDENT_DEFENDER    = 43
    PROTECTION_REDOUBT    = 44
    PROTECTION_COMBAT_EXPERTISE    = 45
    PROTECTION_TOUCHED_BY_THE_LIGHT    = 46
    PROTECTION_AVENGERS_SHIELD    = 47
    PROTECTION_GUARDED_BY_THE_LIGHT    = 48
    PROTECTION_SHIELD_OF_THE_TEMPLAR    = 49
    PROTECTION_JUDGEMENTS_OF_THE_JUST    = 50
    PROTECTION_HAMMER_OF_THE_RIGHTEOUS    = 51

    RETRIBUTION_DEFLECTION    = 52
    RETRIBUTION_BENEDICTION    = 53
    RETRIBUTION_IMP_JUDGE    = 54
    RETRIBUTION_HEART_OF_THE_CRUSADER    = 55
    RETRIBUTION_IMP_BOM    = 56
    RETRIBUTION_VINDICATION    = 57
    RETRIBUTION_CONVICTION    = 58
    RETRIBUTION_SEAL_OF_COMMAND    = 59
    RETRIBUTION_PURSUIT_OF_JUSTICE    = 60
    RETRIBUTION_EYE_FOR_AN_EYE   = 61
    RETRIBUTION_SANCTITY_OF_BATTLE   = 62
    RETRIBUTION_CRUSADE   = 63
    RETRIBUTION_TWO_HAND_WEP   = 64
    RETRIBUTION_SANCTIFIED_RET   = 65
    RETRIBUTION_VENGEANCE   = 66
    RETRIBUTION_DIVINE_PURPOSE   = 67
    RETRIBUTION_ART_OF_WAR   = 68
    RETRIBUTION_REPENTANCE   = 69
    RETRIBUTION_JUDGEMENTS_OF_THE_WISE   = 70
    RETRIBUTION_FANATICISM  = 71
    RETRIBUTION_SANCTIFIED_WRATH   = 72
    RETRIBUTION_SWIFT_RETRIBUTION   = 73
    RETRIBUTION_CRUSADER_STRIKE   = 74
    RETRIBUTION_SHEATH_OF_LIGHT   = 75
    RETRIBUTION_RIGHTEOUS_VENGANCE   = 76
    RETRIBUTION_DIVINE_STORM   = 77

# --- Talent Spec Definitions ---
TalentCheckList = List[Tuple[bool, Paladin, str, int, str, str]]

paladin_holy: TalentCheckList = [
    # Keep existing list
    [True, Paladin.HOLY_SPIRITUAL_FOCUS, ERROR + " Spiritual Focus (Expected 5/5)", 5, "exact", "Core talent for casting without pushback"],
    [True, Paladin.HOLY_SEALS_OF_THE_PURE, ERROR + " Seals of the Pure (Expected 0/5)", 0, "exact", "Does nothing for Holy."],
    [True, Paladin.HOLY_HEALING_LIGHT, ERROR + " Healing Light (Expected 3/3)", 3, "exact", "Increases healing effectiveness"],
    [True, Paladin.HOLY_DIVINE_INTELLECT, ERROR + " Divine Intellect (Expected 5/5)", 5, "exact", "Increases intellect for better mana pool and gives more spellpower through other talents"],
    [True, Paladin.HOLY_UNYIELDING_FAITH, ERROR + " Unyielding Faith (Expected 0/2)", 0, "exact", "Situational crowd control reduction. Never used in PvE"],
    [True, Paladin.HOLY_AURA_MASTERY, ERROR + " Aura Mastery (Expected 1/1)", 1, "exact", "Doubles aura effects for short duration. One of the best defensive cooldowns in the game."],
    [True, Paladin.HOLY_ILLUMINATION, ERROR + " Illumination (Expected 5/5)", 5, "exact", "Mana return on critical heals"],
    [True, Paladin.HOLY_IMP_CONC_AURA, ERROR + " Improved Concentration Aura (Expected 0/3)", 0, "exact", "Improves concentration aura effectiveness. Rarely ever useful in PvE"],
    [True, Paladin.HOLY_PURE_OF_HEART, ERROR + " Pure of Heart (Expected 0/3)", 0, "exact", "Reduces duration of curses and diseases. Never useful in PvE"],
    [True, Paladin.HOLY_DIVINE_FAVOR, ERROR + " Divine Favor (Expected 1/1)", 1, "exact", "Guaranteed crit heal or Holy Shock. Needed to pick better talents down below."],
    [True, Paladin.HOLY_SANCTIFIED_LIGHT, ERROR + " Sanctified Light (Expected 3/3)", 3, "exact", "Increases critical strike chance of Holy Light."],
    [True, Paladin.HOLY_PURIFYING_POWER, ERROR + " Purifying Power (Expected 0/2)", 0, "exact", "Simply not useful in PvE."],
    [True, Paladin.HOLY_HOLY_POWER, ERROR + " Holy Power (Expected 5/5)", 5, "exact", "Increases Holy critical strike chance"],
    [True, Paladin.HOLY_LIGHTS_GRACE, ERROR + " Light’s Grace (Expected 3/3)", 3, "exact", "Speeds up Holy Light casting"],
    [True, Paladin.HOLY_HOLY_SHOCK, ERROR + " Holy Shock (Expected 1/1)", 1, "exact", "Instant cast Holy damage or healing"],
    [True, Paladin.HOLY_BLESSED_LIFE, ERROR + " Blessed Life (Expected 0/3)", 0, "exact", "4%/8%/12% Chance to take half damage. Not consistent enough to pick it up for PvE."],
    [True, Paladin.HOLY_SACRED_CLEANSING, ERROR + " Sacred Cleansing (Expected 0/3)", 0, "exact", "Chance to increase resistance when cleansing. Purely PvP talent"],
    [True, Paladin.HOLY_HOLY_GUIDANCE, ERROR + " Holy Guidance (Expected 5/5)", 5, "exact", "Spellpower increase based on intellect"],
    [True, Paladin.HOLY_DIVINE_ILLUMINATION, ERROR + " Divine Illumination (Expected 1/1)", 1, "exact", "Halves mana cost of all spells temporarily"],
    [True, Paladin.HOLY_JUDGEMENTS_OF_THE_PURE, ERROR + " Judgements of the Pure (Expected 5/5)", 5, "exact", "Haste increase after Judging"],
    [True, Paladin.HOLY_INFUSION_OF_LIGHT, ERROR + " Infusion of Light (Expected 2/2)", 2, "exact", "Holy Shock criticals reduce the cast time of next Flash of Light or increase crit chance of next Holy Light"],
    [True, Paladin.HOLY_ENLIGHTENED_JUDGEMENT, ERROR + " Enlightened Judgement (Expected 2/2)", 2, "exact", "Increases Judgment range and hit"],
    [True, Paladin.HOLY_BEACON_OF_LIGHT, ERROR + " Beacon of Light (Expected 1/1)", 1, "exact", "Duplicate healing onto another target"],
    [True, Paladin.PROTECTION_DIVINITY, ERROR + " Divinity (Expected 5/5)", 5, "exact", "Increases healing done by you by 5%"],
    [True, Paladin.PROTECTION_DIVINE_SACRIFICE, ERROR + " Divine Sacrifice (Expected 1/1)", 1, "exact", "Provides access to one of the most powerful raid CDs"],
    [True, Paladin.PROTECTION_DIVINE_GUARDIAN, ERROR + " Divine Guardian (Expected 2/2)", 2, "exact", "Raid Wide 20% damage reduction on divine sacrifice cast, increases duration of sacred shield from 30s to 60s"],
    [True, Paladin.PROTECTION_IMP_DEVO, WARNING + " Improved Devotion Aura (Expected 3/3)", 3, "exact", "Increased healing done to raid. Not stricly required, but very nice to have."],
]
paladin_prot: TalentCheckList = [
    # Keep existing list
    [True, Paladin.PROTECTION_HAMMER_OF_THE_RIGHTEOUS, ERROR + " Hammer of the Righteous (Expected 1/1)",    1, "exact", "Protection Paladin capstone talent"],
    [False, Paladin.PROTECTION_DIVINITY, WARNING + " Divinity (Expected 0/5)",                                 1, "at_least", "Only pick this up if your healers are slacking or you're doing very hard content where you actually need every last heal."],
    [False, Paladin.PROTECTION_STOICISM, ERROR + " Stoicism (Expected 0/3)",                                  1, "at_least", "You're not going to be stunned often enough for this to be useful over other talents."],
    [False, Paladin.PROTECTION_GUARDIANS_FAVOR, WARNING + " Guardian's Favor (Expected 0/2)",                   1, "at_least", "Could be useful, but most of the time it's better to put those points somewhere else."],
    [True, Paladin.PROTECTION_DIVINE_STR, ERROR + " Divine Strength (Expected 5/5)",                        5, "exact", "Strength provides Block Value (survivability) and more threat."],
    [True, Paladin.PROTECTION_ANTICIPATION, ERROR + " Anticipation (Expected 5/5)",                         5, "exact", "Free dodge."],
    [True, Paladin.PROTECTION_DIVINE_SACRIFICE, ERROR + " Divine Sacrifice (Expected 1/1)",                 1, "exact", "Required for Divine Guardian talent and in some specific uses, extra sac on other tank/party."],
    [True, Paladin.PROTECTION_IMP_RF, ERROR + " Improved Righteous Fury (Expected 3/3)",                    3, "exact", "Free damage reduction."],
    [True, Paladin.PROTECTION_TOUGHNESS, ERROR + " Toughness (Expected 5/5)",                               5, "exact", "Free armor."],
    [True, Paladin.PROTECTION_DIVINE_GUARDIAN, ERROR + " Divine Guardian (Expected 2/2)",                   2, "exact", "This is the reason you pick up Divine Sacrifice talent: 20% damage reduction for 6s for the ENTIRE RAID."],
    [False, Paladin.PROTECTION_IMP_HOJ, WARNING +" Improved Hammer of Justice (Expected 0/2)",                 1, "at_least", "Generally not required."],
    [True, Paladin.PROTECTION_IMP_DEVO, WARNING + " Improved Devotion Aura (Expected 3/3)",                   3, "exact", "Free armor and increased healing done to raid. (2nd part can be provided by resto druid.)"],
    [True, Paladin.PROTECTION_BLESSING_OF_SANC, ERROR + " Blessing of Sanctuary (Expected 1/1)",            1, "exact", "Main way you're going to regenerate mana."],
    [True, Paladin.PROTECTION_RECKONING, WARNING + " Reckoning (Expected 1/5)",                               1, "exact", "Nice to have for extra damage / threat."],
    [False, Paladin.PROTECTION_RECKONING, WARNING + " Reckoning (Expected 1/5)",                                5, "exact", "5 points should be only taken if you REALLY need it for threat or you want to do some DPS."],
    [True, Paladin.PROTECTION_SACRED_DUTY, ERROR + " Sacred Duty (Expected 2/2)",                           2, "exact", "Stamina and your main damage reduction cooldown reduction."],
    [True, Paladin.PROTECTION_ONE_HAND_WEP, ERROR + " One-Handed Weapon Specialization (Expected 3/3)",     3, "exact", "Free damage => more threat."],
    [True, Paladin.PROTECTION_SPIRITUAL_ATTUNEMENT, WARNING + " Spiritual Attunement (Expected 1/2)", 1, "at_least", "You should generally have 1 point here. Exceptions exist."],
    [False, Paladin.PROTECTION_SPIRITUAL_ATTUNEMENT, ERROR + " Spiritual Attunement (Expected 1/2)",          2, "exact", "1 talent point is enough to not run OOM in a raid setting."],
    [True, Paladin.PROTECTION_HOLY_SHIELD, ERROR + " Holy Shield (Expected 1/1)",                           1, "exact", "30% Chance to block + damage on block."],
    [True, Paladin.PROTECTION_ARDENT_DEFENDER, ERROR + " Ardent Defender (Expected 3/3)",                   3, "exact", "The most OP tanking talent in Wrath. Provides cheat death and damage taken reduction."],
    [True, Paladin.PROTECTION_REDOUBT, ERROR + " Redoubt (Expected 3/3)",                                   3, "exact", "Increased block value and block chance proc."],
    [True, Paladin.PROTECTION_COMBAT_EXPERTISE, ERROR + " Combat Expertise (Expected 3/3)",                 3, "exact", "Increases expertise, stamina, and gives 6% critical strike."],
    [True, Paladin.PROTECTION_TOUCHED_BY_THE_LIGHT, ERROR + " Touched by the Light (Expected 3/3)",         3, "exact", "Some of your spells scale off spell power."],
    [True, Paladin.PROTECTION_AVENGERS_SHIELD, ERROR + " Avenger’s Shield (Expected 1/1)",                  1, "exact", "Required to reach Shield of the Templar talent. Extra button for ranged pulls."],
    [True, Paladin.PROTECTION_GUARDED_BY_THE_LIGHT, ERROR + " Guarded by the Light (Expected 2/2)",         2, "exact", "6% spell damage taken reduction and divine plea uptime."],
    [True, Paladin.PROTECTION_SHIELD_OF_THE_TEMPLAR, ERROR + " Shield of the Templar (Expected 3/3)",       3, "exact", "Damage taken reduced by 3%."],
    [False, Paladin.PROTECTION_JUDGEMENTS_OF_THE_JUST, WARNING + " Judgements of the Just (Expected 0/2)",      1, "at_least", "Only useful if you do not have a DK in the raid and you need the 10%/20% attack speed slow."],
    [True, Paladin.RETRIBUTION_DEFLECTION, ERROR + " Deflection (Expected 5/5)",                            5, "exact", "Free 5% parry."],
    [False, Paladin.RETRIBUTION_BENEDICTION, ERROR + " Benediction (Expected 0/5)",                           1, "at_least", "You're never gonna run out of mana if you play properly."],
    [True, Paladin.RETRIBUTION_IMP_JUDGE, ERROR + " Improved Judgement (Expected 2/2)",                     2, "exact", "More threat."],
    [True, Paladin.RETRIBUTION_HEART_OF_THE_CRUSADER, ERROR + " Heart of the Crusader (Expected 3/3)",      3, "exact", "Standard to have it taken, provides 3% crit."],
    [False, Paladin.RETRIBUTION_IMP_BOM, ERROR +" Improved Blessing of Might (Expected 0/2)",                1, "at_least", "You should never have to take it. You have to give up other useful stuff for this talent."],
    [True, Paladin.RETRIBUTION_VINDICATION, ERROR + " Vindication (Expected 2/2)",                          2, "exact", "574 AP reduction, 100% uptime, roughly equals 10-15% physical damage reduction. Can be provided by other classes, but prot/ret paladins are most reliable."],
    [True, Paladin.RETRIBUTION_CONVICTION, WARNING + " Conviction (Expected at most 3/5)",                            3, "at_most", "Free threat. Generally, you'll have 3 points here, more and you're sacrificing some other talent."],
    [True, Paladin.RETRIBUTION_SEAL_OF_COMMAND, ERROR + " Seal of Command (Expected 1/1)",                  1, "exact", "AoE damage/threat."],
    [False, Paladin.RETRIBUTION_PURSUIT_OF_JUSTICE, ERROR + " Pursuit of Justice (Expected 0/2)",             1, "at_least", "You're a tank, you don't need to chase bosses to maximize damage/threat."],
    [False, Paladin.RETRIBUTION_EYE_FOR_AN_EYE, ERROR + " Eye for an Eye (Expected 0/2)",                     1, "at_least", "You're a tank, you can't be crit."],
    [False, Paladin.RETRIBUTION_SANCTITY_OF_BATTLE, ERROR + " Sanctity of Battle (Expected 0/3)",             1, "at_least", "Crusade talent provides more damage/threat."],
    [True, Paladin.RETRIBUTION_CRUSADE, ERROR + " Crusade (Expected 3/3)",                                  3, "exact", "Free 6% (in ICC) damage increase."],
]
paladin_ret: TalentCheckList = [
    # Keep existing list
    [True, Paladin.HOLY_SEALS_OF_THE_PURE, ERROR + "Seals of the Pure (Expected 5/5)", 5, "exact"," Increases damage done by your main seal."],
    [True, Paladin.HOLY_AURA_MASTERY, ERROR + " Aura Mastery (Expected 1/1)", 1, "exact", "Doubles aura effects for short duration. One of the best defensive cooldowns in the game."], # Note: Ret usually doesn't take this, maybe optional?
    [True, Paladin.RETRIBUTION_DEFLECTION, ERROR + " Deflection (Expected 0/5)", 0, "exact", "Not useful for retribution"], # Corrected expected points
    [True, Paladin.RETRIBUTION_BENEDICTION, ERROR + " Benediction (Expected 5/5)", 5, "exact", "Reduces mana cost of Judgements and Seals"],
    [True, Paladin.RETRIBUTION_IMP_JUDGE, ERROR + " Improved Judgement (Expected 2/2)", 2, "exact", "Reduces cooldown of Judgement"],
    [True, Paladin.RETRIBUTION_HEART_OF_THE_CRUSADER, ERROR + " Heart of the Crusader (Expected 3/3)", 3, "exact", "Increases critical strike chance against targets affected by Judgement"],
    [True, Paladin.RETRIBUTION_IMP_BOM, ERROR + " Improved Blessing of Might (Expected 2/2)", 2, "exact", "Increases the effectiveness of Blessing of Might"],
    [False, Paladin.RETRIBUTION_VINDICATION, OK + " Vindication", 2, "exact", "Reduces target's attack power. Nice to have on retribution paladin."],
    [True, Paladin.RETRIBUTION_CONVICTION, ERROR + " Conviction (Expected 5/5)", 5, "exact", "Increases critical strike chance"],
    [True, Paladin.RETRIBUTION_SEAL_OF_COMMAND, ERROR + " Seal of Command (Expected 1/1)", 1, "exact", "Primary seal for Retribution Paladins"],
    [True, Paladin.RETRIBUTION_PURSUIT_OF_JUSTICE, WARNING + " Pursuit of Justice (Expected 2/2)", 2, "exact", "Increases movement speed and hit chance"], # Note: Often skipped for more DPS talents
    [True, Paladin.RETRIBUTION_EYE_FOR_AN_EYE, ERROR + " Eye for an Eye (Expected 0/2)", 0, "exact", "Reflects damage taken from critical strikes. Awful in PvE"],
    [True, Paladin.RETRIBUTION_SANCTITY_OF_BATTLE, ERROR + " Sanctity of Battle (Expected 3/3)", 3, "exact", "Increases damage done by Judgements and Seals"], # Note: Often skipped for Crusade
    [True, Paladin.RETRIBUTION_CRUSADE, ERROR + " Crusade (Expected 3/3)", 3, "exact", "Increases damage against Humanoids, Demons, Undead, and Elementals"],
    [True, Paladin.RETRIBUTION_TWO_HAND_WEP, ERROR + " Two-Handed Weapon Specialization (Expected 3/3)", 3, "exact", "Increases damage with two-handed weapons"],
    [True, Paladin.RETRIBUTION_SANCTIFIED_RET, ERROR + " Sanctified Retribution (Expected 1/1)", 1, "exact", "Increases damage done by Retribution Aura"],
    [True, Paladin.RETRIBUTION_VENGEANCE, ERROR + " Vengeance (Expected 3/3)", 3, "exact", "Increases attack power after landing a critical strike"],
    [False, Paladin.RETRIBUTION_DIVINE_PURPOSE, ERROR + " Divine Purpose (Expected 0/2)", 0, "exact", "Reduces chance to be hit by spells and ranged attacks and HoF removes stun. Purely PvP talent"], # Corrected expected points
    [True, Paladin.RETRIBUTION_ART_OF_WAR, ERROR + " Art of War (Expected 2/2)", 2, "exact", "Gives a chance to reduce the cooldown of Exorcism and Holy Wrath"],
    [True, Paladin.RETRIBUTION_REPENTANCE, ERROR + " Repentance (Expected 1/1)", 1, "exact", "Crowd control ability"], # Note: Often skipped in PvE
    [True, Paladin.RETRIBUTION_JUDGEMENTS_OF_THE_WISE, ERROR + " Judgements of the Wise (Expected 3/3)", 3, "exact", "Restores mana when Judgement is used"],
    [True, Paladin.RETRIBUTION_FANATICISM, ERROR + " Fanaticism (Expected 3/3)", 3, "exact", "Increases critical strike chance and reduces threat generated"],
    [True, Paladin.RETRIBUTION_SANCTIFIED_WRATH, ERROR + " Sanctified Wrath (Expected 2/2)", 2, "exact", "Increases critical strike chance of Hammer of Wrath"],
    [True, Paladin.RETRIBUTION_SWIFT_RETRIBUTION, ERROR + " Swift Retribution (Expected 3/3)", 3, "exact", "Increases attack speed for the party"],
    [True, Paladin.RETRIBUTION_CRUSADER_STRIKE, ERROR + " Crusader Strike (Expected 1/1)", 1, "exact", "Primary damage ability"],
    [True, Paladin.RETRIBUTION_SHEATH_OF_LIGHT, ERROR + " Sheath of Light (Expected 3/3)", 3, "exact", "Increases spell power based on attack power"],
    [True, Paladin.RETRIBUTION_RIGHTEOUS_VENGANCE, ERROR + " Righteous Vengeance (Expected 3/3)", 3, "exact", "Adds a damage over time effect to critical strikes"],
    [True, Paladin.RETRIBUTION_DIVINE_STORM, ERROR + " Divine Storm (Expected 1/1)", 1, "exact", "Powerful AoE ability"],
]

SPEC_MAP: Dict[str, TalentCheckList] = {
    "Holy": paladin_holy,
    "Protection": paladin_prot,
    "Retribution": paladin_ret,
}

# --- Spec Detection ---
def detect_spec(talent_string: str) -> str:
    """Detects the likely Paladin spec based on key talents."""
    if not talent_string or len(talent_string) < Paladin.RETRIBUTION_DIVINE_STORM:
        return "Unknown"

    if has_talent(talent_string, Paladin.RETRIBUTION_DIVINE_STORM, 1, "exact"):
        return "Retribution"
    if has_talent(talent_string, Paladin.PROTECTION_HAMMER_OF_THE_RIGHTEOUS, 1, "exact"):
        return "Protection"
    if has_talent(talent_string, Paladin.HOLY_BEACON_OF_LIGHT, 1, "exact"):
        return "Holy"

    # Fallback guess (less reliable)
    # holy_pts = sum(int(p) for p in talent_string[0:Paladin.PROTECTION_DIVINITY])
    # prot_pts = sum(int(p) for p in talent_string[Paladin.PROTECTION_DIVINITY:Paladin.RETRIBUTION_DEFLECTION])
    # ret_pts = sum(int(p) for p in talent_string[Paladin.RETRIBUTION_DEFLECTION:])
    # if ret_pts > prot_pts and ret_pts > holy_pts: return "Retribution"
    # if prot_pts > ret_pts and prot_pts > holy_pts: return "Protection"
    # if holy_pts > prot_pts and holy_pts > ret_pts: return "Holy"

    return "Unknown"

# --- Talent Check Function ---
def check_talents(
    talent_string: str, character_name: str, realm_name: str
) -> discord.Embed:
    """Checks talents against predefined spec templates."""
    # This function is identical to the DK one, just uses Paladin specs
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
        if required != is_met:
            issues_found += 1
            embed.add_field(name=check_str, value=justification, inline=False)

    if issues_found == 0:
        embed.add_field(
            name=f"Looks good! {OK}",
            value="No major issues detected based on the template.",
            inline=False,
        )
    else:
         embed.description = f"Found {issues_found} potential issue(s) with the '{detected_spec}' talents."
         if any(ERROR in field.name for field in embed.fields):
              embed.color = discord.Color.red()
         elif any(WARNING in field.name for field in embed.fields):
              embed.color = discord.Color.orange()

    return embed
