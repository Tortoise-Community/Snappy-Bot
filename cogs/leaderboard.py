from __future__ import annotations

from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands


class Leaderboard(commands.Cog):
    """Simple points leaderboard using SQLite PointsManager."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = self.bot.leaderboard_manager

    # ------------- commands -------------

    @app_commands.command(
        name="rmpoints",
        description="Remove points from a user (mods only).",
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def rmpoints(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        new_total = await self.manager.remove_points(
            interaction.guild.id, member.id, amount
        )

        desc = (
            f"**{amount}** points have been removed from **{member.mention}**\n"
            f"New total: **{new_total}** points."
        )

        embed = discord.Embed(
            title="Points Removed ❎",
            description=desc,
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)



    @app_commands.command(
        name="addpoints",
        description="Give points to a user (mods only).",
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def addpoints(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
        reason: Optional[str] = None,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        new_total = await self.manager.add_points(
            interaction.guild.id, member.id, amount
        )

        desc = (
            f"**{member.mention}** has been given **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )

        dm_desc = (
            f"You were awarded **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )

        if reason:
            desc += f"\n**Comment:** {reason}"
            dm_desc += f"\n\n**Comment:** {reason}"

        embed = discord.Embed(
            title="Points Awarded ✅",
            description=desc,
            color=discord.Color.green(),
        )

        dm_embed = discord.Embed(
            title="Congratulations :star2:",
            description=dm_desc,
            color=discord.Color.green(),
        )

        embed.set_footer(text=f"Given by {interaction.user.display_name}")
        dm_embed.set_footer(text=f"Great job! 💠 Tortoise Community")

        await member.send(embed=dm_embed);
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @addpoints.error
    async def addpoints_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True,
            )
            return

        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred while running this command.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "An error occurred while running this command.",
                ephemeral=True,
            )
        raise error

    @app_commands.command(
        name="leaderboard",
        description="Show the points leaderboard for this server.",
    )
    async def leaderboard(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        entries = await self.manager.get_leaderboard(
            guild.id,
            min_points=1,
            limit=10,
        )

        if not entries:
            await interaction.response.send_message(
                "No one has any points yet. Start awarding some with `/addpoints`!",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"🏆 {guild.name} Leaderboard",
            description="Top users by points:",
            color=discord.Color.gold(),
        )

        rank_emojis = ["🥇", "🥈", "🥉"]

        for index, (user_id, points) in enumerate(entries, start=1):
            member = guild.get_member(user_id)
            name = member.mention if member else f"<@{user_id}>"

            if index <= len(rank_emojis):
                rank_label = rank_emojis[index - 1]
            else:
                rank_label = f"#{index}"

            embed.add_field(
                value=f"{rank_label} {name}",
                name=f"**{points}** points",
                inline=False,
            )

        embed.set_footer(text="Only users with > 0 points are shown.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="points",
        description="Check your points or another member's points.",
    )
    async def points(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        target = member or interaction.user
        pts = await self.manager.get_points(interaction.guild.id, target.id)

        embed = discord.Embed(
            title="📊 Points",
            description=f"**{target.mention}** has **{pts}** points.",
            color=discord.Color.blurple(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))

