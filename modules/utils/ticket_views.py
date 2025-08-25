# modules/tickets/ticket_views.py
import discord
from discord.ui import View, Button, Select
from discord import ButtonStyle, Interaction
from database import db, get_helper_slots, get_point_values, get_admin_roles
import asyncio
from .transcript import save_transcript

class TicketView(View):
    def __init__(self, owner: discord.Member, category: str, slots: int, guild_id: int):
        super().__init__(timeout=None)
        self.owner = owner
        self.category = category
        self.slots = slots
        self.guild_id = guild_id
        self.helpers = []

        self.add_item(JoinButton(self))
        self.add_item(LeaveButton(self))
        self.add_item(RemoveHelperButton(self))
        self.add_item(CloseButton(self))

class JoinButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Join as Helper", style=ButtonStyle.success, emoji="🙋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        if interaction.user in self.ticket_view.helpers:
            await interaction.response.send_message("❌ Already helping!", ephemeral=True)
            return
        if len(self.ticket_view.helpers) >= self.ticket_view.slots:
            await interaction.response.send_message("❌ Ticket full!", ephemeral=True)
            return
        self.ticket_view.helpers.append(interaction.user)
        await interaction.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        await self.update_embed(interaction)
        await interaction.response.send_message("✅ You joined this ticket.", ephemeral=True)

    async def update_embed(self, interaction):
        embed = interaction.message.embeds[0]
        helper_list = [f"{i+1}. {self.ticket_view.helpers[i].mention}" if i < len(self.ticket_view.helpers) else f"{i+1}. [Empty]" for i in range(self.ticket_view.slots)]
        for i, f in enumerate(embed.fields):
            if f.name == "👥 Helpers":
                embed.set_field_at(i, name="👥 Helpers", value="\n".join(helper_list), inline=False)
        await interaction.message.edit(embed=embed, view=self.ticket_view)

class LeaveButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Leave Ticket", style=ButtonStyle.secondary, emoji="👋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        if interaction.user not in self.ticket_view.helpers:
            await interaction.response.send_message("❌ Not a helper!", ephemeral=True)
            return
        self.ticket_view.helpers.remove(interaction.user)
        await interaction.channel.set_permissions(interaction.user, overwrite=None)
        await JoinButton(self.ticket_view).update_embed(interaction)
        await interaction.response.send_message("👋 You left the ticket.", ephemeral=True)

class RemoveHelperButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Remove Helper", style=ButtonStyle.danger, emoji="🗑️")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        admin_roles = await get_admin_roles(interaction.guild.id)
        is_admin = interaction.user.guild_permissions.administrator or any(r.id in admin_roles for r in interaction.user.roles)
        if not is_admin:
            await interaction.response.send_message("❌ No permission!", ephemeral=True)
            return
        if not self.ticket_view.helpers:
            await interaction.response.send_message("❌ No helpers to remove!", ephemeral=True)
            return

        options = [discord.SelectOption(label=h.display_name, value=str(i)) for i, h in enumerate(self.ticket_view.helpers)]
        select = HelperSelect(self.ticket_view, options)
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Select helper to remove:", view=view, ephemeral=True)

class HelperSelect(Select):
    def __init__(self, ticket_view, options):
        super().__init__(placeholder="Choose a helper", min_values=1, max_values=1, options=options)
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        index = int(self.values[0])
        removed = self.ticket_view.helpers.pop(index)
        await interaction.channel.set_permissions(removed, overwrite=None)
        await JoinButton(self.ticket_view).update_embed(interaction)
        await interaction.response.send_message(f"✅ {removed.mention} removed.", ephemeral=True)

class CloseButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Close Ticket", style=ButtonStyle.danger, emoji="🔒")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        admin_roles = await get_admin_roles(interaction.guild.id)
        is_admin = interaction.user.guild_permissions.administrator or any(r.id in admin_roles for r in interaction.user.roles)
        if interaction.user != self.ticket_view.owner and not is_admin:
            await interaction.response.send_message("❌ Only owner/admin can close!", ephemeral=True)
            return

        # Award points to helpers
        points = (await get_point_values(self.ticket_view.guild_id)).get(self.ticket_view.category, 0)
        for helper in self.ticket_view.helpers:
            await db.add_user_points(self.ticket_view.guild_id, helper.id, points)

        # Save transcript
        await save_transcript(interaction.channel, self.ticket_view)

        await interaction.response.send_message(f"🔒 Ticket closed. Helpers awarded {points} points each.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Closed by {interaction.user.display_name}")
