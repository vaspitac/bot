# modules/setup/setup_commands.py
import discord
from discord.ext import commands
from discord import Embed
from discord.ui import View, Button
from .setup_roles_channels import RoleChannelModal
from database import DatabaseManager

db = DatabaseManager()

class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Set Roles/Channels", style=discord.ButtonStyle.primary, custom_id="set_roles_channels"))
        self.add_item(Button(label="Reset Setup", style=discord.ButtonStyle.danger, custom_id="reset_setup"))

    @discord.ui.button(label="Set Roles/Channels", style=discord.ButtonStyle.primary, custom_id="set_roles_channels")
    async def set_roles_channels(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleChannelModal())

    @discord.ui.button(label="Reset Setup", style=discord.ButtonStyle.danger, custom_id="reset_setup")
    async def reset_setup(self, button: Button, interaction: discord.Interaction):
        await db.update_server_config(interaction.guild.id,
                                      admin_role_id=None,
                                      staff_role_id=None,
                                      helper_role_id=None,
                                      viewer_role_id=None,
                                      blocked_role_id=None,
                                      reward_role_id=None,
                                      ticket_category_id=None,
                                      transcript_channel_id=None)
        await interaction.response.send_message("⚠️ Setup has been reset!", ephemeral=True)

class SetupCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        embed = Embed(
            title="Bot Setup",
            description="Use the buttons below to set roles/channels or reset setup.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=SetupView())

def setup(bot):
    bot.add_cog(SetupCommandsCog(bot))
