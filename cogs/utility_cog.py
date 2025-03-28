# cogs/utility_cog.py
import discord
from discord.ext import commands
import logging
import config # Import your config
from utils.embeds import create_info_embed, create_error_embed
from utils.constants import EMBED_COLOR_INFO

logger = logging.getLogger(__name__)

class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("UtilityCog initialized.")

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Provides the bot's invite link."""
        # Generate invite link with necessary permissions (adjust scope/perms as needed)
        # Example: Read/Send Messages, Embed Links
        perms = discord.Permissions(send_messages=True, embed_links=True, read_messages=True)
        invite_link = discord.utils.oauth_url(self.bot.user.id, permissions=perms, scopes=("bot",))
        await ctx.send(f"Here is the invite link: <{invite_link}>")


    @commands.command()
    async def complain(self, ctx: commands.Context, *, message: str):
        """Sends a complaint message to the bot owner."""
        if not message:
            await ctx.send("Please provide a message for your complaint.")
            return

        try:
            owner = await self.bot.fetch_user(config.OWNER_USER_ID)
            if not owner:
                await ctx.send(embed=create_error_embed(description="Could not find the bot owner to send the complaint."))
                return

            sender = ctx.author
            complaint_message = (
                f"**Complaint from {sender} ({sender.id}) in server '{ctx.guild.name if ctx.guild else 'DM'}':**\n"
                f"```\n{message}\n```"
            )

            # Handle potential message length issues
            if len(complaint_message) > 2000:
                complaint_message = complaint_message[:1990] + "... (truncated)"

            await owner.send(complaint_message)
            await ctx.send("Your complaint has been forwarded to the bot owner!")
            logger.info(f"Complaint sent from {sender.id} to owner {config.OWNER_USER_ID}")

        except discord.NotFound:
             await ctx.send(embed=create_error_embed(description="Could not find the bot owner (invalid OWNER_USER_ID?)."))
        except discord.Forbidden:
             await ctx.send(embed=create_error_embed(description="I cannot DM the bot owner. They might have DMs disabled or have blocked me."))
             logger.warning(f"Failed to send complaint DM to owner {config.OWNER_USER_ID} (Forbidden).")
        except Exception as e:
            logger.exception(f"Error sending complaint from {ctx.author.id}: {e}")
            await ctx.send(embed=create_error_embed(description="An unexpected error occurred while sending the complaint."))


    @commands.command()
    async def info(self, ctx: commands.Context):
        """Displays information about the bot and its commands."""
        embed = discord.Embed(
            title="T3 Bot Command List",
            description="Fetch information from Warmane Armory.",
            color=EMBED_COLOR_INFO
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url) # Use bot's avatar

        # Stalk Cog Commands (assuming prefix is '.bot ')
        embed.add_field(
            name="🔍 `.bot stalk <character> [realm]`",
            value="Shows a detailed summary for a character. Realm defaults to Icecrown.\n"
                  "*Example:* `.bot stalk Puredecay Lordaeron`",
            inline=False
        )
        embed.add_field(
            name="👥 `.bot multistalk <char1> [char2-realm] ...`",
            value="Shows a quick overview (GS, Ench, Gem, Spec, Prof) for multiple characters. Realm defaults to Icecrown.\n"
                  "*Example:* `.bot multistalk Puredecay Cloudsky-Lordaeron Qtqueenx`",
            inline=False
        )
        embed.add_field(
            name="✨ `.bot checkTalents <character> [realm]`",
            value="Checks character talents against predefined templates (DK, Paladin supported).\n"
                  "*Example:* `.bot checkTalents Puredecay`",
            inline=False
        )

        # Utility Cog Commands
        embed.add_field(
            name="ℹ️ `.bot info`",
            value="Shows this help message.",
            inline=False
        )
        embed.add_field(
            name="✉️ `.bot invite`",
            value="Get the link to invite this bot to your server.",
            inline=False
        )
        embed.add_field(
            name="📢 `.bot complain <message>`",
            value="Send feedback or a complaint directly to the bot owner.\n"
                  "*Example:* `.bot complain This bot needs more features!`",
            inline=False
        )

        embed.set_footer(text="Bot Owner: foxgirls4life (Neko/Edgy) | Send complaints!")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner() # Restrict this command to the bot owner defined in config
    async def serverinfo(self, ctx: commands.Context):
        """(Owner only) Shows the number of servers the bot is in."""
        guild_count = len(self.bot.guilds)
        await ctx.send(f"Bot is connected to **{guild_count}** Discord server(s).")
        logger.info(f"Server info requested by owner. Bot is in {guild_count} guilds.")
        # Optionally list guild names to console for owner
        # print("Guilds:")
        # for guild in self.bot.guilds:
        #     print(f"- {guild.name} (ID: {guild.id})")

    @serverinfo.error
    async def serverinfo_error(self, ctx, error):
        """Error handler for serverinfo command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("Sorry, only the bot owner can use this command.")
        else:
            logger.error(f"Error in serverinfo command: {error}")
            await ctx.send("An error occurred.")


# --- Setup Function ---
async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))

# No teardown needed for this simple cog unless resources were acquired
