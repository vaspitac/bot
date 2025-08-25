import discord
from discord.ext import commands
from database import DatabaseManager

db = DatabaseManager()

class PointsExtraCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="history")
    async def history_command(self, ctx, member: discord.Member = None):
        """Show a user's points history (current points as placeholder)"""
        member = member or ctx.author
        points = await db.get_user_points(ctx.guild.id, member.id)
        # TODO: Extend DB to track full history
        await ctx.send(f"📜 {member.display_name} has {points} points (history tracking not yet implemented).")

    @commands.command(name="pointsinfo")
    async def pointsinfo_command(self, ctx):
        """Explain the points system"""
        info = (
            "💠 **Points System Info** 💠\n"
            "- Users earn points for completing tasks.\n"
            "- Admins can add, remove, or set points.\n"
            "- Check your points with `!points`.\n"
            "- See top users with `!leaderboard` or `!lb`.\n"
            "- Reset the leaderboard with `!resetlb` (admin only).\n"
            "- Remove users from leaderboard with `!removeuser` (admin only)."
        )
        await ctx.send(info)

# -------------------- LOAD COG --------------------
def setup(bot):
    bot.add_cog(PointsExtraCog(bot))