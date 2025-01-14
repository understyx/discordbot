import requests
from bs4 import BeautifulSoup
import re

class QueryWarmaneArmory():

    @staticmethod
    def getHTML(character, realm, dataType):
        header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"}
        url = f"http://armory.warmane.com/character/{character.capitalize()}/{realm.capitalize()}/{dataType}"
        r = requests.get(url, headers=header)
        if r.status_code != 200:
            return None
        return r.content

    @staticmethod
    def check_for_error(html):
        message = "The character you are looking for does not exist or does not meet the minimum required level."
        parser = BeautifulSoup(html, 'html.parser')
        if message in parser.text:
            return True
        else:
            return False

    @staticmethod
    def extract_items_from_profile(html):
        parser = BeautifulSoup(html, 'html.parser')
        rel_attributes = [tag['rel'] for tag in parser.find_all(attrs={'rel': True})]

        data = []
        for item in rel_attributes: #cleanup pass 1
            if "item" in item[0]:
                data.append(item[0])

        result = {}
        for item in data: #data into dict form for easier handling
            components = item.split("&")
            for component in components:
                if component.startswith("item="):
                    item_id = component.split("=")[1]
                    result[item_id] = {"enchant": None, "gems": []}
                elif component.startswith("ench="):
                    enchant_id = component.split("=")[1]
                    result[item_id]["enchant"] = enchant_id
                elif component.startswith("gems="):
                    gem_ids = component.split("=")[1].split(":")
                    result[item_id]["gems"] = [gem for gem in gem_ids if gem != "0"]
            
        return result

    @staticmethod
    def extract_guild_from_profile(html):
        parser = BeautifulSoup(html, 'html.parser')
        try:
            return parser.find('span', class_='guild-name').a.text
        except AttributeError:
            return ""
    
    @staticmethod
    def extract_professions_from_profile(html):
        parser = BeautifulSoup(html, 'html.parser')
        prof = parser.find('div', class_='profskills')
        try:
            text_divs = prof.find_all('div', class_='text')
        except AttributeError:
            return ["",""]
        results = []
        for div in text_divs:
            prof_name = div.contents[0].strip()
            prof_value = div.find('span', class_='value').text.strip()  # Span value
            results.append(f"{prof_name} ({prof_value})")
        return results

    @staticmethod
    def extract_specializations_from_profile(html):
        parser = BeautifulSoup(html, 'html.parser')
        spec = parser.find('div', class_='specialization')
        text_divs = spec.find_all('div', class_='text')

        results = []
        for div in text_divs:
            spec_name = div.contents[0].strip()
            try:
                spec_value = div.find('span', class_='value').text.strip()  # Span value
            except AttributeError:
                spec_value = "0 / 0 / 0"
            results.append(f"{spec_name} ({spec_value})")
        return results

    @staticmethod
    def extract_class_race_level_from_profile(html):
        parser = BeautifulSoup(html, 'html.parser')
        data = parser.find("div", class_="level-race-class").text
        result = re.findall(r"(\b[A-Za-z0-9]*[\s{1},])", data)
        result = "".join(result)
        return result[0:result.find(",")]
    
    def extract_glyphs_from_talents(html):
        parser = BeautifulSoup(html, 'html.parser')
        glyph_sections = parser.find_all('div', attrs={'data-glyphs': True})

        glyph_data = {}
        for section in glyph_sections:
            glyph_id = section['data-glyphs']  # e.g., "0", "1"
            glyph_data[glyph_id] = {
                "Major Glyphs": [],
                "Minor Glyphs": []
            }
            
            major_glyphs = section.find_all('div', class_='glyph major')
            for glyph in major_glyphs:
                glyph_name = glyph.find('a').text.strip()
                glyph_data[glyph_id]["Major Glyphs"].append(glyph_name)

            minor_glyphs = section.find_all('div', class_='glyph minor')
            for glyph in minor_glyphs:
                glyph_name = glyph.find('a').text.strip()
                glyph_data[glyph_id]["Minor Glyphs"].append(glyph_name)

        return glyph_data
