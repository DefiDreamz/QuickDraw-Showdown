import discord
import os
import asyncio
import logging
import sqlite3
from discord.ext import commands
from aiohttp import web
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('discord')

# --- Web Server Setup ---
async def health_check(request):
    return web.Response(text="Bot is running")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")

# --- Database Setup ---
DATABASE_FILE = 'data/settings.db'

def initialize_database():
    """Initializes the settings database and creates the settings table if it doesn't exist."""
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                game_channel_id INTEGER DEFAULT NULL
            )
        ''')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized successfully at {DATABASE_FILE}")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred during database initialization: {e}", exc_info=True)

# --- End Database Setup ---

# Define necessary intents
intents = discord.Intents.default()
intents.message_content = True # If using message commands
intents.members = True # To access member information

class QuickDrawBot(commands.Bot):
    """Main bot class for QuickDraw Showdown."""
    def __init__(self):
        super().__init__(command_prefix=config.COMMAND_PREFIX, intents=intents)

    async def setup_hook(self):
        """Loads cogs automatically when the bot starts."""
        # Initialize database first
        initialize_database()

        logger.info(f'Loading cogs...')
        cogs_loaded = 0
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('_'):
                cog_name = f'cogs.{filename[:-3]}'
                try:
                    await self.load_extension(cog_name)
                    logger.info(f'Successfully loaded cog: {cog_name}')
                    cogs_loaded += 1
                except Exception as e:
                    logger.error(f'Failed to load cog {cog_name}: {e}', exc_info=True)
        logger.info(f'Loaded {cogs_loaded} cogs.')

        # Sync slash commands if needed (usually good practice on startup)
        # Note: Syncing globally can take time. For testing, sync to specific guilds.
        # await self.tree.sync() # Sync globally

        # Sync to a specific guild for testing (faster)
        # Replace YOUR_TEST_GUILD_ID with your test guild ID
        try:
            guild_id = 1363216998879723590 # <--- SERVER ID INSERTED
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild) # Copy global commands to guild
            await self.tree.sync(guild=guild)
            logger.info(f'Synced slash commands to guild {guild_id}.')
        except Exception as e:
            logger.error(f'Failed to sync commands to guild: {e}')

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')
        await self.change_presence(activity=discord.Game(name="QuickDraw Showdown"))


async def main():
    """Initializes and runs the bot."""
    bot = QuickDrawBot()
    
    # Start web server
    await run_web_server()
    
    try:
        await bot.start(config.BOT_TOKEN)
    except discord.LoginFailure:
        logger.error('Invalid Discord token. Please check your config.py file.')
    except Exception as e:
        logger.error(f'Error running bot: {e}', exc_info=True)


if __name__ == '__main__':
    asyncio.run(main()) 