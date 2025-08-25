import discord
from discord.ext import commands
from discord import Embed
from database import DatabaseManager

db = DatabaseManager()  # initialize your database manager

class CustomCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rrules")
    async def rrules_command(self, ctx):
        """Display custom rules for runners"""
        command_data = await db.get_custom_command(ctx.guild.id, "rrules")
        if not command_data:
            await ctx.send("❌ Runner rules have not been configured. Use `!setup` to configure custom commands.")
            return
        
        embed = Embed(
            title="📜 Runner Rules",
            description=command_data['content'],
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="hrules")
    async def hrules_command(self, ctx):
        """Display custom rules for helpers"""
        command_data = await db.get_custom_command(ctx.guild.id, "hrules")
        if not command_data:
            await ctx.send("❌ Helper rules have not been configured. Use `!setup` to configure custom commands.")
            return
        
        embed = Embed(
            title="📋 Helper Rules",
            description=command_data['content'],
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="proof")
    async def proof_command(self, ctx):
        """Display proof submission instructions"""
        command_data = await db.get_custom_command(ctx.guild.id, "proof")
        if not command_data:
            await ctx.send("❌ Proof instructions have not been configured. Use `!setup` to configure custom commands.")
            return
        
        embed = Embed(
            title="📸 Proof Submission",
            description=command_data['content'],
            color=discord.Color.gold()
        )
        
        if command_data.get('image_url'):
            embed.set_image(url=command_data['image_url'])
        
        await ctx.send(embed=embed)

# -------------------- LOAD COG --------------------
def setup(bot):
    bot.add_cog(CustomCommandsCog(bot))
