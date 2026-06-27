from __future__ import annotations

import os
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from .db_config import get_config, load_config, _config_dir

DEFAULT_DB_PATH = _config_dir() / "restaurant.sqlite"

# نضمن تحميل الإعدادات من db_config.json مرة واحدة عند استيراد الملف
load_config()


# ─────────────────────────────────────────────────────────
# SQLite backend (محلي أو على مسار شبكة)
# ─────────────────────────────────────────────────────────

def _sqlite_path(db_path: Path) -> Path:
    cfg = get_config()
    custom = cfg.get("sqlite_path", "").strip()
    if custom:
        return Path(custom)
    if db_path.is_file():
        return db_path
    for legacy in _legacy_db_paths():
        if legacy.is_file():
            return legacy
    return db_path


def _legacy_db_paths() -> list[Path]:
    paths: list[Path] = [Path(__file__).resolve().parents[1] / "restaurant.sqlite"]
    if getattr(sys, "frozen", False):
        paths.insert(0, Path(os.path.dirname(sys.executable)) / "restaurant.sqlite")
    return paths


def _write_db_path_file(path: Path) -> None:
    """يكتب مسار ملف قاعدة البيانات في ملف نصي على سطح المكتب — لتسهيل
    نقل المسار لجهاز آخر عند ربط الأجهزة عبر الشبكة. يُكتب مرة واحدة فقط
    عند إنشاء قاعدة البيانات لأول مرة على هذا الجهاز."""
    try:
        from .admin_auth import _desktop_dir
        desktop = _desktop_dir()
        info_path = desktop / "RestaurantManager_DB_PATH.txt"
        with open(info_path, "w", encoding="utf-8") as f:
            f.write("Restaurant Manager — مسار قاعدة البيانات\n")
            f.write("=" * 45 + "\n")
            f.write(f"{path}\n")
            f.write("=" * 45 + "\n")
            f.write(
                "لربط جهاز آخر بنفس قاعدة البيانات هذه عبر الشبكة:\n"
                "1) شارك المجلد الذي يحتوي هذا الملف بصلاحية Read/Write.\n"
                "2) على الجهاز الآخر، افتح شاشة \"إعداد قاعدة البيانات\"،\n"
                "   اختر \"SQLite على الشبكة\"، واكتب المسار بصيغة:\n"
                f"   \\\\اسم_هذا_الجهاز\\اسم_المجلد_المُشارك\\{path.name}\n"
            )
    except Exception:
        pass  # عدم القدرة على الكتابة لسطح المكتب لا يجب أن يوقف البرنامج


def _sqlite_connect(db_path: Path) -> sqlite3.Connection:
    path = _sqlite_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    is_first_time = not path.is_file()
    # timeout أطول لأن أكتر من جهاز ممكن يكتب على نفس ملف الشبكة في نفس الوقت
    conn = sqlite3.connect(str(path), timeout=20)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, json TEXT NOT NULL)"
    )
    if is_first_time:
        _write_db_path_file(path)
    return conn


def _sqlite_load_state() -> dict[str, Any] | None:
    conn = _sqlite_connect(DEFAULT_DB_PATH)
    try:
        row = conn.execute(
            "SELECT json FROM app_state WHERE key = ?", ("state",)
        ).fetchone()
        if not row:
            return None
        return json.loads(row[0])
    finally:
        conn.close()


def _sqlite_save_state(state: dict[str, Any]) -> None:
    conn = _sqlite_connect(DEFAULT_DB_PATH)
    try:
        conn.execute(
            "INSERT INTO app_state(key, json) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET json = excluded.json",
            ("state", json.dumps(state, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────
# MySQL backend (سيرفر مركزي — الأنسب لعدة أجهزة معاً)
# ─────────────────────────────────────────────────────────

def _mysql_connect():
    import mysql.connector
    cfg = get_config()
    conn = mysql.connector.connect(
        host=cfg.get("mysql_host", "localhost"),
        port=int(cfg.get("mysql_port", 3306)),
        database=cfg.get("mysql_database", "restaurant_db"),
        user=cfg.get("mysql_user", ""),
        password=cfg.get("mysql_password", ""),
        charset=cfg.get("mysql_charset", "utf8mb4"),
        connection_timeout=int(cfg.get("mysql_timeout", 10)),
    )
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS app_state ("
        "`key` VARCHAR(50) PRIMARY KEY, "
        "json_data LONGTEXT NOT NULL"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )
    conn.commit()
    return conn


def _mysql_load_state() -> dict[str, Any] | None:
    conn = _mysql_connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT json_data FROM app_state WHERE `key` = %s", ("state",))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])
    finally:
        conn.close()


def _mysql_save_state(state: dict[str, Any]) -> None:
    conn = _mysql_connect()
    try:
        cur = conn.cursor()
        payload = json.dumps(state, ensure_ascii=False)
        cur.execute(
            "INSERT INTO app_state(`key`, json_data) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE json_data = %s",
            ("state", payload, payload),
        )
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────
# الواجهة العامة — نفس الأسماء المستخدمة في app.py (لا تغيير هناك)
# ─────────────────────────────────────────────────────────

def load_state(db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    db_type = get_config().get("db_type", "sqlite_local")
    if db_type == "mysql":
        return _mysql_load_state()
    return _sqlite_load_state()


def save_state(state: dict[str, Any], db_path: Path = DEFAULT_DB_PATH) -> None:
    db_type = get_config().get("db_type", "sqlite_local")
    if db_type == "mysql":
        _mysql_save_state(state)
    else:
        _sqlite_save_state(state)
