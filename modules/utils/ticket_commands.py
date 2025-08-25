import discord
from discord.ext import commands
from modules.utils.helpers import get_admin_roles  # make sure this points to your helper functions

class HelpCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Show available commands"""
        admin_roles = await get_admin_roles(ctx.guild.id) or []
        is_admin = any(r.id in admin_roles for r in ctx.author.roles)

        embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blue())

        # General commands
        embed.add_field(
            name="📋 General Commands",
            value=(
                "`!help` - Show this help message\n"
                "`!points [user]` - Check points for yourself or another user\n"
                "`!leaderboard` - Show server points leaderboard\n"
                "`!rrules` - Show runner rules\n"
                "`!hrules` - Show helper rules\n"
                "`!proof` - Show proof submission instructions"
            ),
            inline=False
        )

        # Ticket commands
        embed.add_field(
            name="🎫 Ticket Commands",
            value=(
                "Use the ticket panel to create tickets\n"
                "`!removehelper @user` - Remove a helper from current ticket (Admin only)"
            ),
            inline=False
        )

        if is_admin or ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="⚙️ Admin Commands",
                value=(
                    "`!setup` - Interactive bot configuration\n"
                    "`!create` - Create ticket selection panel\n"
                    "`!delete <message_id>` - Delete bot message panel\n"
                    "`!add @user <points>` - Add points to user\n"
                    "`!remove @user <points>` - Remove points from user\n"
                    "`!setpoints @user <points>` - Set user's points\n"
                    "`!restartleaderboard` - Reset all points\n"
                    "`!setupreset` - Reset all bot configuration\n"
                    "And various reset commands for specific settings"
                ),
                inline=False
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCommandCog(bot))
