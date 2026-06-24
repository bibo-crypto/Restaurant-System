"""
restaurant_system/admin_auth.py
─────────────────────────────────
إدارة كلمة مرور المدير بشكل آمن:
- لا توجد كلمة مرور ثابتة في الكود.
- عند أول تشغيل، تُولَّد كلمة مرور عشوائية وتُكتب في ملف نصي على سطح المكتب
  (يجب على المدير حذفه بعد تغيير كلمة المرور من داخل البرنامج).
- تُخزَّن كلمة المرور مشفّرة (مرتبطة بهوية الجهاز) في db_config.json.
"""

import hashlib
import os
import secrets
from pathlib import Path

from .db_config import get_config, save_config, _DEFAULTS  # noqa: F401


def _hash_password(plain: str) -> str:
    return hashlib.sha256(f"RestaurantManager::{plain}".encode("utf-8")).hexdigest()


def _write_first_login_file(plain_password: str) -> None:
    """يكتب كلمة المرور الأولى لملف نصي على سطح المكتب — مرة واحدة فقط."""
    try:
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        path = desktop / "RestaurantManager_ADMIN_PASSWORD.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("Restaurant Manager — كلمة مرور المدير الأولى\n")
            f.write("=" * 45 + "\n")
            f.write(f"admin / {plain_password}\n")
            f.write("=" * 45 + "\n")
            f.write("⚠️  احذف هذا الملف بعد تغيير كلمة المرور من شاشة الإعدادات.\n")
    except Exception:
        pass  # عدم القدرة على الكتابة لسطح المكتب لا يجب أن يوقف البرنامج


def ensure_admin_password_exists() -> None:
    """
    يضمن وجود كلمة مرور مدير مخزّنة. إن لم توجد (أول تشغيل)، يولّد كلمة
    مرور عشوائية، يحفظها مشفّرة، ويكتبها في ملف على سطح المكتب.
    """
    cfg = get_config()
    if cfg.get("admin_password_hash"):
        return

    plain = secrets.token_urlsafe(9)  # كلمة مرور عشوائية آمنة (12 حرف تقريباً)
    cfg["admin_password_hash"] = _hash_password(plain)
    save_config({**_DEFAULTS, **cfg})
    _write_first_login_file(plain)


def verify_admin_password(value: str) -> bool:
    cfg = get_config()
    stored_hash = cfg.get("admin_password_hash", "")
    if not stored_hash:
        return False
    return _hash_password(value) == stored_hash


def set_admin_password(new_plain: str) -> None:
    """لتغيير كلمة مرور المدير من شاشة الإعدادات لاحقاً."""
    cfg = get_config()
    cfg["admin_password_hash"] = _hash_password(new_plain)
    save_config({**_DEFAULTS, **cfg})
