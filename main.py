import discord
from discord.ext import commands
import asyncio
import logging
from config import TOKEN  # Uses TOKEN from config.py
from database import DatabaseManager
from webserver import start_webserver

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database manager
db = DatabaseManager()

class TicketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        super().__init__(
            command_prefix='/',  # Use slash for consistency with slash commands
            intents=intents,
            help_command=None
        )
        self.db = db  # Make database accessible to cogs

    async def setup_hook(self):
        """Load all cogs when the bot starts"""
        try:
            # Load Points System
            await self.load_extension("modules.points.commands")
            logger.info("✅ Points commands loaded")
            # Remove legacy/extra/custom modules if not using them
            # await self.load_extension("modules.points.custom_commands")
            # await self.load_extension("modules.points.points_extra")
            
            # Load Setup System
            await self.load_extension("modules.setup.setup_command")
            logger.info("✅ Setup commands loaded")
            # await self.load_extension("modules.setup.setup_custom_commands")
            # await self.load_extension("modules.setup.setup_reset")
            
            # Load Ticket System
            await self.load_extension("modules.tickets.panel_command")
            logger.info("✅ Ticket panel loaded")
            # await self.load_extension("modules.tickets.ticket_commands")  # Only if you have this
            
            # Load Help System
            await self.load_extension("modules.utils.help_commands")
            logger.info("✅ Help commands loaded")
            
            logger.info("🎉 All modules loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Error loading modules: {e}")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"🚀 Logged in as {self.user} (ID: {self.user.id})")
        # Initialize database
        await db.initialize_database()
        logger.info("✅ Database initialized")
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")
        logger.info("🎫 Bot is ready! Ticket system online.")

# Create bot instance
bot = TicketBot()

# Start webserver in background
start_webserver()

# Run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)  # Uses TOKEN from config.py

if __name__ == "__main__":
    asyncio.run(main())