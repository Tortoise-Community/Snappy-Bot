# bot.py
import asyncio
import os

import discord
from discord.ext import commands
from decouple import config
from utils.manager import BanLimitManager, PointsManager

TOKEN = config("DISCORD_BOT_TOKEN")
GUILD_ID = 577192344529404154

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # needed for member info / bans
        super().__init__(
            command_prefix="!",  # prefix is optional now, mainly for owner/debug commands
            intents=intents,
            application_id=None,  # can set your app ID here if you want
        )
        self.ban_manager = BanLimitManager()
        self.leaderboard_manager = PointsManager()


    async def setup_hook(self) -> None:
        # Load cogs/extensions here
        await self.ban_manager.setup()
        await self.leaderboard_manager.setup()
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.leaderboard")
        await self.load_extension("cogs.advent_of_code")
        await self.load_extension("cogs.welcome")
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync()
        print("Synced application commands.")


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="watching Tortoise Community"
    ))


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
