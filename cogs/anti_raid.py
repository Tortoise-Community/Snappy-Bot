from __future__ import annotations

import time
from collections import defaultdict, deque

import discord
from discord.ext import commands
from constants import bot_dev_channel_id


class AntiRaidSpam(commands.Cog):
    """
    Bans users who spam messages across multiple channels shortly after joining.
    """

    JOIN_GRACE_PERIOD = 8 * 60        # seconds since joining
    CHANNEL_THRESHOLD = 3             # distinct channels
    SPAM_WINDOW = 30                  # seconds
    BAN_REASON = "Raid protection: multi-channel spam on join"
    APPEAL_SERVER_URL = "https://discord.gg/X9aQKymWpk"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_log = defaultdict(lambda: defaultdict(deque))


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        member = message.author
        guild = message.guild

        if member.guild_permissions.manage_messages:
            return

        if not member.joined_at:
            return

        join_age = (discord.utils.utcnow() - member.joined_at).total_seconds()
        if join_age > self.JOIN_GRACE_PERIOD:
            return

        now = time.time()
        logs = self.message_log[guild.id][member.id]

        content = self.extract_message_content(message)
        logs.append((now, message.channel.id, content))

        # Remove old entries
        while logs and now - logs[0][0] > self.SPAM_WINDOW:
            logs.popleft()

        unique_channels = {cid for _, cid, _ in logs}

        if len(unique_channels) >= self.CHANNEL_THRESHOLD:
            await self.handle_raid(member, message, list(logs))
            self.message_log[guild.id].pop(member.id, None)


    def extract_message_content(self, message: discord.Message) -> str:
        """
        Extract meaningful content from a Discord message.
        Covers text, embeds, attachments, and stickers.
        """

        parts: list[str] = []

        if message.clean_content:
            parts.append(message.clean_content.strip())

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

        if not parts:
            return "[Empty message payload]"

        return " | ".join(parts)[:500]


    async def handle_raid(
        self,
        member: discord.Member,
        message: discord.Message,
        logs: list[tuple[float, int, str]],
    ):
        guild = member.guild

        await self.send_dm_notice(member, guild)

        try:
            await message.delete()
        except discord.Forbidden:
            pass

        try:
            await guild.ban(
                member,
                reason=self.BAN_REASON,
                delete_message_days=1,
            )
        except discord.Forbidden:
            return

        await self.log_to_mod_channel(guild, member, logs)


    async def send_dm_notice(self, member: discord.Member, guild: discord.Guild):
        embed = discord.Embed(
            title="You have been automatically banned",
            description=(
                f"You were banned from **{guild.name}** due to **automated raid protection**.\n\n"
                "Our system flagged your activity as spam-like behavior after joining.\n\n"
                "**If this was a mistake**, you may appeal using the link below."
            ),
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Appeal",
            value=f"[Join the appeal server]({self.APPEAL_SERVER_URL})",
            inline=False,
        )
        embed.set_footer(text="This action was performed automatically 💠 Tortoise Community")

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass


    async def log_to_mod_channel(
        self,
        guild: discord.Guild,
        member: discord.Member,
        logs: list[tuple[float, int, str]],
    ):
        channel = guild.get_channel(bot_dev_channel_id)
        if channel is None:
            return

        lines = []
        for _, channel_id, content in logs:
            ch = guild.get_channel(channel_id)
            ch_name = f"#{ch.name}" if ch else f"#{channel_id}"
            lines.append(f"**{ch_name}:** {content}")

        embed = discord.Embed(
            title="🚨 Raid Ban Triggered",
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="User",
            value=f"{member} (`{member.id}`)",
            inline=False,
        )
        embed.add_field(
            name="Joined",
            value=f"<t:{int(member.joined_at.timestamp())}:R>",
            inline=False,
        )
        embed.add_field(
            name="Messages",
            value="\n".join(lines),
            inline=False,
        )
        embed.set_footer(text=self.BAN_REASON)

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiRaidSpam(bot))
