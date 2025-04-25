# cogs/settings.py
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import logging
import os # Import os

logger = logging.getLogger(__name__)
DATABASE_FILE = 'data/settings.db' # Define database file path

# --- Database Helper Functions ---

def set_game_channel_db(guild_id: int, channel_id: int | None):
    """Sets or clears the game channel ID for a specific guild."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO guild_settings (guild_id, game_channel_id)
            VALUES (?, ?)
        ''', (guild_id, channel_id))
        conn.commit()
        conn.close()
        logger.info(f"Set game channel for guild {guild_id} to {channel_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error setting game channel for guild {guild_id}: {e}", exc_info=True)
        return False

def get_game_channel_db(guild_id: int) -> int | None:
    """Gets the configured game channel ID for a specific guild."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT game_channel_id FROM guild_settings WHERE guild_id = ?
        ''', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        if result and result[0] is not None:
            logger.debug(f"Retrieved game channel {result[0]} for guild {guild_id}")
            return result[0]
        else:
            logger.debug(f"No specific game channel configured for guild {guild_id}")
            return None
    except sqlite3.Error as e:
        logger.error(f"Error getting game channel for guild {guild_id}: {e}", exc_info=True)
        return None

# --- End Database Helper Functions ---


class Settings(commands.Cog):
    """Cog for managing bot settings per server."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_game_channel", description="Sets the channel where game commands are allowed.")
    @app_commands.describe(channel="The text channel to restrict game commands to (leave blank to allow everywhere).")
    @app_commands.default_permissions(administrator=True) # Only admins can use this
    async def set_game_channel_command(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Sets the channel for game commands."""
        guild_id = interaction.guild_id
        channel_id = channel.id if channel else None

        # Attempt to update the database
        # Using run_in_executor to avoid blocking the event loop with DB operations
        success = await self.bot.loop.run_in_executor(
            None, set_game_channel_db, guild_id, channel_id
        )

        if success:
            if channel:
                await interaction.response.send_message(
                    f"✅ Game commands are now restricted to {channel.mention}.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "✅ Game commands are now allowed in any channel.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Failed to update the game channel setting due to a database error.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Settings(bot)) 