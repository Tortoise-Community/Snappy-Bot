import asyncio

import discord
from decouple import config
from discord.ext import commands

from utils.manager import BanLimitManager, PointsManager

TOKEN = config("DISCORD_BOT_TOKEN")
GUILD_ID = 577192344529404154


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=None,
        )
        self.ban_manager = BanLimitManager()
        self.leaderboard_manager = PointsManager()



    async def setup_hook(self) -> None:
        # Load cogs/extensions here
        await self.ban_manager.setup()
        await self.leaderboard_manager.setup()
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.leaderboard")
        await self.load_extension("cogs.challenge_notifications")
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.status")
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync()
        print("Synced application commands.")


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.guild is None:
        try:
            await message.channel.send(
                "🚫 Commands are disabled in DMs. Please use me in a server."
            )
        except discord.Forbidden:
            pass
        return
    await bot.process_commands(message)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
