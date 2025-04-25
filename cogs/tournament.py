import discord
import random
import asyncio
from discord import app_commands
from discord.ext import commands
import math

# Import the database getter function
from cogs.settings import get_game_channel_db

import config


class Tournament(commands.Cog):
    """Cog for handling tournaments in QuickDraw Showdown."""
    
    def __init__(self, bot):
        self.bot = bot
        self.participants = {}  # Format: {guild_id: [user_id1, user_id2, ...]}
        self.active_tournaments = set()  # Set of guild IDs with active tournaments
        self.duel_outcomes = [
            "{loser} got distracted by a tumbleweed. {winner} wins!",
            "{loser} tried to draw but dropped their revolver!",
            "{winner} was faster than a rattlesnake. {loser} didn't stand a chance.",
            "{loser} sneezed at the wrong moment. {winner} takes the win!",
            "{winner} spun their revolver like a pro. {loser} was too intimidated to shoot straight.",
            "{loser} fumbled with their holster. {winner} didn't waste a second!",
            "{winner} squinted like Clint Eastwood. {loser} couldn't handle the pressure.",
            "A dust cloud blew into {loser}'s eyes! {winner} seized the opportunity!",
            "{loser} Pulled out a wand, what? {winner} remains cool as ice.",
            "{winner} shot with deadly precision. {loser} never saw it coming."
        ]
    
    async def update_stats(self, winner_id, loser_id):
        """Update player statistics after a duel. Used by the Duel cog as well."""
        # Import here to avoid circular imports
        from cogs.duel import Duel
        duel_cog = self.bot.get_cog('Duel')
        if duel_cog:
            await duel_cog.update_stats(winner_id, loser_id)
    
    @app_commands.command(name="join_tournament", description="Join the next tournament")
    async def join_tournament(self, interaction: discord.Interaction):
        """Join the upcoming tournament in this server."""
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

        user_id = interaction.user.id
        
        # Initialize guild in participants dict if not present
        if guild_id not in self.participants:
            self.participants[guild_id] = []
        
        # Check if tournament is already active
        if guild_id in self.active_tournaments:
            await interaction.response.send_message(
                "A tournament is already in progress! Wait for the next one.", 
                ephemeral=True
            )
            return
        
        # Check if user is already in the tournament
        if user_id in self.participants[guild_id]:
            await interaction.response.send_message(
                "You're already registered for the tournament!", 
                ephemeral=True
            )
            return
        
        # Add user to tournament
        self.participants[guild_id].append(user_id)
        count = len(self.participants[guild_id])
        
        await interaction.response.send_message(
            f"🎯 {interaction.user.display_name} has joined the tournament! ({count} participant{'s' if count != 1 else ''})"
        )
    
    @app_commands.command(name="start_tournament", description="Start the tournament with registered players")
    @app_commands.default_permissions(administrator=True)
    async def start_tournament(self, interaction: discord.Interaction):
        """Start a tournament with all registered players."""
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

        # guild_id already defined above
        # Check if enough participants
        if guild_id not in self.participants or len(self.participants[guild_id]) < 2:
            await interaction.response.send_message(
                "Not enough participants! At least 2 players are needed.", 
                ephemeral=True
            )
            return
        
        # Mark tournament as active
        self.active_tournaments.add(guild_id)
        
        # Get participants
        participant_ids = self.participants[guild_id].copy()
        random.shuffle(participant_ids)  # Randomize bracket order
        
        # Create initial embed with participants
        embed = discord.Embed(
            title="🏆 QuickDraw Tournament",
            description="The tournament is about to begin!",
            color=discord.Color.gold()
        )
        
        participants_str = ""
        for i, pid in enumerate(participant_ids, 1):
            member = interaction.guild.get_member(pid)
            name = member.display_name if member else f"Unknown Gunslinger ({pid})"
            participants_str += f"{i}. {name}\n"
        
        embed.add_field(name="Participants", value=participants_str)
        
        # Calculate number of rounds needed
        num_participants = len(participant_ids)
        num_rounds = math.ceil(math.log2(num_participants))
        
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(2)
        
        # Run the tournament
        await self.run_tournament(interaction.channel, participant_ids, num_rounds)
        
        # Clear participant list and mark tournament as inactive
        self.participants[guild_id] = []
        self.active_tournaments.remove(guild_id)
    
    async def run_tournament(self, channel, participants, num_rounds):
        """Run the tournament with the given participants."""
        round_num = 1
        current_round_participants = participants
        
        # Add byes if needed to make the number of participants a power of 2
        target_count = 2 ** num_rounds
        while len(current_round_participants) < target_count:
            current_round_participants.append(None)  # None represents a "bye"
        
        # Run each round
        while round_num <= num_rounds:
            await channel.send(f"## Round {round_num}")
            await asyncio.sleep(1)
            
            next_round_participants = []
            matches = []
            
            # Create matches for this round
            for i in range(0, len(current_round_participants), 2):
                if i+1 < len(current_round_participants):
                    matches.append((current_round_participants[i], current_round_participants[i+1]))
            
            # Run each match
            for match_num, (player1_id, player2_id) in enumerate(matches, 1):
                # Handle byes
                if player1_id is None:
                    next_round_participants.append(player2_id)
                    continue
                if player2_id is None:
                    next_round_participants.append(player1_id)
                    continue
                
                # Get player objects
                player1 = channel.guild.get_member(player1_id)
                player2 = channel.guild.get_member(player2_id)
                
                player1_name = player1.display_name if player1 else f"Unknown ({player1_id})"
                player2_name = player2.display_name if player2 else f"Unknown ({player2_id})"
                
                # Announce match
                await channel.send(f"### Match {match_num}: {player1_name} vs {player2_name}")
                await asyncio.sleep(1.5)
                
                # Countdown
                countdown_msg = await channel.send("Get ready...")
                for i in range(3, 0, -1):
                    await countdown_msg.edit(content=f"Get ready... {i}")
                    await asyncio.sleep(1)
                
                await countdown_msg.edit(content="**DRAW!** 🔫")
                await asyncio.sleep(1.5)
                
                # Determine winner (random for now)
                if random.random() < 0.5:
                    winner, loser = player1, player2
                    winner_id, loser_id = player1_id, player2_id
                else:
                    winner, loser = player2, player1
                    winner_id, loser_id = player2_id, player1_id
                
                # Get a random outcome message
                outcome = random.choice(self.duel_outcomes)
                winner_name = winner.display_name if winner else f"Unknown ({winner_id})"
                loser_name = loser.display_name if loser else f"Unknown ({loser_id})"
                outcome = outcome.format(winner=winner_name, loser=loser_name)
                
                # Send the result
                await channel.send(f"💥 {outcome}")
                await channel.send(f"🏆 {winner_name} advances to the next round!")
                
                # Update stats
                await self.update_stats(winner_id, loser_id)
                
                # Add winner to next round
                next_round_participants.append(winner_id)
                
                # Pause between matches
                await asyncio.sleep(2)
            
            # Update for next round
            current_round_participants = next_round_participants
            round_num += 1
            
            # If we have a winner, end the tournament
            if len(current_round_participants) == 1:
                winner_id = current_round_participants[0]
                winner = channel.guild.get_member(winner_id)
                winner_name = winner.display_name if winner else f"Unknown ({winner_id})"
                
                # Create winner embed
                embed = discord.Embed(
                    title="🏆 Tournament Champion 🏆",
                    description=f"**{winner_name}** is the fastest gunslinger in the West!",
                    color=discord.Color.gold()
                )
                
                if winner and winner.avatar:
                    embed.set_thumbnail(url=winner.avatar.url)
                
                await channel.send(embed=embed)
                break


async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Tournament(bot)) 