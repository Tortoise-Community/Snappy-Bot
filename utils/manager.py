import aiosqlite
from datetime import datetime

class BanLimitManager:
    def __init__(self, db_path: str = "data/ban_limits.db", max_bans: int = 3, hours: int = 24):
        self.db_path = db_path
        self.max_bans = max_bans
        self.hours = hours

    # Create the DB table (call once at startup)
    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ban_records (
                    user_id INTEGER,
                    timestamp REAL
                )
            """)
            print("DB setup")
            await db.commit()

    # Check if a moderator can ban & record if allowed
    async def try_ban(self, user_id: int) -> bool:
        """
        Returns True if moderator can ban, and records the ban.
        Returns False if moderator reached limit.
        """
        now = datetime.utcnow().timestamp()
        limit_time = now - (self.hours * 3600)

        async with aiosqlite.connect(self.db_path) as db:
            # Remove expired ban records
            await db.execute(
                "DELETE FROM ban_records WHERE timestamp < ?", (limit_time,)
            )

            # Count remaining records within time period
            async with db.execute(
                "SELECT COUNT(*) FROM ban_records WHERE user_id = ?", (user_id,)
            ) as cursor:
                (count,) = await cursor.fetchone()

            # Reached maximum limit
            if count >= self.max_bans:
                return False

            # Record this ban
            await db.execute(
                "INSERT INTO ban_records (user_id, timestamp) VALUES (?, ?)",
                (user_id, now)
            )
            await db.commit()

        return True


class PointsManager:
    """SQLite-backed points manager (for leaderboards, etc.)."""

    def __init__(self, db_path: str = "data/ban_limits.db"):
        # You can keep the same db_path so both managers share one file,
        # or pass a different db_path when creating this.
        self.db_path = db_path

    async def setup(self):
        """Initialize the points table."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS points (
                    guild_id INTEGER NOT NULL,
                    user_id  INTEGER NOT NULL,
                    points   INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, user_id)
                )
                """
            )
            print("PointsManager DB setup")
            await db.commit()

    async def add_points(self, guild_id: int, user_id: int, amount: int) -> int:
        """
        Add points to a user and return the new total.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Upsert row: insert or update
            await db.execute(
                """
                INSERT INTO points (guild_id, user_id, points)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id, user_id)
                DO UPDATE SET points = points + excluded.points
                """,
                (guild_id, user_id, amount),
            )
            await db.commit()

            # Fetch new total
            async with db.execute(
                "SELECT points FROM points WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def remove_points(self, guild_id: int, user_id: int, amount: int) -> int:
        """
        Remove points from a user and return the new total.
        Points will not go below 0.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Decrease points; ensure row exists
            await db.execute(
                """
                INSERT INTO points (guild_id, user_id, points)
                VALUES (?, ?, 0)
                ON CONFLICT(guild_id, user_id)
                DO NOTHING
                """,
                (guild_id, user_id),
            )

            # Subtract points (temporary negative allowed)
            await db.execute(
                """
                UPDATE points
                SET points = points - ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (amount, guild_id, user_id),
            )

            # Clamp to 0
            await db.execute(
                """
                UPDATE points
                SET points = 0
                WHERE guild_id = ? AND user_id = ? AND points < 0
                """,
                (guild_id, user_id),
            )

            await db.commit()

            # Fetch updated total
            async with db.execute(
                    "SELECT points FROM points WHERE guild_id = ? AND user_id = ?",
                    (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_points(self, guild_id: int, user_id: int) -> int:
        """Get current points of a user."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT points FROM points WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_leaderboard(self, guild_id: int, min_points: int = 1, limit: int = 10):
        """
        Get a list of (user_id, points) sorted by points desc.
        Only users with points >= min_points.
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT user_id, points
                FROM points
                WHERE guild_id = ? AND points >= ?
                ORDER BY points DESC
                LIMIT ?
                """,
                (guild_id, min_points, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [(row[0], row[1]) for row in rows]