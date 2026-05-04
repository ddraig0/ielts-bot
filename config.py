import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE")

# Admin
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]

# Subscription
SUBSCRIPTION_PRICE = 15  # AZN per month
TRIAL_DAYS = 3

# Database
DB_PATH = "ielts_bot.db"
