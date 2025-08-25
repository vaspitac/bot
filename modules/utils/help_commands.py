import discord
from discord import app_commands, Embed
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all bot commands and help")
    async def help(self, interaction: discord.Interaction):
        embed = Embed(
            title="✨ Bot Commands & Help",
            description="Welcome! Here are all the commands you can use.",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="🎟️ Ticket Commands",
            value=(
                "`/panel` — Create ticket panel (admin, staff)\n"
                "`/removehelper @user` — Remove helper from ticket (admin, staff)"
            ),
            inline=False
        )
        embed.add_field(
            name="📈 Points & Leaderboard",
            value=(
                "`/leaderboard` — View top helpers\n"
                "`/points [@user]` — See someone's points\n"
                "`/myrank` — See your leaderboard rank\n"
                "`/addpoints @user amount` — Add points (admin/staff)\n"
                "`/removepoints @user amount` — Remove points (admin/staff)\n"
                "`/setpoints @user amount` — Set points (admin/staff)\n"
                "`/removeuser @user` — Remove user from leaderboard (admin/staff)\n"
                "`/resetlb` — Reset entire leaderboard (admin)"
            ),
            inline=False
        )
        embed.add_field(
            name="📜 Rules & Setup",
            value=(
                "`/hrules` — Helper guidelines\n"
                "`/rrules` — Requester guidelines\n"
                "`/proof` — Proof requirements\n"
                "`/setup` — Configure server settings (admin)"
            ),
            inline=False
        )
        embed.set_footer(text="Need more help? Contact a member of the staff team!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))