# modules/setup/setup_reset.py
from discord.ext import commands
from database import DatabaseManager

db = DatabaseManager()

class SetupResetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="resetsetup")
    @commands.has_permissions(administrator=True)
    async def resetsetup(self, ctx):
        await db.update_server_config(ctx.guild.id,
                                      admin_role_id=None,
                                      staff_role_id=None,
                                      helper_role_id=None,
                                      viewer_role_id=None,
                                      blocked_role_id=None,
                                      reward_role_id=None,
                                      ticket_category_id=None,
                                      transcript_channel_id=None)
        await ctx.send("⚠️ Setup has been fully reset!")

def setup(bot):
    bot.add_cog(SetupResetCog(bot))