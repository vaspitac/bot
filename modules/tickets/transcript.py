# modules/tickets/transcript.py
import discord
from discord.ext import commands
import io
from database import db

class TicketTranscriptCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def save_transcript(self, channel: discord.TextChannel, category: str, owner, closed_by):
        config = await db.get_server_config(channel.guild.id)
        transcript_channel = channel.guild.get_channel(config.get("transcript_channel_id"))
        if not transcript_channel:
            return

        lines = [f"=== TRANSCRIPT: {channel.name} ==="]
        async for msg in channel.history(limit=None, oldest_first=True):
            content = msg.content or "[No text]"
            lines.append(f"[{msg.created_at}] {msg.author.display_name}: {content}")
            for a in msg.attachments:
                lines.append(f"    📎 {a.filename}")

        file = io.BytesIO("\n".join(lines).encode("utf-8"))
        file.seek(0)

        embed = discord.Embed(title=f"📄 Ticket Transcript: {category}", color=discord.Color.red())
        embed.add_field(name="Owner", value=owner.mention)
        embed.add_field(name="Closed By", value=closed_by.mention)
        embed.add_field(name="Channel", value=f"#{channel.name}")

        await transcript_channel.send(embed=embed, file=discord.File(file, filename=f"transcript-{channel.name}.txt"))

def setup(bot):
    bot.add_cog(TicketTranscriptCog(bot))
