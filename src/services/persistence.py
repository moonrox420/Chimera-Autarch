"""
Persistence service for database operations.
"""

import asyncio
import aiosqlite
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import PersistenceSettings
from core.logging import get_logger

logger = get_logger(__name__)


class PersistenceService:
    """Handles all database operations."""

    def __init__(self, settings: PersistenceSettings):
        self.settings = settings
        self.db_path = Path(settings.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize database connection and schema."""
        self._connection = await aiosqlite.connect(str(self.db_path))

        # Create tables
        await self._create_tables()

        logger.info(f"Database initialized at {self.db_path}")

    async def shutdown(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _create_tables(self) -> None:
        """Create database schema."""
        if not self._connection:
            return

        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS evolutions (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                failure_reason TEXT,
                applied_fix TEXT,
                observed_improvement REAL,
                timestamp REAL,
                validation_metrics TEXT
            );

            CREATE TABLE IF NOT EXISTS tool_metrics (
                tool_name TEXT,
                timestamp REAL,
                success BOOLEAN,
                latency REAL,
                context TEXT
            );

            CREATE TABLE IF NOT EXISTS node_metrics (
                node_id TEXT,
                timestamp REAL,
                status TEXT,
                reputation REAL,
                resources TEXT
            );
        """)

        await self._connection.commit()

    async def log_evolution(self, evolution: Dict[str, Any]) -> None:
        """Log an evolution record."""
        if not self._connection:
            return

        await self._connection.execute(
            """
            INSERT INTO evolutions VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evolution["id"],
                evolution["topic"],
                evolution.get("failure_reason"),
                evolution.get("applied_fix"),
                evolution.get("observed_improvement", 0.0),
                evolution["timestamp"],
                json.dumps(evolution.get("validation_metrics", {})),
            ),
        )
        await self._connection.commit()

    async def log_tool_metric(
        self,
        tool_name: str,
        success: bool,
        latency: float,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log tool execution metrics."""
        if not self._connection:
            return

        await self._connection.execute(
            """
            INSERT INTO tool_metrics VALUES (?, ?, ?, ?, ?)
            """,
            (
                tool_name,
                time.time(),
                success,
                latency,
                json.dumps(context or {}),
            ),
        )
        await self._connection.commit()

    async def get_evolution_history(self, topic: Optional[str] = None, limit: int = 100) -> list:
        """Get evolution history."""
        if not self._connection:
            return []

        if topic:
            cursor = await self._connection.execute(
                "SELECT * FROM evolutions WHERE topic = ? ORDER BY timestamp DESC LIMIT ?",
                (topic, limit)
            )
        else:
            cursor = await self._connection.execute(
                "SELECT * FROM evolutions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def backup_loop(self) -> None:
        """Background task for automatic backups."""
        while True:
            try:
                await asyncio.sleep(self.settings.backup_interval)
                await self._create_backup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Backup error: {e}")

    async def _create_backup(self) -> None:
        """Create database backup."""
        if not self._connection:
            return

        backup_dir = Path(self.settings.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())
        backup_path = backup_dir / f"chimera_backup_{timestamp}.db"

        # SQLite backup
        await self._connection.backup(backup_path)

        # Clean old backups
        await self._cleanup_old_backups()

        logger.info(f"Database backup created: {backup_path}")

    async def _cleanup_old_backups(self) -> None:
        """Remove old backups beyond retention limit."""
        backup_dir = Path(self.settings.backup_dir)
        if not backup_dir.exists():
            return

        backups = sorted(backup_dir.glob("chimera_backup_*.db"))
        if len(backups) > self.settings.backup_retention:
            to_remove = backups[:-self.settings.backup_retention]
            for backup in to_remove:
                backup.unlink()
                logger.debug(f"Removed old backup: {backup}")