# modules/setup/setup_custom_commands.py
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
from discord import Interaction
from database import DatabaseManager

db = DatabaseManager()

class CustomCommandModal(Modal):
    def __init__(self, command_name: str, existing_content: str = "", existing_image: str = ""):
        super().__init__(title=f"Setup {command_name} Command")
        self.command_name = command_name

        self.content_input = TextInput(label="Command Content", placeholder="Enter content...", default=existing_content, style=discord.TextStyle.long, max_length=2000)
        self.add_item(self.content_input)

        if command_name == "proof":
            self.image_input = TextInput(label="Image URL (Optional)", placeholder="Image URL", default=existing_image, required=False)
            self.add_item(self.image_input)

    async def on_submit(self, interaction: Interaction):
        content = self.content_input.value
        image_url = getattr(self, 'image_input', None)
        image_url = image_url.value if image_url else ""
        await db.set_custom_command(interaction.guild.id, self.command_name, content, image_url)
        await interaction.response.send_message(f"✅ Custom command `!{self.command_name}` configured!", ephemeral=True)

class SetupCustomCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setupcommand")
    @commands.has_permissions(administrator=True)
    async def setupcommand(self, ctx, command_name: str):
        if command_name not in ["rrules", "hrules", "proof"]:
            await ctx.send("❌ Invalid command name. Use rrules, hrules, or proof.")
            return
        await ctx.send_modal(CustomCommandModal(command_name))

def setup(bot):
    bot.add_cog(SetupCustomCommandsCog(bot))
