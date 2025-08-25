import discord
from discord.ext import commands
from discord import ui
from database import DatabaseManager

db = DatabaseManager()

class PointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="points")
    async def points_command(self, ctx, member: discord.Member = None):
        """Check points for yourself or another user"""
        member = member or ctx.author
        points = await db.get_user_points(ctx.guild.id, member.id)
        await ctx.send(f"💰 {member.display_name} has {points} points.")

    @commands.command(name="addpoints")
    @commands.has_permissions(administrator=True)
    async def addpoints_command(self, ctx, member: discord.Member, amount: int):
        """Add points to a user (admin only)"""
        await db.add_user_points(ctx.guild.id, member.id, amount)
        await ctx.send(f"✅ Added {amount} points to {member.display_name}.")

    @commands.command(name="removepoints")
    @commands.has_permissions(administrator=True)
    async def removepoints_command(self, ctx, member: discord.Member, amount: int):
        """Remove points from a user (admin only)"""
        current = await db.get_user_points(ctx.guild.id, member.id)
        new_total = max(current - amount, 0)
        await db.set_user_points(ctx.guild.id, member.id, new_total)
        await ctx.send(f"✅ Removed {amount} points from {member.display_name}. New total: {new_total}")

    @commands.command(name="setpoints")
    @commands.has_permissions(administrator=True)
    async def setpoints_command(self, ctx, member: discord.Member, amount: int):
        """Set points for a user (admin only)"""
        await db.set_user_points(ctx.guild.id, member.id, amount)
        await ctx.send(f"✅ Set {member.display_name}'s points to {amount}.")

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard_command(self, ctx):
        """Show the top 10 users on the leaderboard"""
        all_points = await db.get_all_user_points(ctx.guild.id)
        if not all_points:
            await ctx.send("No points recorded yet.")
            return

        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        leaderboard = ""
        for i, (user_id, points) in enumerate(sorted_points[:10], start=1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"User ID {user_id}"
            leaderboard += f"{i}. {name} — {points} points\n"

        await ctx.send(f"🏆 **Leaderboard** 🏆\n{leaderboard}")

    @commands.command(name="myrank")
    async def myrank_command(self, ctx):
        """Show your current rank in the leaderboard"""
        all_points = await db.get_all_user_points(ctx.guild.id)
        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        for i, (user_id, points) in enumerate(sorted_points, start=1):
            if user_id == ctx.author.id:
                await ctx.send(f"📊 {ctx.author.display_name}, your rank is #{i} with {points} points.")
                return
        await ctx.send(f"📊 {ctx.author.display_name}, you have 0 points and are not on the leaderboard.")

    @commands.command(name="resetlb")
    @commands.has_permissions(administrator=True)
    async def resetlb_command(self, ctx):
        """Reset the leaderboard with confirmation button"""

        class Confirm(ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
            async def confirm(self, interaction: discord.Interaction, button: ui.Button):
                await db.clear_all_points(ctx.guild.id)
                await interaction.response.edit_message(content="✅ Leaderboard has been reset!", view=None)
                self.value = True
                self.stop()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction: discord.Interaction, button: ui.Button):
                await interaction.response.edit_message(content="❌ Leaderboard reset cancelled.", view=None)
                self.value = False
                self.stop()

        await ctx.send("⚠️ Are you sure you want to reset the leaderboard?", view=Confirm())

    @commands.command(name="removeuser")
    @commands.has_permissions(administrator=True)
    async def removeuser_command(self, ctx, member: discord.Member):
        """Remove a specific user from the leaderboard"""
        await db.remove_user(ctx.guild.id, member.id)
        await ctx.send(f"✅ {member.display_name} has been removed from the leaderboard.")

# -------------------- LOAD COG --------------------
def setup(bot):
    bot.add_cog(PointsCog(bot))
