# Snappy Discord Bot

Snappy is a lightweight, open-source Discord bot built using **discord.py v2+** and modern Discord application commands.

Historically, the Tortoise Community operated a much more advanced bot, **[Tortoise-Bot](https://github.com/Tortoise-Commuinity/Tortoise-Bot)**, which was tightly integrated with our website through a custom REST API. That bot provided a broader feature set and deeper web-backed interactions. However, due to significant technical debt including the need to migrate from **discord.py v1 to v2** and to rework the associated web backend, Tortoise-Bot is currently inactive and requires substantial refactoring before it can be brought back online.

Snappy exists to fill that gap. It provides the **essential moderation and community functionality** required today, using a clean, modern architecture. Once Tortoise-Bot is restored in the future, Snappy will continue to be maintained as a **dedicated events and utility bot** alongside it.

---

## What Snappy Currently Does

### Moderation

* Slash-command based moderation commands
* Per-moderator ban rate limiting
* Welcome messages and leave logging
* Temporary welcome roles with automatic removal
* DM restrictions for bot commands

### Community Tools

* Points system with server-specific leaderboards
* Manual point awarding and removal (moderator-only)
* User point lookup
* Role-based notification opt-ins using buttons



## Setup Overview

### Requirements

* Python 3.11+
* PostgreSQL
* A Discord application with slash commands enabled

### Environment Variables

```env
DISCORD_BOT_TOKEN=your_bot_token
DB_URL=postgresql://user:password@host:port/database
HOST=0.0.0.0
PORT=8080
```

### Running the Bot

```bash
python bot.py
```

On startup, the bot will:

* Connect to the database
* Initialize required tables
* Load all cogs
* Sync slash commands to the configured guild
* 
---

## Health Check Endpoints

The bot exposes an internal HTTP server for monitoring:

* `GET /health` — runtime and resource statistics
* `GET /ready` — readiness probe

Requests are rate-limited to prevent abuse.
These endpoints are intended for internal monitoring, Docker health checks, or orchestration systems.

---

### Database Note

Earlier versions of the project used SQLite for persistence.
The bot has since **fully migrated to PostgreSQL** to improve concurrency handling, reliability, and long-term scalability.

SQLite is no longer used anywhere in the codebase.

---

## Contributor Guidelines

This project is open to contributors and community improvements. Please refer [CONTRIBUTING.md](/CONTRIBUTING.md)

### Important Notes

* This is **not a paid project**
* Contributions are voluntary
* The bot is fully open source
* Active contributors will receive `@Contributor` role in the community

If you plan a larger refactor or feature addition, open an issue first to discuss scope.

---

## License

This project is licensed under the **MIT License**.

## Status

Snappy is actively maintained and production-ready for its current scope.
It is intentionally minimal by design and will continue to coexist with Tortoise-Bot once the latter is restored.
