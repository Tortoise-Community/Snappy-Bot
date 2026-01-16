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

    JOIN_GRACE_PERIOD = 8 * 60        # seconds since joining (5 minutes)
    CHANNEL_THRESHOLD = 4             # number of distinct channels
    SPAM_WINDOW = 30                  # seconds
    BAN_REASON = "Raid protection: multi-channel spam on join"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # guild_id -> user_id -> deque[(timestamp, channel_id)]
        self.message_log = defaultdict(lambda: defaultdict(deque))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        member = message.author
        guild = message.guild

        # Ignore moderators
        if member.guild_permissions.manage_messages:
            return

        # Ensure joined_at exists
        if not member.joined_at:
            return

        now = time.time()
        join_age = (discord.utils.utcnow() - member.joined_at).total_seconds()

        # Only enforce for new joins
        if join_age > self.JOIN_GRACE_PERIOD:
            return

        logs = self.message_log[guild.id][member.id]
        logs.append((now, message.channel.id))

        # Drop old entries
        while logs and now - logs[0][0] > self.SPAM_WINDOW:
            logs.popleft()

        # Count unique channels
        unique_channels = {cid for _, cid in logs}

        if len(unique_channels) >= self.CHANNEL_THRESHOLD:
            await self.ban_member(member, message)
            self.message_log[guild.id].pop(member.id, None)


    async def ban_member(self, member: discord.Member, message: discord.Message):
        guild = member.guild

        # Delete triggering message
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        # Ban user
        try:
            await guild.ban(
                member,
                reason=self.BAN_REASON,
                delete_message_days=1,
            )
        except discord.Forbidden:
            return

        channel = guild.get_channel(bot_dev_channel_id)
        if channel:
            await channel.send(
                f"🚨 **Raid Ban Triggered**\n"
                f"User: `{member}` (`{member.id}`)\n"
                f"Joined: <t:{int(member.joined_at.timestamp())}:R>\n"
                f"Reason: {self.BAN_REASON}"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiRaidSpam(bot))
