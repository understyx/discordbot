import discord
from utils.constants import EMBED_COLOR_ERROR, EMBED_COLOR_INFO

def create_error_embed(title="Error!", description="An unexpected error occurred."):
    """Creates a standard error embed."""
    embed = discord.Embed(
        title=title, description=description, color=EMBED_COLOR_ERROR
    )
    return embed

def create_char_not_found_embed(character: str, realm: str):
    """Creates an embed for when a character is not found."""
    embed = discord.Embed(
        title="Character Not Found", color=EMBED_COLOR_ERROR
    )
    embed.add_field(
        name=f"Could not find {character.capitalize()}-{realm.capitalize()}",
        value="The character might not exist, be below level 10, or the Armory is down.",
        inline=False,
    )
    return embed

def create_info_embed(title="Info", description=""):
    """Creates a standard info embed."""
    embed = discord.Embed(
        title=title, description=description, color=EMBED_COLOR_INFO
    )
    return embed
