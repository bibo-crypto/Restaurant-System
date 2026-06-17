# 🍽️ Restaurant Manager — نظام إدارة مطعم

تطبيق سطح مكتب لإدارة المطعم بالكامل، مبني بـ Python و PyQt6، يدعم تعدد الأدوار (مدير، كاشير، جرسون، مطبخ) وواجهة ثنائية اللغة (عربي / إنجليزي).

## ✨ المميزات

- **نظام أدوار متعدد:** أربعة أدوار مستقلة — مدير، كاشير، جرسون، ومطبخ — كل دور له شاشاته وصلاحياته الخاصة.
- **شاشة المطبخ (Kitchen Display):** عرض لحظي للطلبات المُرسلة من الجرسونات للمطبخ.
- **إدارة الطاولات:** تتبع حالة الطاولات وإرسال الطلبات وتحصيل الدفع.
- **نظام الحجوزات:** حجز الطاولات مع منع تضارب الحجوزات على نفس الطاولة في نفس الوقت.
- **التقارير:** تقارير مبيعات وأداء مع رسوم بيانية.
- **إشعارات صوتية:** تنبيهات صوتية عند استلام طلبات جديدة في المطبخ.
- **ثنائي اللغة:** دعم كامل للعربية والإنجليزية في كل الواجهات.
- **حفظ تلقائي للحالة:** كل بيانات التطبيق (الطاولات، الحجوزات، الطلبات) محفوظة في SQLite تلقائياً.

## 🛠️ التقنيات المستخدمة

| التقنية | الاستخدام |
|---|---|
| Python 3.10+ | لغة البرمجة الأساسية |
| PyQt6 | واجهة المستخدم |
| SQLite | تخزين حالة التطبيق |

## 🚀 التشغيل

### Windows

```powershell
git clone https://github.com/bibo-crypto/Rysturant-System.git
cd Rysturant-System
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### macOS / Linux

```bash
git clone https://github.com/bibo-crypto/Rysturant-System.git
cd Rysturant-System
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📁 بنية المشروع

```
Rysturant-System/
├── main.py                      # نقطة تشغيل البرنامج
├── requirements.txt             # المتطلبات
└── restaurant_system/
    ├── app.py                   # واجهات التطبيق الكاملة (تسجيل الدخول، الطاولات، المطبخ، التقارير...)
    └── db.py                    # طبقة حفظ واسترجاع حالة التطبيق (SQLite)
```

## 👤 المطور

**Abanob Eid (Bibo)**
مطور Python | تطبيقات سطح المكتب
