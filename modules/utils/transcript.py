# modules/tickets/transcript.py
import discord
import io
from discord import Embed
from database import get_server_config

async def save_transcript(channel: discord.TextChannel, ticket_view):
    config = await get_server_config(channel.guild.id)
    transcript_channel = channel.guild.get_channel(config.get("transcript_channel_id")) if config else None
    if not transcript_channel:
        return

    lines = [f"=== TRANSCRIPT: {channel.name} ==="]
    async for msg in channel.history(limit=None, oldest_first=True):
        content = msg.content if msg.content else "[No text content]"
        lines.append(f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author.display_name}: {content}")
        for a in msg.attachments:
            lines.append(f"    📎 Attachment: {a.filename}")

    transcript_file = io.BytesIO("\n".join(lines).encode("utf-8"))
    transcript_file.seek(0)

    embed = Embed(title=f"📄 Ticket Transcript: {ticket_view.category}", color=discord.Color.red())
    embed.add_field(name="Ticket Owner", value=ticket_view.owner.mention, inline=True)
    embed.add_field(name="Channel", value=f"#{channel.name}", inline=True)

    await transcript_channel.send(embed=embed, file=discord.File(transcript_file, filename=f"transcript-{channel.name}.txt"))
