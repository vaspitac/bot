import discord
from discord.ui import Modal, TextInput, InputTextStyle

class TicketModal(Modal):
    def __init__(self, category: str, guild_id: int):
        super().__init__(title=f"{category} Ticket Form")
        self.category = category
        self.guild_id = guild_id

        self.in_game_name = TextInput(
            label="In-game name?",
            placeholder="Enter your in-game name",
            style=InputTextStyle.short,
            required=True
        )
        self.server_name = TextInput(
            label="Server name?",
            placeholder="Enter your server",
            style=InputTextStyle.short,
            required=True
        )
        self.room_number = TextInput(
            label="Room number?",
            placeholder="Enter room number",
            style=InputTextStyle.short,
            required=True
        )
        self.additional_info = TextInput(
            label="Additional info (optional)",
            placeholder="Any extra info...",
            style=InputTextStyle.long,
            required=False
        )

        self.add_item(self.in_game_name)
        self.add_item(self.server_name)
        self.add_item(self.room_number)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Send data to ticket cog
        await interaction.client.get_cog("TicketCommandsCog").create_ticket(
            interaction=interaction,
            category=self.category,
            answers={
                "In-game Name": self.in_game_name.value,
                "Server Name": self.server_name.value,
                "Room Number": self.room_number.value,
                "Additional Info": self.additional_info.value
            }
        )
