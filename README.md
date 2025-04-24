# QuickDraw Showdown Discord Bot

A fun cowboy-themed dueling bot for Discord servers.

## Features

- Challenge other server members to quick-draw duels
- Join and participate in tournaments 
- Track your stats and climb the leaderboard
- Earn titles based on your performance

## Commands

- `/duel @user` - Challenge another user to a quick-draw duel
- `/accept` - Accept a duel challenge
- `/join_tournament` - Join the next tournament
- `/start_tournament` - (Admin only) Start a tournament with all registered players
- `/stats [@user]` - Check your dueling stats (or another player's)
- `/leaderboard` - View the top duelists on the server

## Setup Instructions

1. **Prerequisites**
   - Python 3.8 or higher
   - A Discord Bot Token (obtainable from [Discord Developer Portal](https://discord.com/developers/applications))

2. **Installation**
   ```bash
   # Clone the repository (or download the code)
   git clone https://github.com/yourusername/quickdraw-bot.git
   cd quickdraw-bot
   
   # Create and activate a virtual environment
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Open `config.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual Discord bot token
   - (Optional) Add your Discord User ID to the `ADMIN_IDS` list for testing admin commands

4. **Running the Bot**
   ```bash
   python bot.py
   ```

5. **Inviting the Bot to Your Server**
   - Create a bot invite link from the Discord Developer Portal
   - Ensure you grant the bot the `bot` and `applications.commands` scopes
   - Required permissions: Send Messages, Embed Links, Read Message History, and Use Slash Commands

## Bot Permissions

Make sure the bot has the following permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Application Commands

## License

This project is licensed under the MIT License - see the LICENSE file for details. 