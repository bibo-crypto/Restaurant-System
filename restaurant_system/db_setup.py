"""
restaurant_system/db_setup.py
───────────────────────────────
شاشة إعداد قاعدة البيانات — تظهر عند أول تشغيل أو عند الحاجة لتغيير الإعداد.
تدعم: SQLite محلي | SQLite على الشبكة | MySQL/MariaDB
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QGroupBox, QFormLayout, QMessageBox, QSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt

from .db_config import get_config, save_config, test_connection


class DBSetupDialog(QDialog):
    """نافذة إعداد الاتصال بقاعدة البيانات."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إعداد قاعدة البيانات — Restaurant Manager")
        self.setMinimumWidth(460)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        cfg = get_config()
        layout = QVBoxLayout(self)

        # ── اختيار نوع قاعدة البيانات ──
        layout.addWidget(QLabel("اختر طريقة تخزين البيانات:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("SQLite محلي (جهاز واحد فقط)", "sqlite_local")
        self.type_combo.addItem("SQLite على الشبكة (مسار مشترك بين الأجهزة)", "sqlite_network")
        self.type_combo.addItem("MySQL / MariaDB (سيرفر مركزي — موصى به لعدة أجهزة)", "mysql")
        idx = {"sqlite_local": 0, "sqlite_network": 1, "mysql": 2}.get(cfg.get("db_type"), 0)
        self.type_combo.setCurrentIndex(idx)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(self.type_combo)

        # ── إعدادات SQLite الشبكي ──
        self.sqlite_box = QGroupBox("مسار ملف قاعدة البيانات على الشبكة")
        sqlite_form = QHBoxLayout()
        self.sqlite_path = QLineEdit(cfg.get("sqlite_path", ""))
        self.sqlite_path.setPlaceholderText(r"\\SERVER\Share\restaurant.sqlite")
        browse_btn = QPushButton("استعراض...")
        browse_btn.clicked.connect(self._browse_sqlite_path)
        sqlite_form.addWidget(self.sqlite_path)
        sqlite_form.addWidget(browse_btn)
        self.sqlite_box.setLayout(sqlite_form)
        layout.addWidget(self.sqlite_box)

        # ── إعدادات MySQL ──
        self.mysql_box = QGroupBox("إعدادات سيرفر MySQL / MariaDB")
        mysql_form = QFormLayout()
        self.mysql_host = QLineEdit(cfg.get("mysql_host", "localhost"))
        self.mysql_port = QSpinBox()
        self.mysql_port.setRange(1, 65535)
        self.mysql_port.setValue(int(cfg.get("mysql_port", 3306)))
        self.mysql_db = QLineEdit(cfg.get("mysql_database", "restaurant_db"))
        self.mysql_user = QLineEdit(cfg.get("mysql_user", "restaurant_user"))
        self.mysql_pass = QLineEdit(cfg.get("mysql_password", ""))
        self.mysql_pass.setEchoMode(QLineEdit.EchoMode.Password)
        mysql_form.addRow("السيرفر (Host):", self.mysql_host)
        mysql_form.addRow("المنفذ (Port):", self.mysql_port)
        mysql_form.addRow("اسم قاعدة البيانات:", self.mysql_db)
        mysql_form.addRow("اسم المستخدم:", self.mysql_user)
        mysql_form.addRow("كلمة المرور:", self.mysql_pass)
        self.mysql_box.setLayout(mysql_form)
        layout.addWidget(self.mysql_box)

        # ── الأزرار ──
        btn_row = QHBoxLayout()
        test_btn = QPushButton("اختبار الاتصال")
        test_btn.clicked.connect(self._test)
        save_btn = QPushButton("حفظ والمتابعة")
        save_btn.clicked.connect(self._save_and_close)
        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        self._on_type_changed()

    def _on_type_changed(self):
        db_type = self.type_combo.currentData()
        self.sqlite_box.setVisible(db_type == "sqlite_network")
        self.mysql_box.setVisible(db_type == "mysql")

    def _browse_sqlite_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "اختر أو أنشئ ملف قاعدة البيانات",
            "restaurant.sqlite", "SQLite Files (*.sqlite)"
        )
        if path:
            self.sqlite_path.setText(path)

    def _collect_config(self) -> dict:
        return {
            "db_type": self.type_combo.currentData(),
            "sqlite_path": self.sqlite_path.text().strip(),
            "mysql_host": self.mysql_host.text().strip(),
            "mysql_port": self.mysql_port.value(),
            "mysql_database": self.mysql_db.text().strip(),
            "mysql_user": self.mysql_user.text().strip(),
            "mysql_password": self.mysql_pass.text(),
            "mysql_charset": "utf8mb4",
            "mysql_timeout": 10,
        }

    def _test(self):
        cfg = self._collect_config()
        ok, msg = test_connection(cfg)
        if ok:
            QMessageBox.information(self, "نتيجة الاختبار", msg)
        else:
            QMessageBox.warning(self, "نتيجة الاختبار", msg)

    def _save_and_close(self):
        cfg = self._collect_config()
        ok, msg = test_connection(cfg)
        if not ok:
            reply = QMessageBox.question(
                self, "فشل الاتصال",
                f"{msg}\n\nهل تريد الحفظ والمتابعة على أي حال؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        cfg["setup_completed"] = True
        save_config(cfg)
        QMessageBox.information(self, "تم", "تم حفظ إعدادات قاعدة البيانات بنجاح.\nأعد تشغيل البرنامج لتطبيق التغييرات.")
        self.accept()
