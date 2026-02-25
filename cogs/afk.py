from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands, tasks
from discord import app_commands


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = bot.afk_manager
        self.cleanup_expired.start()

    def cog_unload(self):
        self.cleanup_expired.cancel()


    @app_commands.command(name="setafk", description="Set AFK status.")
    async def setafk(
        self,
        interaction: discord.Interaction,
        hours: Optional[int] = None,
        days: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Server only command.", ephemeral=True
            )
            return

        if not hours and not days:
            await interaction.response.send_message(
                "Provide hours or days.", ephemeral=True
            )
            return

        total = timedelta(hours=hours or 0, days=days or 0)
        until = datetime.now(timezone.utc) + total

        await self.manager.set_afk(
            interaction.guild.id,
            interaction.user.id,
            until,
            reason,
        )

        embed = discord.Embed(
            title="AFK Enabled",
            description=f"You are AFK for {total}.",
            color=0xffb101,
        )

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        afk = await self.manager.get_afk(message.guild.id, message.author.id)
        if afk:
            await self.manager.remove_afk(message.guild.id, message.author.id)
            await message.channel.send(
                embed=discord.Embed(
                    title="",
                    description=f"{message.author.mention} is no longer afk",
                    color=0xffb101,
                )
            )

        mentioned_users = set(message.mentions)

        if message.reference:
            ref = message.reference.resolved
            if isinstance(ref, discord.Message):
                mentioned_users.add(ref.author)

        for member in mentioned_users:
            if member.bot:
                continue

            data = await self.manager.get_afk(message.guild.id, member.id)
            if not data:
                continue

            reason = data["reason"]
            until = data["until"]

            remaining = until - datetime.now(timezone.utc)
            if remaining.total_seconds() <= 0:
                await self.manager.remove_afk(message.guild.id, member.id)
                continue

            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            days, hours = divmod(hours, 24)

            time_str = []
            if days:
                time_str.append(f"{days}d")
            if hours:
                time_str.append(f"{hours}h")

            embed = discord.Embed(
                description=f"{member.mention} is AFK for {' '.join(time_str)}.",
                color=0xffb101,
            )

            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            await message.channel.send(embed=embed)


    @tasks.loop(minutes=10)
    async def cleanup_expired(self):
        expired = await self.manager.get_expired()
        for guild_id, user_id in expired:
            await self.manager.remove_afk(guild_id, user_id)

    @cleanup_expired.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))