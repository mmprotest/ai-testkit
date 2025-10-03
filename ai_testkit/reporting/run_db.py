"""SQLite run registry."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class RunDatabase:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path.home() / ".ait" / "runs.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self._init()

    def _init(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suite TEXT,
                pass_rate REAL,
                total_cost REAL,
                avg_latency REAL,
                timestamp TEXT
            )
            """
        )
        self.conn.commit()

    def record(self, suite: str, pass_rate: float, total_cost: float, avg_latency: float, timestamp: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO runs (suite, pass_rate, total_cost, avg_latency, timestamp) VALUES (?, ?, ?, ?, ?)",
            (suite, pass_rate, total_cost, avg_latency, timestamp),
        )
        self.conn.commit()

    def fetch(self, suite: str) -> Iterable[tuple]:
        cur = self.conn.cursor()
        cur.execute("SELECT suite, pass_rate, total_cost, avg_latency, timestamp FROM runs WHERE suite=?", (suite,))
        return cur.fetchall()

