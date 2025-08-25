import discord
from discord import app_commands, Embed, Color, ui

class PanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="Ultra Speaker Express", custom_id="ultra_speaker", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="Ultra Gramiel Express", custom_id="ultra_gramiel", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="4-Man Ultra Daily Express", custom_id="4man_ultra_daily", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="7-Man Ultra Daily Express", custom_id="7man_ultra_daily", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="Ultra Weekly Express", custom_id="ultra_weekly", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="Grim Express", custom_id="grim_express", style=discord.ButtonStyle.primary))
        self.add_item(ui.Button(label="Daily Temple Express", custom_id="daily_temple", style=discord.ButtonStyle.primary))

@app_commands.command(name="panel", description="Show the helper panel")
async def panel(interaction: discord.Interaction):
    embed = Embed(
        title="🎮 In-game Assistance",
        description=(
            "Select a service below to create a help ticket. Our helpers will assist you!\n\n"
            "### 📜 Guidelines & Rules: Use /hrules, /rrules, and /proof commands\n"
            "### 📋 Available Services\n"
            "- Ultra Speaker Express — 8 points\n"
            "- Ultra Gramiel Express — 7 points\n"
            "- 4-Man Ultra Daily Express — 4 points\n"
            "- 7-Man Ultra Daily Express — 7 points\n"
            "- Ultra Weekly Express — 12 points\n"
            "- Grim Express — 10 points\n"
            "- Daily Temple Express — 6 points\n"
            "### ℹ️ How it works\n"
            "1. Select a service\n"
            "2. Fill out the form\n"
            "3. Wait for helpers to join\n"
            "4. Get help in your private ticket!"
        ),
        color=Color.purple()
    )
    await interaction.response.send_message(embed=embed, view=PanelView(), ephemeral=True)

async def setup(bot):
    bot.tree.add_command(panel)