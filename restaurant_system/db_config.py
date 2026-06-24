"""
restaurant_system/db_config.py
───────────────────────────────
مدير إعدادات الاتصال بقاعدة البيانات.
يدعم 3 أوضاع:
  1) sqlite_local  : ملف SQLite محلي (جهاز واحد فقط — الوضع الافتراضي)
  2) sqlite_network: ملف SQLite على مسار شبكة مشترك (مسار UNC من نوع server/share)
  3) mysql         : سيرفر MySQL/MariaDB مركزي (الأنسب لعدة أجهزة معاً)

يُحفَظ الإعداد في: <APP_DIR>/db_config.json
"""

import json
import os
import sys
from pathlib import Path


def _config_dir() -> Path:
    """
    مجلد حفظ الإعدادات — دائماً قابل للكتابة وثابت بين التشغيلات.
    نفضّل مجلد بيانات المستخدم حتى لا يضيع الملف مع إعادة البناء أو تغيير مكان البرنامج.
    """
    data_env = os.environ.get("RESTAURANT_DATA_DIR", "").strip()
    if data_env:
        return Path(data_env)
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "RestaurantManager"
    return Path.home() / ".restaurant_manager"


def _config_path() -> Path:
    return _config_dir() / "db_config.json"


def _legacy_config_paths() -> list[Path]:
    """
    مواقع قديمة قد يكون فيها الملف من نسخ سابقة.
    نستخدمها للترحيل مرة واحدة فقط حتى لا يطلب التطبيق الإعداد مرة أخرى.
    """
    paths: list[Path] = [Path(__file__).resolve().parents[1] / "db_config.json"]
    if getattr(sys, "frozen", False):
        paths.insert(0, Path(os.path.dirname(sys.executable)) / "db_config.json")
    return paths


# ── الافتراضي: SQLite محلي ──
_DEFAULTS = {
    "db_type": "sqlite_local",   # "sqlite_local" | "sqlite_network" | "mysql"
    # نميز بين ملف موجود فعلاً وبين إعداد تم اختياره وحفظه من المستخدم
    "setup_completed": False,
    # كلمة مرور المدير — لا قيمة افتراضية ثابتة؛ تُولَّد عشوائياً عند أول تشغيل
    "admin_password_hash": "",
    # SQLite (محلي أو شبكة)
    "sqlite_path": "",           # فارغ = restaurant.sqlite في مجلد البرنامج
    # MySQL / MariaDB
    "mysql_host":     "localhost",
    "mysql_port":     3306,
    "mysql_database": "restaurant_db",
    "mysql_user":     "restaurant_user",
    "mysql_password": "",
    "mysql_charset":  "utf8mb4",
    "mysql_timeout":  10,
}

_config: dict = dict(_DEFAULTS)
_loaded = False


def load_config() -> dict:
    """يحمّل الإعدادات من الملف — يُستدعى مرة عند بدء البرنامج."""
    global _config, _loaded
    p = _config_path()
    if p.is_file():
        try:
            with open(p, "r", encoding="utf-8") as f:
                saved = json.load(f)
            _config = {**_DEFAULTS, **saved}
        except Exception:
            _config = dict(_DEFAULTS)
    else:
        migrated = False
        for legacy_path in _legacy_config_paths():
            if legacy_path.is_file():
                try:
                    with open(legacy_path, "r", encoding="utf-8") as f:
                        saved = json.load(f)
                    _config = {**_DEFAULTS, **saved}
                    migrated = True
                    break
                except Exception:
                    _config = dict(_DEFAULTS)
        if migrated:
            try:
                save_config(_config)
            except Exception:
                pass
        else:
            _config = dict(_DEFAULTS)
    _loaded = True
    return _config


def save_config(data: dict):
    """يحفظ الإعدادات مع تشفير كلمة مرور MySQL إن وُجدت أداة تشفير."""
    global _config, _loaded
    _config = {**_DEFAULTS, **data}
    _loaded = True
    p = _config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    to_save = dict(_config)
    if to_save.get("mysql_password"):
        try:
            from .crypto import encrypt, is_encrypted
            pw = to_save["mysql_password"]
            if not is_encrypted(pw):
                to_save["mysql_password"] = encrypt(pw)
        except Exception:
            pass
    with open(p, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)


def get_config() -> dict:
    """يرجع الإعدادات مع فك تشفير كلمة المرور."""
    if not _loaded:
        load_config()
    cfg = dict(_config)
    if cfg.get("mysql_password"):
        try:
            from .crypto import decrypt, is_encrypted
            pw = cfg["mysql_password"]
            if is_encrypted(pw):
                cfg["mysql_password"] = decrypt(pw)
        except Exception:
            pass
    return cfg


def get_db_type() -> str:
    return get_config().get("db_type", "sqlite_local")


def test_connection(config: dict) -> tuple[bool, str]:
    """
    يختبر الاتصال بقاعدة البيانات قبل الحفظ.
    Returns: (success: bool, message: str)
    """
    db_type = config.get("db_type", "sqlite_local")

    if db_type in ("sqlite_local", "sqlite_network"):
        path = config.get("sqlite_path", "").strip()
        if not path:
            return True, "✅ SQLite محلي (مسار افتراضي) — لا حاجة لاختبار"
        try:
            import sqlite3
            if path.startswith("\\\\") or path.startswith("//"):
                parent = os.path.dirname(path)
                if not os.path.exists(parent):
                    return False, f"❌ لا يمكن الوصول إلى مجلد الشبكة: {parent}"
            conn = sqlite3.connect(path, timeout=5)
            conn.execute("SELECT 1")
            conn.close()
            return True, f"✅ تم الاتصال بـ SQLite: {path}"
        except Exception as e:
            return False, f"❌ فشل الاتصال: {e}"

    elif db_type == "mysql":
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=config.get("mysql_host", "localhost"),
                port=int(config.get("mysql_port", 3306)),
                database=config.get("mysql_database", "restaurant_db"),
                user=config.get("mysql_user", ""),
                password=config.get("mysql_password", ""),
                charset=config.get("mysql_charset", "utf8mb4"),
                connection_timeout=int(config.get("mysql_timeout", 10)),
            )
            conn.close()
            return True, f"✅ تم الاتصال بـ MySQL: {config['mysql_host']}:{config['mysql_port']}"
        except ImportError:
            return False, "❌ مكتبة mysql-connector-python غير مثبتة\nشغّل: pip install mysql-connector-python"
        except Exception as e:
            return False, f"❌ فشل الاتصال: {e}"

    return False, "❌ نوع قاعدة البيانات غير معروف"
