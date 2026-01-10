import asyncio
import discord
from decouple import config
from discord.ext import commands

from utils.manager import (
    BanLimitManager,
    PointsManager,
    WelcomeRoleManager,
    Database,
)

TOKEN = config("DISCORD_BOT_TOKEN")
DB_URL = config("DB_URL")
GUILD_ID = 577192344529404154


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self) -> None:
        self.db = Database(DB_URL)
        await self.db.connect()

        self.ban_manager = BanLimitManager(self.db)
        self.points_manager = PointsManager(self.db)
        self.welcome_role_manager = WelcomeRoleManager(self.db)

        await self.ban_manager.setup()
        await self.points_manager.setup()
        await self.welcome_role_manager.setup()

        # ---------- COGS ----------
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.leaderboard")
        await self.load_extension("cogs.challenge_notifications")
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.status")

        await self.tree.sync()
        print("✅ Synced application commands")


bot = MyBot()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")


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
