from __future__ import annotations

import os
import time
import platform
from datetime import datetime, timedelta
from typing import Dict

import psutil
import discord
from discord.ext import commands
from aiohttp import web
from decouple import config

import constants


class HealthCheck(commands.Cog):
    """
    Exposes health endpoints for monitoring the bot.
    """

    def __init__(
        self,
        bot: commands.Bot,
        host: str = "0.0.0.0",
        port: int = "8080",
    ):
        self.bot = bot
        self.host = host
        self.port = port

        self.start_time = time.time()

        self.rate_limit_window = timedelta(minutes=constants.rate_limit_minutes)
        self.client_last_seen: Dict[str, datetime] = {}

        self.app = web.Application()
        self.app.add_routes(
            [
                web.get("/health", self.health),
                web.head("/ready", self.ready),
            ]
        )

        self.runner: web.AppRunner | None = None
        self.site: web.TCPSite | None = None

        self.bot.loop.create_task(self._start_server())


    def _is_rate_limited(self, request: web.Request) -> bool:
        # Support reverse proxies
        client_ip = (
            request.headers.get("X-Forwarded-For", request.remote)
            or "unknown"
        )
        # If multiple IPs are present, take the first
        client_ip = client_ip.split(",")[0].strip()

        now = datetime.utcnow()
        last_seen = self.client_last_seen.get(client_ip)

        if last_seen and (now - last_seen) < self.rate_limit_window:
            return True

        self.client_last_seen[client_ip] = now
        return False


    async def health(self, request: web.Request) -> web.Response:
        if self._is_rate_limited(request):
            return web.json_response(
                {
                    "status": "rate_limited",
                    "retry_after_minutes": constants.rate_limit_minutes,
                },
                status=429,
            )

        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024

        data = {
            "status": "ok",
            "uptime_seconds": int(time.time() - self.start_time),
            "latency_ms": round(self.bot.latency * 1000, 2),
            "guilds": len(self.bot.guilds),
            "users": sum(g.member_count or 0 for g in self.bot.guilds),
            "python_version": platform.python_version(),
            "discord_py_version": discord.__version__,
            "memory_mb": round(mem_mb, 2),
            "pid": os.getpid(),
        }

        return web.json_response(data)

    async def ready(self, request: web.Request) -> web.Response:
        if self._is_rate_limited(request):
            return web.Response(text="RATE LIMITED", status=429)

        if self.bot.is_ready():
            return web.Response(text="READY", status=200)

        return web.Response(text="NOT READY", status=503)


    async def _start_server(self):
        await self.bot.wait_until_ready()

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        print(f"Health check server running on http://{self.host}:{self.port}")

    async def cog_unload(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()


async def setup(bot: commands.Bot):
    host = config("HOST", "0.0.0.0")
    port = config("PORT", "8080", cast=int)

    await bot.add_cog(HealthCheck(bot, host=host, port=port))
