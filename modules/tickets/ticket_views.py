# modules/tickets/ticket_views.py
import discord
from discord.ui import View, Button, Select
from discord import ButtonStyle, Interaction
from database import DatabaseManager
import asyncio

# Initialize database
db = DatabaseManager()

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

    async def update_helpers_embed(self, interaction=None):
        """Update the helpers list in the embed"""
        # Get the embed from the message
        message = interaction.message if interaction else await self.channel.fetch_message(self.channel.last_message.id)
        embed = message.embeds[0]
        
        # Update helpers list
        helper_list = []
        for i in range(self.slots):
            if i < len(self.helpers):
                helper_list.append(f"{i+1}. {self.helpers[i].mention}")
            else:
                helper_list.append(f"{i+1}. [Empty]")
        
        # Find and update the helpers field
        for i, field in enumerate(embed.fields):
            if field.name == "👥 Helpers":
                embed.set_field_at(i, name="👥 Helpers", value="\n".join(helper_list), inline=False)
                break
        
        # Update the message
        if interaction:
            await interaction.message.edit(embed=embed, view=self)
        else:
            await message.edit(embed=embed, view=self)

class JoinButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Join as Helper", style=ButtonStyle.success, emoji="🙋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        if interaction.user in self.ticket_view.helpers:
            await interaction.response.send_message("❌ You're already helping with this ticket!", ephemeral=True)
            return
        if len(self.ticket_view.helpers) >= self.ticket_view.slots:
            await interaction.response.send_message("❌ This ticket is full!", ephemeral=True)
            return
        
        # Add helper
        self.ticket_view.helpers.append(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        
        # Update database
        await db.update_ticket_helpers(self.ticket_view.guild_id, self.ticket_view.channel.id, [h.id for h in self.ticket_view.helpers])
        
        # Update embed and respond
        await self.ticket_view.update_helpers_embed(interaction)
        await interaction.response.send_message("✅ You joined this ticket as a helper!", ephemeral=True)

class LeaveButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Leave Ticket", style=ButtonStyle.secondary, emoji="👋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        if interaction.user not in self.ticket_view.helpers:
            await interaction.response.send_message("❌ You're not helping with this ticket!", ephemeral=True)
            return
        
        # Remove helper
        self.ticket_view.helpers.remove(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, overwrite=None)
        
        # Update database
        await db.update_ticket_helpers(self.ticket_view.guild_id, self.ticket_view.channel.id, [h.id for h in self.ticket_view.helpers])
        
        # Update embed and respond
        await self.ticket_view.update_helpers_embed(interaction)
        await interaction.response.send_message("👋 You left the ticket.", ephemeral=True)

class RemoveHelperButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Remove Helper", style=ButtonStyle.danger, emoji="🗑️")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        # Check permissions
        config = await db.get_server_config(interaction.guild.id)
        is_admin = interaction.user.guild_permissions.administrator
        is_staff = False
        
        if config:
            admin_role_id = config.get("admin_role_id")
            staff_role_id = config.get("staff_role_id")
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if admin_role_id and admin_role_id in user_role_ids:
                is_admin = True
            if staff_role_id and staff_role_id in user_role_ids:
                is_staff = True
        
        if not (is_admin or is_staff):
            await interaction.response.send_message("❌ Only staff/admins can remove helpers!", ephemeral=True)
            return
        
        if not self.ticket_view.helpers:
            await interaction.response.send_message("❌ No helpers to remove!", ephemeral=True)
            return

        # Create selection dropdown
        options = [
            discord.SelectOption(label=h.display_name, value=str(i)) 
            for i, h in enumerate(self.ticket_view.helpers)
        ]
        select = HelperSelect(self.ticket_view, options)
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Select helper to remove:", view=view, ephemeral=True)

class HelperSelect(Select):
    def __init__(self, ticket_view, options):
        super().__init__(placeholder="Choose a helper to remove...", min_values=1, max_values=1, options=options)
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        index = int(self.values[0])
        removed_helper = self.ticket_view.helpers.pop(index)
        
        # Remove permissions
        await self.ticket_view.channel.set_permissions(removed_helper, overwrite=None)
        
        # Update database
        await db.update_ticket_helpers(self.ticket_view.guild_id, self.ticket_view.channel.id, [h.id for h in self.ticket_view.helpers])
        
        # Update embed
        await self.ticket_view.update_helpers_embed()
        await interaction.response.send_message(f"✅ Removed {removed_helper.mention} from the ticket.", ephemeral=True)

class CloseButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Close Ticket", style=ButtonStyle.danger, emoji="🔒")
        self.ticket_view = ticket_view

    async def callback(self, interaction: Interaction):
        # Check permissions - only ticket owner or staff/admin can close
        config = await db.get_server_config(interaction.guild.id)
        is_owner = interaction.user == self.ticket_view.owner
        is_admin = interaction.user.guild_permissions.administrator
        is_staff = False
        
        if config:
            admin_role_id = config.get("admin_role_id") 
            staff_role_id = config.get("staff_role_id")
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if admin_role_id and admin_role_id in user_role_ids:
                is_admin = True
            if staff_role_id and staff_role_id in user_role_ids:
                is_staff = True
        
        if not (is_owner or is_admin or is_staff):
            await interaction.response.send_message("❌ Only the ticket owner or staff can close this ticket!", ephemeral=True)
            return

        # Get point values for this category
        ticket_cog = interaction.client.get_cog("TicketCommandsCog")
        points = ticket_cog.CATEGORY_POINTS.get(self.ticket_view.category, 0) if ticket_cog else 0
        
        # Award points to helpers
        for helper in self.ticket_view.helpers:
            await db.add_user_points(self.ticket_view.guild_id, helper.id, points)

        # Save transcript
        await self.save_transcript(interaction.channel, interaction.user)

        # Remove from active tickets
        await db.remove_active_ticket(self.ticket_view.guild_id, self.ticket_view.channel.id)

        await interaction.response.send_message(f"🔒 Ticket closed! {len(self.ticket_view.helpers)} helpers awarded {points} points each.", ephemeral=True)
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.display_name}")

    async def save_transcript(self, channel: discord.TextChannel, closed_by: discord.Member):
        """Save transcript of the ticket"""
        config = await db.get_server_config(channel.guild.id)
        transcript_channel_id = config.get("transcript_channel_id") if config else None
        
        if not transcript_channel_id:
            return  # No transcript channel configured
        
        transcript_channel = channel.guild.get_channel(transcript_channel_id)
        if not transcript_channel:
            return

        # Collect messages
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            content = message.content if message.content else "[No text content]"
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            messages.append(f"[{timestamp}] {message.author.display_name}: {content}")
            
            # Add attachments info
            for attachment in message.attachments:
                messages.append(f"    📎 Attachment: {attachment.filename}")

        # Create transcript file
        transcript_content = f"=== TRANSCRIPT: {channel.name} ===\n" + "\n".join(messages)
        transcript_file = discord.File(
            fp=discord.utils.BytesIO(transcript_content.encode('utf-8')),
            filename=f"transcript-{channel.name}.txt"
        )

        # Send to transcript channel
        embed = discord.Embed(
            title=f"📄 Ticket Transcript: {self.ticket_view.category}",
            color=discord.Color.red()
        )
        embed.add_field(name="Ticket Owner", value=self.ticket_view.owner.mention, inline=True)
        embed.add_field(name="Closed By", value=closed_by.mention, inline=True)
        embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)
        embed.add_field(name="Helpers", value=f"{len(self.ticket_view.helpers)} helpers", inline=True)

        await transcript_channel.send(embed=embed, file=transcript_file)