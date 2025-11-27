import os
import aiohttp
from typing import Any, Dict, Optional
from decouple import config

class AdventOfCodeAPI:
    """
    Standalone Advent of Code private leaderboard client.

    Usage:
        api = AdventOfCodeAPI(leaderboard_id="123456", year=2025)
        data = await api.get_leaderboard()
    """

    BASE_URL = "https://adventofcode.com/{year}/leaderboard/private/view/{leaderboard_id}.json"
    DEFAULT_USER_AGENT = "Tortoise Discord Community AoC bot (github: your-repo-or-contact)"

    def __init__(
        self,
        leaderboard_id: str,
        year: int,
        session_cookie: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        :param leaderboard_id: Your private leaderboard ID (numeric string).
        :param year: AoC year, e.g. 2025.
        :param session_cookie: AoC session cookie (if None, taken from env AOC_COOKIE).
        :param user_agent: Custom user-agent string for requests.
        """
        self.leaderboard_id = leaderboard_id
        self.year = year
        self.session_cookie = session_cookie or config("AOC_COOKIE")
        if not self.session_cookie:
            raise ValueError(
                "AdventOfCodeAPI: session cookie is missing. "
                "Pass session_cookie=... or set the AOC_COOKIE environment variable."
            )

        self.user_agent = user_agent or self.DEFAULT_USER_AGENT

        self.url = self.BASE_URL.format(
            year=self.year,
            leaderboard_id=self.leaderboard_id,
        )

    async def get_leaderboard(self) -> Dict[str, Any]:
        """
        Fetch and return the leaderboard JSON as a dict.

        Raises aiohttp.ClientResponseError for HTTP errors
        or aiohttp.ClientError for network issues.
        """
        headers = {"User-Agent": self.user_agent}
        cookies = {"session": self.session_cookie}

        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            async with session.get(self.url) as resp:
                resp.raise_for_status()  # raises if not 2xx
                data = await resp.json()
                return data
