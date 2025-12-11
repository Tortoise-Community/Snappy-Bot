from __future__ import annotations

import discord
from discord.ext import commands
import constants

WELCOME_CHANNEL_ID = 577192344533598472


class Welcome(commands.Cog):
    """Send a welcome message when someone joins the server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Ignore DMs / non-guild joins (just in case)
        guild = member.guild
        if guild is None or guild.id !=  577192344529404154:
            return

        # Decide which channel to send to
        channel = None

        if WELCOME_CHANNEL_ID:
            channel = guild.get_channel(WELCOME_CHANNEL_ID)

        # Fallback: use system channel if set and viewable
        if channel is None:
            channel = guild.system_channel

        # If we still don't have a channel, give up gracefully
        if channel is None:
            return

        try:
            await channel.send(content=f"Hi {member.mention}! Welcome to our server.", delete_after=120)
        except discord.Forbidden:
            # Bot can't send messages in the channel
            pass

        try:
            content_footer = (
                f"Links: [Website]({constants.website_url}) | "
                f"[Rules]({constants.rules_url}) | "
                f"[Events]({constants.events_url})"
            )
            dm_embed = discord.Embed(
                title=f"Welcome to {guild.name}!",
                description=(
                    "Introduce yourself in <#577192344533598472>\n\n"
                    "For **Leetcode challenges** checkout <#780841435712716800>\n\n\n"
                    + content_footer
                ),
                color=discord.Color.green(),
            )
            dm_embed.set_footer(text="Tortoise Programming Community", icon_url="https://s6.imgcdn.dev/YP66q0.png")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # User has DMs closed – just ignore
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
