# modules/utils/help_commands.py
import discord
from discord.ext import commands
from discord import app_commands
from database import DatabaseManager

db = DatabaseManager()

class HelpCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all bot commands and help")
    async def slash_help(self, interaction: discord.Interaction):
        """Slash command version of help"""
        await self.send_help_embed(interaction, is_slash=True)

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Regular command version of help"""
        await self.send_help_embed(ctx, is_slash=False)

    async def send_help_embed(self, ctx_or_interaction, is_slash=False):
        """Send the help embed with your custom text"""
        
        # Check if user has admin/staff permissions
        if is_slash:
            user = ctx_or_interaction.user
            guild = ctx_or_interaction.guild
        else:
            user = ctx_or_interaction.author
            guild = ctx_or_interaction.guild

        # Check permissions
        config = await db.get_server_config(guild.id)
        is_admin = user.guild_permissions.administrator
        is_staff = False
        
        if config:
            admin_role_id = config.get("admin_role_id")
            staff_role_id = config.get("staff_role_id")
            user_role_ids = [role.id for role in user.roles]
            
            if admin_role_id and admin_role_id in user_role_ids:
                is_admin = True
            if staff_role_id and staff_role_id in user_role_ids:
                is_staff = True

        # Create embed with your exact style
        embed = discord.Embed(
            title="✨ Bot Commands & Help",
            description="Welcome! Here are all the commands you can use.",
            color=discord.Color.blurple()
        )

        # Ticket Commands
        ticket_commands = (
            "`!create` or `/create` — Create ticket panel (admin, staff)\n"
            "`!removehelper @user` — Remove helper from ticket (admin, staff)"
        )
        embed.add_field(name="🎫 Ticket Commands", value=ticket_commands, inline=False)

        # Points & Leaderboard  
        points_commands = (
            "`!leaderboard` or `/leaderboard` — View top helpers\n"
            "`!points [@user]` or `/points` — See someone's points\n"
            "`!myrank` or `/myrank` — See your leaderboard rank\n"
            "`!pointsinfo` — Learn about the points system"
        )
        
        if is_admin or is_staff:
            points_commands += (
                "\n`!addpoints @user amount` or `/addpoints` — Add points (admin, staff)\n"
                "`!removepoints @user amount` or `/removepoints` — Remove points (admin, staff)\n"
                "`!setpoints @user amount` or `/setpoints` — Set points (admin, staff)\n"
                "`!removeuser @user` or `/removeuser` — Remove user from leaderboard (admin, staff)"
            )
            
        if is_admin:
            points_commands += "\n`!resetlb` or `/resetlb` — Reset entire leaderboard (admin)"
            
        embed.add_field(name="📊 Points & Leaderboard", value=points_commands, inline=False)

        # Rules & Setup
        rules_commands = (
            "`!hrules` or `/hrules` — Helper guidelines\n"
            "`!rrules` or `/rrules` — Requester guidelines\n"
            "`!proof` or `/proof` — Proof requirements"
        )
        
        if is_admin:
            rules_commands += (
                "\n`!setup` or `/setup` — Configure server settings (admin)\n"
                "`!setupcommands` — Configure custom commands (admin)\n"
                "`!resetsetup` — Reset all server settings (admin)"
            )
            
        embed.add_field(name="📜 Rules & Setup", value=rules_commands, inline=False)

        # Footer
        embed.set_footer(text="Need more help? Contact a member of the staff team!")
        
        if is_slash:
            await ctx_or_interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed)

    # Command aliases matching your desired names
    @commands.command(name="mypoints")
    async def mypoints_alias(self, ctx):
        """Alias for !points command"""
        points_cog = self.bot.get_cog("PointsCog")
        if points_cog:
            await points_cog.points_command(ctx)

    @app_commands.command(name="mypoints", description="See your own points")
    async def slash_mypoints(self, interaction: discord.Interaction):
        """Slash version of mypoints"""
        points_cog = self.bot.get_cog("PointsCog")
        if points_cog:
            points = await db.get_user_points(interaction.guild.id, interaction.user.id)
            await interaction.response.send_message(f"💰 {interaction.user.display_name} has {points} points.")

async def setup(bot):
    await bot.add_cog(HelpCommandsCog(bot))