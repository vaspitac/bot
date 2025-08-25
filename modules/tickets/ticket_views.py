import discord
from discord.ui import View, Button, Select
from database import db

class TicketView(View):
    def __init__(self, owner: discord.Member, category: str, slots: int, guild_id: int, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.owner = owner
        self.category = category
        self.slots = slots
        self.guild_id = guild_id
        self.channel = channel
        self.helpers = []

        self.add_item(JoinButton(self))
        self.add_item(LeaveButton(self))
        self.add_item(RemoveHelperButton(self))
        self.add_item(CloseButton(self))

# --- BUTTONS ---
class JoinButton(Button):
    def __init__(self, ticket_view):
        super().__init__(label="Join as Helper", style=discord.ButtonStyle.success, emoji="🙋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user in self.ticket_view.helpers:
            return await interaction.response.send_message("❌ Already helping!", ephemeral=True)
        if len(self.ticket_view.helpers) >= self.ticket_view.slots:
            return await interaction.response.send_message("❌ Ticket full!", ephemeral=True)
        self.ticket_view.helpers.append(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        await self.ticket_view.update_helpers_embed(interaction)

class LeaveButton(Button):
    def __init__(self, ticket_view):
        super().__init__(label="Leave Ticket", style=discord.ButtonStyle.secondary, emoji="👋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.ticket_view.helpers:
            return await interaction.response.send_message("❌ Not a helper!", ephemeral=True)
        self.ticket_view.helpers.remove(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, overwrite=None)
        await self.ticket_view.update_helpers_embed(interaction)

class RemoveHelperButton(Button):
    def __init__(self, ticket_view):
        super().__init__(label="Remove Helper", style=discord.ButtonStyle.danger, emoji="🗑️")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        # Only staff/admin can remove helpers
        config = await db.get_server_config(self.ticket_view.guild_id)
        staff_role = self.ticket_view.channel.guild.get_role(config.get("staff_role_id"))
        admin_role = self.ticket_view.channel.guild.get_role(config.get("admin_role_id"))
        if staff_role not in interaction.user.roles and admin_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ No permission!", ephemeral=True)

        if not self.ticket_view.helpers:
            return await interaction.response.send_message("❌ No helpers to remove.", ephemeral=True)
        options = [discord.SelectOption(label=h.display_name, value=str(i)) for i, h in enumerate(self.ticket_view.helpers)]
        select = HelperRemovalSelect(self.ticket_view, options)
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select helper to remove:", view=view, ephemeral=True)

class HelperRemovalSelect(Select):
    def __init__(self, ticket_view, options):
        super().__init__(placeholder="Choose helper...", options=options)
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        removed = self.ticket_view.helpers.pop(index)
        await self.ticket_view.channel.set_permissions(removed, overwrite=None)
        await self.ticket_view.update_helpers_embed(interaction)
        await interaction.response.send_message(f"✅ Removed {removed.mention}", ephemeral=True)

class CloseButton(Button):
    def __init__(self, ticket_view):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        points = self.ticket_view.channel.guild.get_cog("TicketCommandsCog").CATEGORY_POINTS[self.ticket_view.category]
        for helper in self.ticket_view.helpers:
            await db.add_user_points(self.ticket_view.guild_id, helper.id, points)
        await interaction.response.send_message("Ticket closed. Points awarded to helpers.", ephemeral=True)
        await self.ticket_view.channel.delete()

# --- Helper method for updating embed ---
async def update_helpers_embed(self, interaction=None):
    embed = self.channel.last_message.embeds[0]
    helper_list = [f"{i+1}. {self.helpers[i].mention}" if i < len(self.helpers) else f"{i+1}. [Empty]" for i in range(self.slots)]
    for i, field in enumerate(embed.fields):
        if field.name == "👥 Helpers":
            embed.set_field_at(i, name="👥 Helpers", value="\n".join(helper_list), inline=False)
    if interaction:
        await interaction.message.edit(embed=embed, view=self)
    else:
        last_msg = await self.channel.fetch_message(self.channel.last_message.id)
        await last_msg.edit(embed=embed, view=self)

TicketView.update_helpers_embed = update_helpers_embed
