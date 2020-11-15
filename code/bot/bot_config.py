from code.config import DATA_DIR

# The bot TOKEN
# This value will be taken into account if the -t argument is not passed to the main script
# Note that if this TOKEN is empty and the -t argument is not passed, it will not boot up
TOKEN = ""

# Enter the admins Telegram ID in this array
ADMIN = []

# Sleep time for the main Thread of the bot (in seconds)
SLEEP_TIME = 30

# Bot config save file for persistence
BOT_CONFIG_FILE = f"{DATA_DIR}/bot_settings.json"
