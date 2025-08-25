import discord
from discord.ext import commands
from discord import Embed
from database import db
from .ticket_views import TicketView

CATEGORY_POINTS = {
    "Ultra Speaker Express": 8,
    "Ultra Gramiel Express": 7,
    "4-Man Ultra Daily Express": 4,
    "7-Man Ultra Daily Express": 7,
    "Ultra Weekly Express": 12,
    "Grim Express": 10,
    "Daily Temple Express": 6
}

CATEGORY_SLOTS = {
    "Ultra Speaker Express": 3,
    "Ultra Gramiel Express": 3,
    "4-Man Ultra Daily Express": 3,
    "7-Man Ultra Daily Express": 6,
    "Ultra Weekly Express": 3,
    "Grim Express": 6,
    "Daily Temple Express": 3
}

CATEGORY_CHANNEL_NAMES = {
    "Ultra Speaker Express": "ultra-speaker",
    "Ultra Gramiel Express": "ultra-gramiel",
    "4-Man Ultra Daily Express": "4-man-daily",
    "7-Man Ultra Daily Express": "7-man-daily",
    "Ultra Weekly Express": "weekly-ultra",
    "Grim Express": "grimchallenge",
    "Daily Temple Express": "templeshrine"
}

class TicketCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_POINTS = CATEGORY_POINTS
        self.CATEGORY_SLOTS = CATEGORY_SLOTS
        self.CATEGORY_CHANNEL_NAMES = CATEGORY_CHANNEL_NAMES

    async def create_ticket(self, interaction, category, answers):
        guild_id = interaction.guild.id

        # Determine ticket number
        async with db.get_connection() as conn:
            async with conn.execute(
                "SELECT MAX(ticket_number) FROM active_tickets WHERE guild_id=? AND ticket_type=?",
                (guild_id, category)
            ) as cursor:
                row = await cursor.fetchone()
                ticket_number = (row[0] or 0) + 1

        # Channel name
        channel_name = f"{CATEGORY_CHANNEL_NAMES[category]}-{ticket_number}"

        # Permissions
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        }

        # Create channel
        category_channel = interaction.guild.get_channel((await db.get_server_config(guild_id))["ticket_category_id"])
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category_channel,
            overwrites=overwrites,
            reason=f"{category} ticket created by {interaction.user.display_name}"
        )

        slots = CATEGORY_SLOTS[category]
        ticket_view = TicketView(interaction.user, category, slots, guild_id, ticket_channel)

        # Embed
        embed = Embed(title=f"🎫 {category} Ticket", color=discord.Color.green())
        for k, v in answers.items():
            if v:
                embed.add_field(name=f"{k}", value=v, inline=True)
        helper_list = [f"{i+1}. [Empty]" for i in range(slots)]
        embed.add_field(name="👥 Helpers", value="\n".join(helper_list), inline=False)
        embed.add_field(name="🏆 Points Value", value=f"{CATEGORY_POINTS[category]} points", inline=True)

        await ticket_channel.send(f"Hello {interaction.user.mention}! Your ticket has been created.", embed=embed, view=ticket_view)

        # Save ticket in DB
        await db.save_active_ticket(guild_id, ticket_channel.id, interaction.user.id, category, ticket_number)

def setup(bot):
    bot.add_cog(TicketCommandsCog(bot))
