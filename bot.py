# bot.py
import discord
from discord.ext import commands
import asyncio
import logging
import os
import config # Import your config

# --- Logging Setup ---
# Basic logging to console and a file
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]: %(message)s')
log_file_handler = logging.FileHandler('bot.log', encoding='utf-8', mode='w')
log_file_handler.setFormatter(log_formatter)
log_console_handler = logging.StreamHandler()
log_console_handler.setFormatter(log_formatter)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Set root level (e.g., INFO, DEBUG)
logger.addHandler(log_file_handler)
logger.addHandler(log_console_handler)

# Silence overly verbose libraries if needed
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('aiomysql').setLevel(logging.WARNING)

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True # Required for message content
# Add other intents like members if needed: intents.members = True

# Use Bot instead of commands.Bot for easier subclassing if needed later
bot = commands.Bot(command_prefix='.bot ', intents=intents, owner_id=config.OWNER_USER_ID)

# --- Cog Loading ---
INITIAL_EXTENSIONS = [
    'cogs.stalk_cog',
    'cogs.utility_cog',
    # Add other cogs here as 'cogs.cog_name'
]

@bot.event
async def on_ready():
    """Called when the bot is ready and connected."""
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds.')
    logger.info('------')
    # Set presence
    await bot.change_presence(activity=discord.Game(name=".bot info"))

@bot.event
async def setup_hook():
    """Asynchronous setup hook called before on_ready."""
    logger.info("Running setup_hook...")

    # Load extensions (Cogs)
    for extension in INITIAL_EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f'Successfully loaded extension: {extension}')
        except commands.ExtensionNotFound:
            logger.error(f'Extension not found: {extension}')
        except commands.ExtensionAlreadyLoaded:
            logger.warning(f'Extension already loaded: {extension}')
        except commands.NoEntryPointError:
            logger.error(f'Extension {extension} has no setup function.')
        except commands.ExtensionFailed as e:
            logger.exception(f'Extension {extension} failed to load: {e}')
            # Optionally, stop the bot if a critical cog fails
            # raise e

    logger.info("Setup_hook finished.")

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Global command error handler."""
    if isinstance(error, commands.CommandNotFound):
        # Optionally send a message or just ignore
        # await ctx.send("Unknown command. Use `.bot info` to see available commands.")
        pass # Ignore unknown commands silently
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`. Use `.bot info` for command usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad argument provided. Use `.bot info` for command usage.")
    elif isinstance(error, commands.CommandOnCooldown):
         await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.CheckFailure):
         # Handle permission errors, NotOwner, etc. Specific cogs might handle their own.
         await ctx.send("You do not have permission to use this command.")
    else:
        # Log other errors
        logger.exception(f"Unhandled command error in '{ctx.command}' invoked by {ctx.author}: {error}")
        # Optionally send a generic error message to the user
        await ctx.send("An unexpected error occurred while running the command.")


async def main():
    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested via KeyboardInterrupt.")
    except Exception as e:
         logger.exception(f"Critical error during bot execution: {e}")
    finally:
         # Ensure resources are cleaned up if asyncio.run exits unexpectedly
         # Note: Cog teardown functions handle most cleanup now
         logger.info("Bot process finished.")

