import os

# Discord Bot Token - Replace with your actual token
# Make sure to set this via environment variable or other secure means
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Admin Role IDs or User IDs who can start tournaments
ADMIN_IDS = [1087826581285769217] # User ID added

# Command Prefix (if not using slash commands exclusively)
COMMAND_PREFIX = '/'

# Data file path
DATA_FILE = 'data/stats.json'

# GAME_CHANNEL_ID removed - settings are now per-guild in database
