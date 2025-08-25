import discord
from discord.ext import commands
import threading
import asyncio
import logging
import sys
import os

# Fix module imports for Render
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ------------------------
# Config & webserver
# ------------------------
from config import TOKEN
from webserver import start_server

# ------------------------
# Database
# ------------------------
from database import DatabaseManager
db = DatabaseManager()

# ------------------------
# Ticket system
# ------------------------
from modules.tickets.ticket_commands import setup_ticket_commands

# Optional placeholders to avoid import errors (safe for Render)
try:
    from modules.tickets.ticket_modal import *
except ImportError:
    pass

try:
    from modules.tickets.ticket_views import *
except ImportError:
    pass

try:
    from modules.tickets.transcript import *
except ImportError:
    pass

# ------------------------
# Logging
# ------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# ------------------------
# Bot setup
# ------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# Bot events
# ------------------------
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await db.initialize_database()
    logger.info("Database initialized.")

# ------------------------
# Load ticket system
# ------------------------
setup_ticket_commands(bot)

# ------------------------
# Load points modules
# ------------------------
bot.load_extension("modules.points.commands")
bot.load_extension("modules.points.points_extra")
bot.load_extension("modules.points.custom_commands")

# ------------------------
# Load setup modules
# ------------------------
bot.load_extension("modules.setup.setup_commands")
bot.load_extension("modules.setup.setup_custom_commands")
bot.load_extension("modules.setup.setup_reset")
bot.load_extension("modules.setup.setup_roles_channels")

# ------------------------
# Start web server
# ------------------------
def start_web_server():
    try:
        start_server()
    except Exception as e:
        logger.error(f"Error starting web server: {e}")

bot.loop.create_task(asyncio.to_thread(start_web_server))

# ------------------------
# Run the bot
# ------------------------
if __name__ == "__main__":
    bot.run(TOKEN)
