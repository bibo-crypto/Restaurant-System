from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "restaurant.sqlite"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, json TEXT NOT NULL)"
    )
    return conn


def load_state(db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT json FROM app_state WHERE key = ?", ("state",)
        ).fetchone()
        if not row:
            return None
        return json.loads(row[0])
    finally:
        conn.close()


def save_state(state: dict[str, Any], db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO app_state(key, json) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET json = excluded.json",
            ("state", json.dumps(state, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()

