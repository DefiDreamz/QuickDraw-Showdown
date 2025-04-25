import discord
import json
import random
import asyncio
from discord import app_commands
from discord.ext import commands

# Import the database getter function
from cogs.settings import get_game_channel_db

import config


class Duel(commands.Cog):
    """Cog for handling duels between players in QuickDraw Showdown."""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_duels = {}  # Format: {challenger_id: (target_id, channel_id)}
        self.duel_outcomes = [
            "{loser} got distracted by a tumbleweed. {winner} wins!",
            "{loser} tried to draw but dropped their revolver!",
            "{winner} was faster than a rattlesnake. {loser} didn't stand a chance.",
            "{loser} sneezed at the wrong moment. {winner} takes the win!",
            "{winner} spun their revolver like a pro. {loser} was too intimidated to shoot straight.",
            "{loser} fumbled with their holster. {winner} didn't waste a second!",
            "{winner} squinted like Clint Eastwood. {loser} couldn't handle the pressure.",
            "A dust cloud blew into {loser}'s eyes! {winner} seized the opportunity!",
            "{loser} got spooked by their own shadow. {winner} remains cool as ice.",
            "{winner} shot with deadly precision. {loser} never saw it coming."
        ]
    
    async def update_stats(self, winner_id, loser_id):
        """Update player statistics after a duel."""
        try:
            # Read current stats
            with open(config.DATA_FILE, 'r') as f:
                stats = json.load(f)
            
            # Initialize player entries if they don't exist
            for player_id in (winner_id, loser_id):
                if str(player_id) not in stats:
                    stats[str(player_id)] = {
                        'wins': 0,
                        'losses': 0,
                        'duels': 0
                    }
            
            # Update stats
            stats[str(winner_id)]['wins'] += 1
            stats[str(winner_id)]['duels'] += 1
            stats[str(loser_id)]['losses'] += 1
            stats[str(loser_id)]['duels'] += 1
            
            # Write updated stats
            with open(config.DATA_FILE, 'w') as f:
                json.dump(stats, f, indent=4)
                
        except Exception as e:
            # Log the error but don't crash
            print(f"Error updating stats: {e}")
    
    @app_commands.command(name="duel", description="Challenge another player to a QuickDraw duel!")
    @app_commands.describe(target="The player you want to challenge")
    async def duel_command(self, interaction: discord.Interaction, target: discord.Member):
        """Challenge another player to a QuickDraw duel."""
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

        challenger = interaction.user
        
        # Check if target is valid (not self, not a bot)
        if target.id == challenger.id:
            await interaction.response.send_message("You can't duel yourself, partner! Find another gunslinger.", ephemeral=True)
            return
        
        if target.bot:
            await interaction.response.send_message("You can't duel a bot! They're too fast for you.", ephemeral=True)
            return
        
        # Check if challenger is already in a duel
        if challenger.id in self.active_duels:
            await interaction.response.send_message("You're already in a duel! Finish that one first.", ephemeral=True)
            return
        
        # Check if target is already in a duel
        for (_, target_info) in self.active_duels.values():
            if target.id == target_info:
                await interaction.response.send_message(f"{target.display_name} is already in a duel! Wait your turn.", ephemeral=True)
                return
        
        # Create a new duel
        self.active_duels[challenger.id] = (target.id, interaction.channel_id)
        
        await interaction.response.send_message(
            f"🤠 {challenger.mention} has challenged {target.mention} to a QuickDraw duel!\n"
            f"{target.mention}, type `/accept` to accept the challenge!"
        )
    
    @app_commands.command(name="accept", description="Accept a duel challenge")
    async def accept_command(self, interaction: discord.Interaction):
        """Accept a pending duel challenge."""
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

        target = interaction.user
        
        # Find if there's a duel waiting for this user to accept
        challenger_id = None
        for c_id, (t_id, channel_id) in self.active_duels.items():
            if t_id == target.id and channel_id == interaction.channel_id:
                challenger_id = c_id
                break
        
        if challenger_id is None:
            await interaction.response.send_message("There's no duel waiting for you to accept in this channel!", ephemeral=True)
            return
        
        # Get challenger object
        challenger = interaction.guild.get_member(challenger_id)
        if not challenger:
            await interaction.response.send_message("The challenger seems to have left the server! Duel cancelled.", ephemeral=True)
            self.active_duels.pop(challenger_id, None)
            return
        
        # Duel accepted, start the countdown
        await interaction.response.send_message(f"🔫 {target.mention} has accepted {challenger.mention}'s challenge! The duel will begin shortly...")
        
        # Remove the duel from active duels
        self.active_duels.pop(challenger_id, None)
        
        # Countdown
        countdown_msg = await interaction.channel.send("Get ready...")
        for i in range(3, 0, -1):
            await countdown_msg.edit(content=f"Get ready... {i}")
            await asyncio.sleep(1)
        
        await countdown_msg.edit(content="**DRAW!** 🔫")
        await asyncio.sleep(1.5)
        
        # Determine winner (random for now)
        if random.random() < 0.5:
            winner, loser = challenger, target
        else:
            winner, loser = target, challenger
        
        # Get a random outcome message
        outcome = random.choice(self.duel_outcomes)
        outcome = outcome.format(winner=winner.display_name, loser=loser.display_name)
        
        # Send the result
        await interaction.channel.send(f"💥 {outcome}")
        await interaction.channel.send(f"🏆 {winner.mention} wins the duel against {loser.mention}!")
        
        # Update stats
        await self.update_stats(winner.id, loser.id)


async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Duel(bot)) 