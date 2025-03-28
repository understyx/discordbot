import requests
from bs4 import BeautifulSoup
import re
from enum import IntEnum
import discord
from table2ascii import table2ascii as t2a, PresetStyle
import paladin
import deathknight

OK = "✅"
ERROR = "❌"


def create_multi_response(*args, conn):
    body = list()
    for character in args:
        if character.isalpha():
            char_data = list()
            
            if len(character.split("-")) == 2:
                character = character.split("-")[0]
                realm = character.split("-")[1]
                char_data.append(character)
                char_data.append(realm)

                profile_html = getHTML(character, realm, "summary")
                char_data.append("H")
                char_data.append(extract_guild_from_profile(profile_html))

            else:
                realm = "Icecrown"

                char_data.append(character)

                profile_html = getHTML(character, realm, "summary")
                race = extract_class_race_level_from_profile(profile_html)

                items = extract_items_from_profile(profile_html)
                items_db = get_items_from_db(items, conn)
                profs = extract_professions_from_profile(profile_html)
                gems = check_gems(items, items_db, profs)
                if gems == "All items are gemmed!":
                    gems = OK
                else:
                    gems = ERROR
                enchants = check_enchants(items, items_db, race, profs)
                if enchants == "All items are enchanted!":
                    enchants = OK
                else:
                    enchants = ERROR

                
                char_data.append(calculate_gearscore(items_db))
                char_data.append(enchants)
                char_data.append(gems)
                char_data.append(clean_data(extract_specializations_from_profile(profile_html)))
                char_data.append(clean_data(profs))
            body.append(char_data)
        output = t2a(
    header=["Character", "Gearscore", "Enchants", "Gems", "Specialization", "   Professions   "],
    body=body,
    style=PresetStyle.thin_compact
    )
    return f"{output}"

def test_talents(character, realm):
    return getTalentPoints(character, realm)


def getTalentPoints(character, realm):
    talent_html = getHTML(character.capitalize(),realm.capitalize(), "talents")
    soup = BeautifulSoup(talent_html, "html.parser")
    containers = soup.find_all("div", class_="talents-container wotlk")
    class_ = extract_class_race_level_from_profile(talent_html)

    embed_return = list()
    for container in containers:
        talent_divs = container.find_all("div", class_="talent-points")
        talent_numbers = []
        for div in talent_divs:
            text = div.get_text(strip=True)  # e.g., "0/5"
            allocated = text.split("/")[0]    # e.g., "0"
            talent_numbers.append(allocated)
        talent_string = "".join(talent_numbers)
        print(talent_string)
        print(class_)
        match class_:
            case _ if "Paladin" in class_:
                print("PALADIN")
                embed_return.append(paladin.talent_check(talent_string, character, realm))
            case _ if "Death Knight" in class_:
                print("DEATH KNIGHT")
                embed_return.append(deathknight.talent_check(talent_string, character, realm))
            case _:
                embed = discord.Embed(
                    title=f"Tough luck, Sunshine! Your class isn't supported yet.",
                    color=discord.Color.blue()
                    )
                return [embed]
    return embed_return
