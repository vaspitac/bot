# modules/setup/setup_roles_channels.py
import discord
from discord.ui import Modal, TextInput
from discord import Interaction
from database import DatabaseManager

db = DatabaseManager()

class RoleChannelModal(Modal):
    def __init__(self):
        super().__init__(title="Set Role or Channel")

        self.role_type = TextInput(label="Type (admin/staff/helper/viewer/blocked/reward/ticket_category/transcript_channel)",
                                   placeholder="Type role or channel type...",
                                   required=True, max_length=50)
        self.add_item(self.role_type)

        self.id_input = TextInput(label="ID", placeholder="Enter the ID here", required=True)
        self.add_item(self.id_input)

    async def on_submit(self, interaction: Interaction):
        field_type = self.role_type.value.lower()
        field_id = int(self.id_input.value)

        role_fields = {
            "admin": "admin_role_id",
            "staff": "staff_role_id",
            "helper": "helper_role_id",
            "viewer": "viewer_role_id",
            "blocked": "blocked_role_id",
            "reward": "reward_role_id"
        }

        channel_fields = {
            "ticket_category": "ticket_category_id",
            "transcript_channel": "transcript_channel_id"
        }

        if field_type in role_fields:
            await db.update_server_config(interaction.guild.id, **{role_fields[field_type]: field_id})
        elif field_type in channel_fields:
            await db.update_server_config(interaction.guild.id, **{channel_fields[field_type]: field_id})
        else:
            await interaction.response.send_message("❌ Invalid type!", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ `{field_type}` set to ID `{field_id}`.", ephemeral=True)
