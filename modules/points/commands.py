import discord
from discord.ext import commands
from discord import app_commands, ui
from database import DatabaseManager

db = DatabaseManager()

class PointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==================== POINTS COMMAND ====================
    @app_commands.command(name="points", description="Check points for yourself or another user")
    @app_commands.describe(member="The user to check points for (optional)")
    async def slash_points(self, interaction: discord.Interaction, member: discord.Member = None):
        """Slash command version of points"""
        member = member or interaction.user
        points = await db.get_user_points(interaction.guild.id, member.id)
        await interaction.response.send_message(f"💰 {member.display_name} has {points} points.")

    @commands.command(name="points")
    async def points_command(self, ctx, member: discord.Member = None):
        """Check points for yourself or another user"""
        member = member or ctx.author
        points = await db.get_user_points(ctx.guild.id, member.id)
        await ctx.send(f"💰 {member.display_name} has {points} points.")

    # ==================== LEADERBOARD COMMAND ====================
    @app_commands.command(name="leaderboard", description="Show the top 10 users on the leaderboard")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        """Slash command version of leaderboard"""
        all_points = await db.get_all_user_points(interaction.guild.id)
        if not all_points:
            await interaction.response.send_message("No points recorded yet.")
            return

        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        leaderboard = ""
        for i, (user_id, points) in enumerate(sorted_points[:10], start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"User ID {user_id}"
            leaderboard += f"{i}. {name} — {points} points\n"

        await interaction.response.send_message(f"🏆 **Leaderboard** 🏆\n{leaderboard}")

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

    # ==================== MY RANK COMMAND ====================
    @app_commands.command(name="myrank", description="Show your current rank in the leaderboard")
    async def slash_myrank(self, interaction: discord.Interaction):
        """Slash command version of myrank"""
        all_points = await db.get_all_user_points(interaction.guild.id)
        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        for i, (user_id, points) in enumerate(sorted_points, start=1):
            if user_id == interaction.user.id:
                await interaction.response.send_message(f"📊 {interaction.user.display_name}, your rank is #{i} with {points} points.")
                return
        await interaction.response.send_message(f"📊 {interaction.user.display_name}, you have 0 points and are not on the leaderboard.")

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

    # ==================== ADD POINTS (ADMIN ONLY) ====================
    @app_commands.command(name="addpoints", description="Add points to a user (admin only)")
    @app_commands.describe(member="The user to add points to", amount="Amount of points to add")
    @app_commands.default_permissions(administrator=True)
    async def slash_addpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Slash command version of addpoints"""
        await db.add_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Added {amount} points to {member.display_name}.")

    @commands.command(name="addpoints")
    @commands.has_permissions(administrator=True)
    async def addpoints_command(self, ctx, member: discord.Member, amount: int):
        """Add points to a user (admin only)"""
        await db.add_user_points(ctx.guild.id, member.id, amount)
        await ctx.send(f"✅ Added {amount} points to {member.display_name}.")

    # ==================== REMOVE POINTS (ADMIN ONLY) ====================
    @app_commands.command(name="removepoints", description="Remove points from a user (admin only)")
    @app_commands.describe(member="The user to remove points from", amount="Amount of points to remove")
    @app_commands.default_permissions(administrator=True)
    async def slash_removepoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Slash command version of removepoints"""
        current = await db.get_user_points(interaction.guild.id, member.id)
        new_total = max(current - amount, 0)
        await db.set_user_points(interaction.guild.id, member.id, new_total)
        await interaction.response.send_message(f"✅ Removed {amount} points from {member.display_name}. New total: {new_total}")

    @commands.command(name="removepoints")
    @commands.has_permissions(administrator=True)
    async def removepoints_command(self, ctx, member: discord.Member, amount: int):
        """Remove points from a user (admin only)"""
        current = await db.get_user_points(ctx.guild.id, member.id)
        new_total = max(current - amount, 0)
        await db.set_user_points(ctx.guild.id, member.id, new_total)
        await ctx.send(f"✅ Removed {amount} points from {member.display_name}. New total: {new_total}")

    # ==================== SET POINTS (ADMIN ONLY) ====================
    @app_commands.command(name="setpoints", description="Set points for a user (admin only)")
    @app_commands.describe(member="The user to set points for", amount="Amount of points to set")
    @app_commands.default_permissions(administrator=True)
    async def slash_setpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Slash command version of setpoints"""
        await db.set_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Set {member.display_name}'s points to {amount}.")

    @commands.command(name="setpoints")
    @commands.has_permissions(administrator=True)
    async def setpoints_command(self, ctx, member: discord.Member, amount: int):
        """Set points for a user (admin only)"""
        await db.set_user_points(ctx.guild.id, member.id, amount)
        await ctx.send(f"✅ Set {member.display_name}'s points to {amount}.")

    # ==================== REMOVE USER (ADMIN ONLY) ====================
    @app_commands.command(name="removeuser", description="Remove a specific user from the leaderboard")
    @app_commands.describe(member="The user to remove from leaderboard")
    @app_commands.default_permissions(administrator=True)
    async def slash_removeuser(self, interaction: discord.Interaction, member: discord.Member):
        """Slash command version of removeuser"""
        await db.remove_user(interaction.guild.id, member.id)
        await interaction.response.send_message(f"✅ {member.display_name} has been removed from the leaderboard.")

    @commands.command(name="removeuser")
    @commands.has_permissions(administrator=True)
    async def removeuser_command(self, ctx, member: discord.Member):
        """Remove a specific user from the leaderboard"""
        await db.remove_user(ctx.guild.id, member.id)
        await ctx.send(f"✅ {member.display_name} has been removed from the leaderboard.")

    # ==================== RESET LEADERBOARD (ADMIN ONLY) ====================
    @app_commands.command(name="resetlb", description="Reset the leaderboard with confirmation")
    @app_commands.default_permissions(administrator=True)
    async def slash_resetlb(self, interaction: discord.Interaction):
        """Slash command version of resetlb"""
        
        class Confirm(ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: ui.Button):
                await db.clear_all_points(interaction.guild.id)
                await button_interaction.response.edit_message(content="✅ Leaderboard has been reset!", view=None)
                self.value = True
                self.stop()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: ui.Button):
                await button_interaction.response.edit_message(content="❌ Leaderboard reset cancelled.", view=None)
                self.value = False
                self.stop()

        await interaction.response.send_message("⚠️ Are you sure you want to reset the leaderboard?", view=Confirm(), ephemeral=True)

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

# ==================== LOAD COG ====================
async def setup(bot):
    await bot.add_cog(PointsCog(bot))