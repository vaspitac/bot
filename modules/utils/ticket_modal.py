# modules/tickets/ticket_modal.py
import discord
from discord.ext import commands
from discord import Modal, TextInput, Interaction, Embed
from .ticket_views import TicketView
from database import db, get_point_values, get_helper_slots, get_server_config

class TicketModal(Modal):
    def __init__(self, category: str, guild_id: int):
        super().__init__(title=f"{category} Ticket Form")
        self.category = category
        self.guild_id = guild_id

        # Modal fields
        self.in_game_name = TextInput(
            label="In-game Name",
            placeholder="Enter your in-game name",
            max_length=100
        )
        self.add_item(self.in_game_name)

        self.server_name = TextInput(
            label="Server Name",
            placeholder="Enter the server name",
            max_length=100
        )
        self.add_item(self.server_name)

        self.room_number = TextInput(
            label="Room Number",
            placeholder="Enter the room number",
            max_length=50
        )
        self.add_item(self.room_number)

        self.additional_info = TextInput(
            label="Additional Info (Optional)",
            placeholder="Any extra details...",
            max_length=500,
            required=False
        )
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: Interaction):
        # Fetch server config
        config = await get_server_config(self.guild_id)
        category_channel = interaction.guild.get_channel(config.get("ticket_category_id")) if config else None

        # Determine helper slots
        helper_slots = (await get_helper_slots(self.guild_id)).get(self.category, 3)
        points = (await get_point_values(self.guild_id)).get(self.category, 0)

        # Embed with ticket info
        embed = Embed(
            title=f"🎫 {self.category} Ticket",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Requested by", value=interaction.user.mention, inline=True)
        embed.add_field(name="💠 In-game Name", value=self.in_game_name.value, inline=True)
        embed.add_field(name="🛡 Server Name", value=self.server_name.value, inline=True)
        embed.add_field(name="🔢 Room Number", value=self.room_number.value, inline=True)
        if self.additional_info.value:
            embed.add_field(name="ℹ️ Additional Info", value=self.additional_info.value, inline=False)
        embed.add_field(name="🏆 Points Value", value=f"{points} points", inline=True)
        embed.add_field(name="👥 Helpers", value="\n".join([f"{i+1}. [Empty]" for i in range(helper_slots)]), inline=False)

        # Create ticket view (buttons)
        ticket_view = TicketView(owner=interaction.user, category=self.category, slots=helper_slots, guild_id=self.guild_id)

        # Create ticket channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        }
        ticket_channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}".lower(),
            category=category_channel,
            overwrites=overwrites,
            reason=f"Ticket created by {interaction.user.display_name}"
        )

        await ticket_channel.send(
            f"🎫 **New Ticket Created!**\nHello {interaction.user.mention}, helpers will join below.",
            embed=embed,
            view=ticket_view
        )
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)
