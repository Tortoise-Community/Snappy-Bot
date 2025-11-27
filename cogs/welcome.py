from __future__ import annotations

import discord
from discord.ext import commands

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
            dm_embed = discord.Embed(
                title=f"Welcome to {guild.name}!",
                description=(
                    "For daily **Leetcode challenges** checkout <#780841435712716800>\n\n"
                    "Please introduce yourself in <#577192344533598472>"
                ),
                color=discord.Color.green(),
            )
            dm_embed.set_footer(text="If you have any questions, feel free to ask the staff team.", icon_url="https://s6.imgcdn.dev/YP66q0.png")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # User has DMs closed – just ignore
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
