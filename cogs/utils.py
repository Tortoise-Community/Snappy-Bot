from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands
from constants import RULES


ALIAS_MAP = {}
for num, rule in RULES.items():
    for alias in rule["aliases"]:
        ALIAS_MAP[alias.lower()] = num


class Utils(commands.Cog):
    """Utility commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rules",
        description="Show all rules or a specific rule using alias"
    )
    @app_commands.describe(alias="Optional rule alias (e.g. dm, nsfw, ping, tos)")
    async def rules(self, interaction: discord.Interaction, alias: str | None = None):

        if alias:
            key = alias.lower().strip()
            rule_num = ALIAS_MAP.get(key)

            if not rule_num:
                await interaction.response.send_message(
                    f"❌ Unknown rule alias: `{alias}`",
                    ephemeral=True
                )
                return

            rule = RULES[rule_num]

            embed = discord.Embed(
                title=f"Rule {rule_num}: {rule['title']}",
                color=discord.Color.dark_grey()
            )

            embed.description = (
                f"{rule['text']}\n"
            )
            embed.set_footer(text=f"Aliases: [{', '.join(rule['aliases'])}]")
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title="Tortoise - Programming Community Rules",
            color=discord.Color.dark_grey()
        )

        blocks = []
        for num in sorted(RULES.keys()):
            rule = RULES[num]
            block = (
                f"**{num}. {rule['title']}**"
                f"{rule['text']}\n"
                f"[aliases: {', '.join(rule['aliases'])}]"
            )
            blocks.append(block)

        embed.description = "\n\n".join(blocks) + "\n\n"
        embed.set_footer(text="Tortoise Community")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
