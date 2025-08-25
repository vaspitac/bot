import discord
from discord import app_commands, Embed, Color, ui

class SetupView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="Configure rrules", custom_id="setup_rrules", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="Configure hrules", custom_id="setup_hrules", style=discord.ButtonStyle.primary))
        # Add other config buttons as you need

@app_commands.command(name="setup", description="Configure server settings (admin)")
@app_commands.default_permissions(administrator=True)
async def setup_cmd(interaction: discord.Interaction):
    embed = Embed(
        title="⚙️ Server Setup",
        description="Use the buttons below to configure server settings and custom commands.",
        color=Color.green()
    )
    await interaction.response.send_message(embed=embed, view=SetupView(), ephemeral=True)

async def setup(bot):
    bot.tree.add_command(setup_cmd)