from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

import constants


class Moderation(commands.Cog):
    """This cog is to be removed after Tortoise bot is back online"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ban",
        description="Ban a member from the server.",
    )
    @app_commands.checks.has_role(constants.moderator_role)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = None
    ):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        author = interaction.user

        if guild is None:
            await interaction.followup.send("This command can only be used in a server.")
            return

        # Safety checks
        if member == author:
            await interaction.followup.send("You can't ban yourself.")
            return

        if member == guild.owner:
            await interaction.followup.send("You can't ban the server owner.")
            return

        if isinstance(author, discord.Member):
            if member.top_role >= author.top_role and author != guild.owner:
                await interaction.followup.send(
                    "You can't ban someone with an equal or higher role than you."
                )
                return

        # Try DMing
        if not await self.bot.ban_manager.try_ban(author.id):
            await interaction.followup.send(
                "You have reached the maximum ban limit for 24 hours.",
                ephemeral=True
            )
            return
        try:
            dm_text = f"You were banned from **{guild.name}**."
            if reason:
                dm_text += f"\nReason: {reason}"
            await member.send(dm_text)
        except:
            pass

        try:
            await guild.ban(member, reason=reason)
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to ban that member.")
            return
        except Exception as e:
            await interaction.followup.send(f"Unexpected error: {e}")
            return

        await interaction.followup.send(
            f":incoming_envelope:  **{member.mention} has been banned.** "
            f"{'(Reason: ' + reason + ')' if reason else ''}",
        )

    @ban.error
    async def ban_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                "You don't have permission to ban members.",
                ephemeral=True,
            )
            return

        # Avoid raising the error; send a simple message instead
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Error: {error}", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"Error: {error}", ephemeral=True
                )
        except:
            pass  # Discord interaction already closed


async def setup(bot):
    await bot.add_cog(Moderation(bot))
