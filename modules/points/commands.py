import discord
from discord import app_commands, Embed, Color, ui
from discord.ext import commands

class PointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="points", description="Check points for yourself or another user")
    @app_commands.describe(member="The user to check points for (optional)")
    async def points(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        points = await self.bot.db.get_user_points(interaction.guild.id, member.id)
        await interaction.response.send_message(f"💰 {member.display_name} has {points} points.")

    @app_commands.command(name="leaderboard", description="Show the top 10 users on the leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        all_points = await self.bot.db.get_all_user_points(interaction.guild.id)
        if not all_points:
            await interaction.response.send_message("No points recorded yet.")
            return

        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        embed = Embed(
            title="🏆 Leaderboard",
            description="Top 10 helpers by points",
            color=Color.gold()
        )
        for i, (user_id, points) in enumerate(sorted_points[:10], start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"User ID {user_id}"
            embed.add_field(
                name=f"{i}. {name}",
                value=f"Points: **{points}**",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="myrank", description="Show your current rank in the leaderboard")
    async def myrank(self, interaction: discord.Interaction):
        all_points = await self.bot.db.get_all_user_points(interaction.guild.id)
        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        for i, (user_id, points) in enumerate(sorted_points, start=1):
            if user_id == interaction.user.id:
                await interaction.response.send_message(f"📊 {interaction.user.display_name}, your rank is #{i} with {points} points.")
                return
        await interaction.response.send_message(f"📊 {interaction.user.display_name}, you have 0 points and are not on the leaderboard.")

    @app_commands.command(name="addpoints", description="Add points to a user (admin only)")
    @app_commands.describe(member="The user to add points to", amount="Amount of points to add")
    @app_commands.default_permissions(administrator=True)
    async def addpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await self.bot.db.add_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Added {amount} points to {member.display_name}.")

    @app_commands.command(name="removepoints", description="Remove points from a user (admin only)")
    @app_commands.describe(member="The user to remove points from", amount="Amount of points to remove")
    @app_commands.default_permissions(administrator=True)
    async def removepoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        current = await self.bot.db.get_user_points(interaction.guild.id, member.id)
        new_total = max(current - amount, 0)
        await self.bot.db.set_user_points(interaction.guild.id, member.id, new_total)
        await interaction.response.send_message(f"✅ Removed {amount} points from {member.display_name}. New total: {new_total}")

    @app_commands.command(name="setpoints", description="Set points for a user (admin only)")
    @app_commands.describe(member="The user to set points for", amount="Amount of points to set")
    @app_commands.default_permissions(administrator=True)
    async def setpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await self.bot.db.set_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Set {member.display_name}'s points to {amount}.")

    @app_commands.command(name="removeuser", description="Remove a specific user from the leaderboard")
    @app_commands.describe(member="The user to remove from leaderboard")
    @app_commands.default_permissions(administrator=True)
    async def removeuser(self, interaction: discord.Interaction, member: discord.Member):
        await self.bot.db.remove_user(interaction.guild.id, member.id)
        await interaction.response.send_message(f"✅ {member.display_name} has been removed from the leaderboard.")

    @app_commands.command(name="resetlb", description="Reset the leaderboard with confirmation")
    @app_commands.default_permissions(administrator=True)
    async def resetlb(self, interaction: discord.Interaction):
        class Confirm(ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: ui.Button):
                await self.bot.db.clear_all_points(interaction.guild.id)
                await button_interaction.response.edit_message(content="✅ Leaderboard has been reset!", view=None)
                self.value = True
                self.stop()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: ui.Button):
                await button_interaction.response.edit_message(content="❌ Leaderboard reset cancelled.", view=None)
                self.value = False
                self.stop()

        await interaction.response.send_message("⚠️ Are you sure you want to reset the leaderboard?", view=Confirm(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(PointsCog(bot))