import os

# Discord Bot Token - Replace with your actual token
# Make sure to set this via environment variable or other secure means
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Admin Role IDs or User IDs who can start tournaments
ADMIN_IDS = [1087826581285769217] # User ID added

# Command Prefix (if not using slash commands exclusively)
COMMAND_PREFIX = '/'

# Data file path
DATA_FILE = 'data/stats.json'

# Channel ID where the game is allowed to be played (replace with your channel ID)
GAME_CHANNEL_ID = 1363245000972046367 # Set this to your channel ID, e.g., 123456789012345678
