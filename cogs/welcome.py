from __future__ import annotations

import discord
from discord.ext import commands, tasks
import constants

WELCOME_ROLE_DURATION_DAYS = 7


class Welcome(commands.Cog):
    """Send a welcome message and manage temporary welcome role."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = bot.welcome_role_manager
        self.remove_welcome_roles.start()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if guild is None or guild.id != constants.tortoise_guild_id:
            return

        welcome_role = guild.get_role(constants.new_member_role)
        if welcome_role is None:
            return

        channel = guild.get_channel(constants.general_channel_id) or guild.system_channel
        if channel:
            try:
                await channel.send(
                    content=f"Hi {member.mention}! Welcome to our server.",
                    delete_after=80,
                )
            except discord.Forbidden:
                pass

        try:
            await member.add_roles(welcome_role, reason="Welcome role added")
            await self.manager.schedule_removal(
                guild_id=guild.id,
                user_id=member.id,
                role_id=welcome_role.id,
                days=WELCOME_ROLE_DURATION_DAYS,
            )
        except discord.Forbidden:
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
                    f"Introduce yourself in <#{constants.general_channel_id}>\n\n"
                    f"Leetcode discussion <#{constants.leetcode_channel_id}>\n\n"
                    f"For **Leetcode challenges** checkout <#{constants.challenges_channel_id}>\n\n\n"
                    + content_footer
                ),
                color=discord.Color.green(),
            )
            dm_embed.set_footer(
                text="Tortoise Programming Community",
                icon_url="https://lairesit.sirv.com/Images/tortoise.png",
            )
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        if guild is None or guild.id != constants.tortoise_guild_id:
            return

        channel = guild.get_channel(constants.system_log_channel_id)
        if channel is None:
            return
        try:
            await channel.send(
                content=(
                    f"👋 **Member Left**\n"
                    f"User: **{member.name}** (`{member.id}`)\n"
                    f"Joined server: <t:{int(member.joined_at.timestamp())}:R>\n"
                    f"Account created: <t:{int(member.created_at.timestamp())}:R>"
                )
            )
        except discord.Forbidden:
            pass


    @tasks.loop(hours=6)
    async def remove_welcome_roles(self):
        removals = await self.manager.get_due_removals()

        for guild_id, user_id, role_id in removals:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            member = guild.get_member(user_id)
            role = guild.get_role(role_id)

            if member and role:
                try:
                    await member.remove_roles(role, reason="Welcome role expired")
                except discord.Forbidden:
                    pass
                except Exception:
                    pass

            await self.manager.delete_entry(guild_id, user_id, role_id)

    @remove_welcome_roles.before_loop
    async def before_remove_welcome_roles(self):
        await self.bot.wait_until_ready()
        await self.manager.setup()


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
