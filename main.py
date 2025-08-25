import discord
from discord.ext import commands
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
# Main async entry point
# ------------------------
async def main():
    # Load ticket system (ensure this is async-safe if needed)
    setup_ticket_commands(bot)

    # Load points modules
    await bot.load_extension("modules.points.commands")
    await bot.load_extension("modules.points.points_extra")
    await bot.load_extension("modules.points.custom_commands")

    # Load setup modules
    await bot.load_extension("modules.setup.setup_commands")
    await bot.load_extension("modules.setup.setup_custom_commands")
    await bot.load_extension("modules.setup.setup_reset")
    await bot.load_extension("modules.setup.setup_roles_channels")

    # Start web server asynchronously
    asyncio.create_task(asyncio.to_thread(start_server))

    # Run the bot
    await bot.start(TOKEN)

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    asyncio.run(main())
