from datetime import datetime, timedelta
import asyncpg


class Database:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def close(self):
        if self.pool:
            await self.pool.close()


class BanLimitManager:
    def __init__(self, db: Database, max_bans: int = 3, hours: int = 24):
        self.db = db
        self.max_bans = max_bans
        self.hours = hours

    async def setup(self):
        await self.db.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS ban_records (
                user_id   BIGINT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL
            )
            """
        )

    async def try_ban(self, user_id: int) -> bool:
        now = datetime.utcnow()
        limit_time = now - timedelta(hours=self.hours)

        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM ban_records WHERE timestamp < $1",
                    limit_time,
                )

                count = await conn.fetchval(
                    "SELECT COUNT(*) FROM ban_records WHERE user_id = $1",
                    user_id,
                )

                if count >= self.max_bans:
                    return False

                await conn.execute(
                    """
                    INSERT INTO ban_records (user_id, timestamp)
                    VALUES ($1, $2)
                    """,
                    user_id,
                    now,
                )

        return True


class PointsManager:
    def __init__(self, db: Database):
        self.db = db

    async def setup(self):
        await self.db.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS points (
                guild_id BIGINT NOT NULL,
                user_id  BIGINT NOT NULL,
                points   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

    async def add_points(self, guild_id: int, user_id: int, amount: int) -> int:
        row = await self.db.pool.fetchrow(
            """
            INSERT INTO points (guild_id, user_id, points)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id, user_id)
            DO UPDATE SET points = points.points + EXCLUDED.points
            RETURNING points
            """,
            guild_id,
            user_id,
            amount,
        )
        return row["points"]

    async def remove_points(self, guild_id: int, user_id: int, amount: int) -> int:
        row = await self.db.pool.fetchrow(
            """
            INSERT INTO points (guild_id, user_id, points)
            VALUES ($1, $2, 0)
            ON CONFLICT (guild_id, user_id)
            DO UPDATE
            SET points = GREATEST(points.points - $3, 0)
            RETURNING points
            """,
            guild_id,
            user_id,
            amount,
        )
        return row["points"]

    async def get_points(self, guild_id: int, user_id: int) -> int:
        return await self.db.pool.fetchval(
            "SELECT points FROM points WHERE guild_id = $1 AND user_id = $2",
            guild_id,
            user_id,
        ) or 0

    async def get_leaderboard(self, guild_id: int, min_points: int = 1, limit: int = 10):
        rows = await self.db.pool.fetch(
            """
            SELECT user_id, points
            FROM points
            WHERE guild_id = $1 AND points >= $2
            ORDER BY points DESC
            LIMIT $3
            """,
            guild_id,
            min_points,
            limit,
        )
        return [(r["user_id"], r["points"]) for r in rows]



class WelcomeRoleManager:
    def __init__(self, db: Database):
        self.db = db

    async def setup(self):
        await self.db.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS welcome_roles (
                guild_id BIGINT NOT NULL,
                user_id  BIGINT NOT NULL,
                role_id  BIGINT NOT NULL,
                remove_at TIMESTAMPTZ NOT NULL,
                PRIMARY KEY (guild_id, user_id, role_id)
            )
            """
        )

    async def schedule_removal(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        days: int = 7,
    ):
        remove_at = datetime.utcnow() + timedelta(days=days)

        await self.db.pool.execute(
            """
            INSERT INTO welcome_roles (guild_id, user_id, role_id, remove_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, user_id, role_id)
            DO UPDATE SET remove_at = EXCLUDED.remove_at
            """,
            guild_id,
            user_id,
            role_id,
            remove_at,
        )

    async def get_due_removals(self):
        rows = await self.db.pool.fetch(
            """
            SELECT guild_id, user_id, role_id
            FROM welcome_roles
            WHERE remove_at <= NOW()
            """
        )
        return [(r["guild_id"], r["user_id"], r["role_id"]) for r in rows]

    async def delete_entry(self, guild_id: int, user_id: int, role_id: int):
        await self.db.pool.execute(
            """
            DELETE FROM welcome_roles
            WHERE guild_id = $1 AND user_id = $2 AND role_id = $3
            """,
            guild_id,
            user_id,
            role_id,
        )
