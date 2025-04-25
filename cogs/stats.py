import discord
import json
from discord import app_commands
from discord.ext import commands

# Import the database getter function
from cogs.settings import get_game_channel_db

import config


class Stats(commands.Cog):
    """Cog for tracking and displaying player statistics in QuickDraw Showdown."""
    
    def __init__(self, bot):
        self.bot = bot
        self.titles = {
            0: 'Newcomer',
            3: 'Greenhorn',
            5: 'Deputy',
            10: 'Sheriff',
            15: 'Gunslinger',
            20: 'Desperado',
            30: 'Outlaw',
            40: 'Legend of the West'
        }
    
    def get_title(self, wins):
        """Get a player's title based on their win count."""
        title = 'Newcomer'  # Default title
        for win_threshold, new_title in sorted(self.titles.items()):
            if wins >= win_threshold:
                title = new_title
            else:
                break
        return title
    
    def load_stats(self):
        """Load player statistics from the data file."""
        try:
            with open(config.DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, return empty dict
            return {}
    
    @app_commands.command(name="stats", description="Show your or another player's duel statistics")
    @app_commands.describe(player="The player whose stats you want to see (leave empty for your own stats)")
    async def stats_command(self, interaction: discord.Interaction, player: discord.Member = None):
        """Display duel statistics for yourself or another player."""
        # NEW CHECK:
        guild_id = interaction.guild_id
        allowed_channel_id = await self.bot.loop.run_in_executor(
            None, get_game_channel_db, guild_id
        )
        if allowed_channel_id is not None and interaction.channel_id != allowed_channel_id:
            await interaction.response.send_message(
                f"This command can only be used in <#{allowed_channel_id}>!",
                ephemeral=True
            )
            return

        # If no player specified, show stats for the command user
        if player is None:
            player = interaction.user
        
        # Load stats data
        stats = self.load_stats()
        player_id = str(player.id)
        
        # Check if player has stats
        if player_id not in stats:
            await interaction.response.send_message(
                f"{player.display_name} hasn't participated in any duels yet!", 
                ephemeral=True
            )
            return
        
        # Get player stats
        player_stats = stats[player_id]
        wins = player_stats.get('wins', 0)
        losses = player_stats.get('losses', 0)
        duels = player_stats.get('duels', 0)
        win_rate = (wins / duels * 100) if duels > 0 else 0
        title = self.get_title(wins)
        
        # Create embed
        embed = discord.Embed(
            title=f"🤠 {player.display_name}'s Dueling Stats",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Title", value=f"**{title}**", inline=False)
        embed.add_field(name="Wins", value=str(wins), inline=True)
        embed.add_field(name="Losses", value=str(losses), inline=True)
        embed.add_field(name="Total Duels", value=str(duels), inline=True)
        embed.add_field(name="Win Rate", value=f"{win_rate:.1f}%", inline=True)
        
        # Set thumbnail to player's avatar if available
        if player.avatar:
            embed.set_thumbnail(url=player.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Show the top duelists")
    async def leaderboard_command(self, interaction: discord.Interaction):
        """Display the top players ranked by wins."""
        # NEW CHECK:
        guild_id = interaction.guild_id
        allowed_channel_id = await self.bot.loop.run_in_executor(
            None, get_game_channel_db, guild_id
        )
        if allowed_channel_id is not None and interaction.channel_id != allowed_channel_id:
            await interaction.response.send_message(
                f"This command can only be used in <#{allowed_channel_id}>!",
                ephemeral=True
            )
            return

        # Load stats data
        stats = self.load_stats()
        
        if not stats:
            await interaction.response.send_message("No duels have been recorded yet!", ephemeral=True)
            return
        
        # Sort players by wins
        sorted_players = sorted(
            stats.items(),
            key=lambda x: (x[1].get('wins', 0), -x[1].get('losses', 0)),
            reverse=True
        )
        
        # Take top 10 players
        top_players = sorted_players[:10]
        
        # Create embed
        embed = discord.Embed(
            title="🏆 QuickDraw Showdown Leaderboard",
            description="The fastest gunslingers in the West!",
            color=discord.Color.gold()
        )
        
        # Add fields for each top player
        for index, (player_id, player_stats) in enumerate(top_players, 1):
            # Try to get member info (they might have left the server)
            try:
                member = await interaction.guild.fetch_member(int(player_id))
                name = member.display_name
            except (discord.NotFound, discord.HTTPException):
                name = f"Unknown Gunslinger ({player_id})"
            
            wins = player_stats.get('wins', 0)
            losses = player_stats.get('losses', 0)
            title = self.get_title(wins)
            
            embed.add_field(
                name=f"{index}. {name}",
                value=f"**{title}**\nWins: {wins} | Losses: {losses}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Stats(bot)) 