from __future__ import annotations
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands
from constants import challenges_channel_id


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = bot.points_manager

    @staticmethod
    def build_challenge_embed():
        return discord.Embed(
            title="Challenge Guidelines",
            description=(
                "Participants who submit a valid working solution will be awarded points "
                "and featured on the leaderboard.\n\n"

                "**Guidelines:**\n"
                "- Start with a brute force approach if needed, then optimize for time and space complexity.\n"
                "- Do not use AI assistance.\n"
                "- Discussions are allowed in <#781129674860003336>, but do not share full solutions.\n"
                "- Any programming language is allowed.\n\n"

                "**Complexity Target:**\n"
                "- Aim for O(N) time and O(N) space or the best achievable complexity.\n"
                "- All valid submissions receive 100 points.\n"
                "- Optimal solutions receive an additional 50 points.\n"
                "- Special challenges award 150 points, with 50 bonus points for optimal solutions (200 total).\n\n"

                "**Submission Rules:**\n"
                "- Post solutions in <#780842875901575228>\n"
                "- Use spoiler tags to hide your code when submitting.\n"
                "- You may use <@712323581828136971> to validate your solution.\n"
                "- Use `/run` followed by properly formatted code blocks in <#781129674860003336>.\n"
                "- Delete your code after execution to avoid spoiling solutions.\n"
                "- Use `/run_help` for more information."
            ),
            color=discord.Color.green()
        )

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author.bot:
    #         return
    #
    #     if message.channel == challenges_channel_id:
    #         await message.reply(embed=self.build_challenge_embed(), mention_author=False)


    @app_commands.command(name="challenge_rules", description="Show challenge guidelines")
    async def rules(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.build_challenge_embed())


    @app_commands.command(name="rmpoints", description="Remove points from a user (mods only).")
    @app_commands.checks.has_permissions(ban_members=True)
    async def rmpoints(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        new_total = await self.manager.remove_points(
            interaction.guild.id, member.id, amount
        )

        embed = discord.Embed(
            title="Points Removed ❎",
            description=(
                f"**{amount}** points removed from {member.mention}\n"
                f"New total: **{new_total}** points."
            ),
            color=discord.Color.red(),
        )

        await interaction.followup.send(embed=embed)


    @app_commands.command(name="addpoints", description="Give points to a user (mods only).")
    @app_commands.checks.has_permissions(ban_members=True)
    async def addpoints(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: app_commands.Range[int, 1, 10_000],
        reason: Optional[str] = None,
        silent: bool = False,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        new_total = await self.manager.add_points(
            interaction.guild.id, member.id, amount
        )

        desc = (
            f"{member.mention} received **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )

        dm_desc = (
            f"You were awarded **{amount}** points.\n"
            f"New total: **{new_total}** points."
        )

        if reason:
            desc += f"\n\n**Reason:** {reason}"
            dm_desc += f"\n\n**Reason:** {reason}"

        embed = discord.Embed(
            title="Points Awarded ✅",
            description=desc,
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"Given by {interaction.user.display_name}")
        if not silent:
            embed = discord.Embed(
                title="Congratulations 🌟",
                description=dm_desc,
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Tortoise Community")
            try:
                await member.send(
                    embed=embed,
                )
            except discord.Forbidden:
                pass

        await interaction.followup.send(embed=embed)


    @addpoints.error
    @rmpoints.error
    async def mod_points_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        msg = "An error occurred while running this command."

        if isinstance(error, app_commands.MissingPermissions):
            msg = "You don't have permission to use this command."

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

        raise error


    @app_commands.command(name="leaderboard", description="Show the points leaderboard.")
    async def leaderboard(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        await interaction.response.defer()

        entries = await self.manager.get_leaderboard(
            interaction.guild.id, min_points=1, limit=10
        )

        if not entries:
            await interaction.followup.send(
                "No one has any points yet.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} Leaderboard",
            color=discord.Color.gold(),
        )

        medals = ["🥇", "🥈", "🥉"]

        for idx, (user_id, points) in enumerate(entries, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.mention if member else f"<@{user_id}>"
            rank = medals[idx - 1] if idx <= 3 else f"#{idx}"
            embed.add_field(
                name=f"**{points}** points",
                value=f"{rank} {name}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)


    @app_commands.command(name="points", description="Check points.")
    async def points(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        target = member or interaction.user
        pts = await self.manager.get_points(interaction.guild.id, target.id)

        embed = discord.Embed(
            title="📊 Points",
            description=f"{target.mention} has **{pts}** points.",
            color=discord.Color.blurple(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
