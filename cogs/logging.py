from __future__ import annotations

import discord
from discord.ext import commands

from bot import MyBot
from constants import tortoise_guild_id, system_log_channel_id


class Logging(commands.Cog):
    """
    Logs deleted messages (single and bulk) to a moderation channel.
    """

    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild.id != tortoise_guild_id or message.author is None or message.author.bot:
            return

        if message.id in self.bot.suppressed_deletes:
            self.bot.suppressed_deletes.discard(message.id)
            return

        channel = message.guild.get_channel(system_log_channel_id)
        if channel is None:
            return

        content = self.extract_content(message)

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="User",
            value=f"{message.author} (`{message.author.id}`)",
            inline=False,
        )
        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False,
        )
        embed.add_field(
            name="Content",
            value=content[:1024],
            inline=False,
        )

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass


    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        if not messages:
            return

        filtered = []
        for msg in messages:
            if msg.id in self.bot.suppressed_deletes:
                self.bot.suppressed_deletes.discard(msg.id)
                continue
            filtered.append(msg)

        if not filtered:
            return

        guild = messages[0].guild
        if guild.id != tortoise_guild_id :
            return

        channel = guild.get_channel(system_log_channel_id)
        if channel is None:
            return

        entries: list[str] = []

        for message in messages:
            if message.author is None:
                continue

            content = self.extract_content(message)
            entries.append(
                f"**{message.author}** in {message.channel.mention}:\n{content}"
            )

        if not entries:
            return

        MAX_CHARS = 3500
        chunks = []
        current = ""

        for entry in entries:
            if len(current) + len(entry) > MAX_CHARS:
                chunks.append(current)
                current = entry
            else:
                current += "\n\n" + entry if current else entry

        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(
                title="🗑️ Bulk Messages Deleted",
                description=chunk,
                color=discord.Color.dark_red(),
            )
            embed.set_footer(text=f"Batch {i}/{len(chunks)}")

            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass


    @staticmethod
    def extract_content(message: discord.Message) -> str:
        """
        Extract text, embeds, attachments, stickers safely.
        """
        parts: list[str] = []

        if message.content:
            parts.append(message.content.strip())

        for attachment in message.attachments:
            parts.append(f"[Attachment] {attachment.url}")

        for embed in message.embeds:
            if embed.url:
                parts.append(f"[Embed URL] {embed.url}")
            elif embed.title or embed.description:
                preview = (embed.title or embed.description or "").strip()
                if preview:
                    parts.append(f"[Embed] {preview[:200]}")

        if message.stickers:
            parts.append("[Sticker]")

        return " | ".join(parts) if parts else "[No content — possibly automated spam]"


async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
