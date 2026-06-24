"""
نظام إدارة المطعم — Restaurant Management System
Python + PyQt6  |  عربي / English
"""

import sys, time, copy, random, math, struct, base64, hashlib, json
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt6.QtWidgets import *
from PyQt6.QtCore    import *
from PyQt6.QtGui     import *
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
try:
    from PyQt6.QtMultimedia import QSoundEffect
except ImportError:
    class QSoundEffect:          # graceful fallback if multimedia missing
        def setSource(self,*a): pass
        def setVolume(self,*a): pass
        def play(self): pass
try:
    from .db import load_state, save_state, DEFAULT_DB_PATH
except ImportError:  # pragma: no cover
    from db import load_state, save_state, DEFAULT_DB_PATH


def _admin_password_ok(value: str) -> bool:
    """يتحقق من كلمة مرور المدير المخزّنة بشكل آمن (مشفّرة، عشوائية لكل تثبيت)."""
    from .admin_auth import verify_admin_password
    return verify_admin_password(value)

# ══════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════════
T = {
'ar': dict(
  app_name='نظام إدارة المطعم', login='دخول', select_role='اختر دورك للدخول',
  enter_name='اكتب اسمك (اختياري)', admin_password='كلمة مرور المدير',
  admin_password_placeholder='اكتب كلمة مرور المدير',
  admin_password_wrong='كلمة مرور المدير غير صحيحة',
  lang_btn='EN',
  settings='الإعدادات',
  tables_mgmt='إدارة الطاولات',
  add_table='إضافة طاولة',
  remove_table='مسح طاولة',
  select_table='اختر طاولة',
  seats_lbl='عدد المقاعد',
  table_added='✓ تم إضافة طاولة',
  table_removed='✓ تم مسح طاولة',
  table_remove_busy='لا يمكن مسح طاولة مشغولة أو عليها طلب.',
  kitchen_updates='تعديلات للمطبخ',
  ack_updates='تم استلام التعديل',
  save_pdf='حفظ PDF',
  print_invoice='طباعة الفاتورة',
  switch_user='تبديل المستخدم',
  roles=dict(admin='مدير', cashier='كاشير', waiter='جرسون', kitchen='مطبخ'),
  nav=dict(tables='الطاولات', orders='الطلبات', menu='المنيو',
           reports='التقارير', kitchen='المطبخ', settings='الإعدادات',
           import_export='استيراد / تصدير'),
  status=dict(free='فارغة', occupied='مشغولة', pending='انتظار',
              preparing='يتحضر', ready='جاهز', paid='مدفوع', cancelled='ملغي'),
  table='طاولة', seats='مقاعد', currency='ج.م',
  subtotal='المجموع الجزئي', service_lbl='خدمة', tax_lbl='ضريبة', total='الإجمالي',
  send_kitchen='إرسال للمطبخ', pay_now='ادفع الآن',
  cash='كاش', card='بطاقة', received='المبلغ المستلم', change_lbl='الباقي',
  confirm_payment='تأكيد الدفع', order_num='طلب #',
  mark_preparing='بدء التحضير', mark_ready='جاهز للتسليم',
  no_orders='لا توجد طلبات حالياً', no_items='الطلب فاضي',
  add_item='إضافة صنف', edit_item='تعديل', del_item='حذف',
  item_ar='الاسم بالعربي', item_en='الاسم بالإنجليزي',
  category='الفئة', available='متاح', unavailable='غير متاح',
  save='حفظ', cancel='إلغاء', close='إغلاق',
  daily_rev='إيراد اليوم', orders_today='طلبات اليوم', avg_order='متوسط الطلب',
  recent='آخر الطلبات', logout='خروج', welcome='أهلاً',
  back='رجوع ←', bill_for='فاتورة طاولة',
  svc_note='تُدمج في الإجمالي', tax_note='تُفصل في الفاتورة',
  save_settings='حفظ الإعدادات', settings_saved='✓ تم حفظ الإعدادات',
  preview='معاينة', example_on='مثال على',
  edit_order='تعديل الطلب', cancel_order='إلغاء الطلب',
  save_changes='حفظ التعديلات وإرسال للمطبخ',
  cancel_confirm='تأكيد إلغاء الطلب؟ لا يمكن التراجع.',
  order_cancelled='✓ تم إلغاء الطلب', order_updated='✓ تم تحديث الطلب',
  sent_ok='✓ تم الإرسال للمطبخ', pay_ok='✓ تم الدفع بنجاح',
  inv_mgmt='إدارة الفاتورة', return_items='إرجاع أصناف', cancel_inv='إلغاء الفاتورة',
  return_title='اختر الأصناف المراد إرجاعها',
  confirm_return='تأكيد الإرجاع', refund_amt='مبلغ الاسترداد',
  inv_cancel_confirm='تأكيد إلغاء الفاتورة؟ هذا الإجراء نهائي.',
  refund_ok='✓ تم تسجيل الإرجاع', inv_cancelled='✓ تم إلغاء الفاتورة',
  total_refunds='إجمالي المستردات', net_rev='صافي الإيراد',
  reason='السبب', enter_reason='اكتب السبب...',
  refunds_hist='سجل الإرجاع', no_refunds='لا يوجد إرجاع',
  avail_qty='متاح للإرجاع', already_ret='مُرجع',
  free_lbl='فارغة', occ_lbl='مشغولة', ready_lbl='جاهزة للدفع',
  item_count='صنف', mins='د',
  queue1='طلب في الانتظار', queueN='طلبات في الانتظار',
  all_cats='الكل', cat_names={'وجبات رئيسية':'وجبات رئيسية','سلطات':'سلطات','مشروبات':'مشروبات','حلويات':'حلويات'},
  del_confirm='حذف الصنف؟', edit_mode='وضع التعديل',
  cancelled_inv='فاتورة ملغاة', click_inv='انقر لإدارة الفاتورة',
  exit_edit='✕ إلغاء التعديل',
  nav_warehouse='المخازن',
  warehouse_title='إدارة المخازن',
  stock_qty='الكمية المتاحة',
  stock_alert_lbl='حد التنبيه',
  stock_alert_note='تنبيه عند نقص المخزون عن هذا الرقم',
  add_stock='إضافة كمية',
  set_stock='تعيين الكمية',
  low_stock_warning='⚠️ مخزون منخفض',
  out_of_stock='نفد المخزون',
  unlimited='غير محدود',
  stock_updated='✓ تم تحديث المخزون',
  stock_deducted='تم خصم من المخزون',
  low_stock_items='أصناف تحتاج تعبئة',
  all_ok='المخزون كافٍ',
  current_stock='المخزون الحالي',
  save_stock='حفظ المخزون',
  unit='وحدة',
  # ── Reservations ──
  nav_reservations='الحجوزات',
  res_title='نظام الحجز المسبق',
  new_res='حجز جديد',
  res_name='اسم العميل',
  res_phone='رقم الهاتف',
  res_date='التاريخ',
  res_time='الوقت',
  res_guests='عدد الأشخاص',
  res_notes='ملاحظات',
  res_table='الطاولة',
  res_status_pending='قيد الانتظار',
  res_status_confirmed='مؤكد',
  res_status_seated='جالس',
  res_status_cancelled='ملغي',
  res_status_noshow='لم يحضر',
  confirm_res='تأكيد الحجز',
  seat_res='إجلاس العميل',
  cancel_res='إلغاء الحجز',
  noshow_res='لم يحضر',
  res_today='حجوزات اليوم',
  res_upcoming='القادمة',
  res_add_ok='✓ تم إضافة الحجز',
  res_updated='✓ تم تحديث الحجز',
  res_cancelled_ok='✓ تم إلغاء الحجز',
  res_no_table='لا توجد طاولة مناسبة',
  res_conflict='يوجد حجز آخر في نفس الوقت لهذه الطاولة',
  guests='أشخاص',
  today='اليوم',
  tomorrow='غداً',
  edit_res='تعديل الحجز',
  delete_res='حذف',
  res_deleted='✓ تم حذف الحجز',
  auto_table='اختيار تلقائي',
  # ── Advanced Reports ──
  rep_period='الفترة',
  rep_today='اليوم',
  rep_week='هذا الأسبوع',
  rep_month='هذا الشهر',
  rep_custom='فترة مخصصة',
  top_items='أكثر الأصناف مبيعاً',
  peak_hours='ساعات الذروة',
  rep_orders='طلبات',
  rep_revenue='إيراد',
  rep_qty='كمية',
  hour_lbl='الساعة',
  day_lbl='اليوم',
  week_days=['الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'],
  no_data='لا توجد بيانات',
  rep_summary='ملخص الفترة',
  total_orders='إجمالي الطلبات',
  total_revenue='إجمالي الإيراد',
  paid_count='مدفوع',
  cancelled_count='ملغي',
  from_date='من',
  to_date='إلى',
  # ── Sound ──
  sound_settings='إعدادات الصوت',
  sound_enabled='تفعيل الإشعارات الصوتية',
  sound_new_order='صوت عند وصول طلب جديد',
  sound_order_ready='صوت عند جاهزية الطلب',
  sound_test='اختبار الصوت',
  sound_volume='مستوى الصوت',
),
'en': dict(
  app_name='Restaurant Manager', login='Enter', select_role='Select your role',
  enter_name='Enter your name (optional)', admin_password='Admin password',
  admin_password_placeholder='Enter admin password',
  admin_password_wrong='Incorrect admin password',
  lang_btn='AR',
  settings='Settings',
  tables_mgmt='Tables Management',
  add_table='Add Table',
  remove_table='Remove Table',
  select_table='Select Table',
  seats_lbl='Seats',
  table_added='✓ Table added',
  table_removed='✓ Table removed',
  table_remove_busy='Cannot remove a busy table or a table with an active order.',
  kitchen_updates='Kitchen updates',
  ack_updates='Acknowledge update',
  save_pdf='Save PDF',
  print_invoice='Print Invoice',
  switch_user='Switch user',
  roles=dict(admin='Manager', cashier='Cashier', waiter='Waiter', kitchen='Kitchen'),
  nav=dict(tables='Tables', orders='Orders', menu='Menu',
           reports='Reports', kitchen='Kitchen', settings='Settings',
           import_export='Import / Export'),
  status=dict(free='Free', occupied='Occupied', pending='Pending',
              preparing='Preparing', ready='Ready', paid='Paid', cancelled='Cancelled'),
  table='Table', seats='Seats', currency='EGP',
  subtotal='Subtotal', service_lbl='Service', tax_lbl='Tax', total='Total',
  send_kitchen='Send to Kitchen', pay_now='Pay Now',
  cash='Cash', card='Card', received='Amount Received', change_lbl='Change',
  confirm_payment='Confirm Payment', order_num='Order #',
  mark_preparing='Start Preparing', mark_ready='Mark as Ready',
  no_orders='No orders at the moment', no_items='Order is empty',
  add_item='Add Item', edit_item='Edit', del_item='Delete',
  item_ar='Arabic Name', item_en='English Name',
  category='Category', available='Available', unavailable='Unavailable',
  save='Save', cancel='Cancel', close='Close',
  daily_rev="Today's Revenue", orders_today="Today's Orders", avg_order='Avg Order',
  recent='Recent Orders', logout='Logout', welcome='Welcome',
  back='← Back', bill_for='Bill - Table',
  svc_note='Merged into total', tax_note='Shown separately on invoice',
  save_settings='Save Settings', settings_saved='✓ Settings saved',
  preview='Preview', example_on='Example on',
  edit_order='Edit Order', cancel_order='Cancel Order',
  save_changes='Save Changes & Send to Kitchen',
  cancel_confirm='Confirm order cancellation? Cannot be undone.',
  order_cancelled='✓ Order cancelled', order_updated='✓ Order updated',
  sent_ok='✓ Sent to kitchen', pay_ok='✓ Payment successful',
  inv_mgmt='Invoice Management', return_items='Return Items', cancel_inv='Cancel Invoice',
  return_title='Select items to return',
  confirm_return='Confirm Return', refund_amt='Refund Amount',
  inv_cancel_confirm='Confirm full invoice cancellation? This is permanent.',
  refund_ok='✓ Return recorded', inv_cancelled='✓ Invoice cancelled',
  total_refunds='Total Refunds', net_rev='Net Revenue',
  reason='Reason', enter_reason='Enter reason...',
  refunds_hist='Return History', no_refunds='No returns',
  avail_qty='Available to return', already_ret='Returned',
  free_lbl='Free', occ_lbl='Occupied', ready_lbl='Ready to Pay',
  item_count='item', mins='min',
  queue1='order in queue', queueN='orders in queue',
  all_cats='All', cat_names={'وجبات رئيسية':'Main Dishes','سلطات':'Salads','مشروبات':'Drinks','حلويات':'Desserts'},
  del_confirm='Delete item?', edit_mode='Edit Mode',
  cancelled_inv='Cancelled Invoice', click_inv='Click to manage invoice',
  exit_edit='✕ Cancel Edit',
  nav_warehouse='Warehouse',
  warehouse_title='Inventory Management',
  stock_qty='Available Qty',
  stock_alert_lbl='Alert Threshold',
  stock_alert_note='Alert when stock falls below this number',
  add_stock='Add Stock',
  set_stock='Set Quantity',
  low_stock_warning='⚠️ Low Stock',
  out_of_stock='Out of Stock',
  unlimited='Unlimited',
  stock_updated='✓ Stock updated',
  stock_deducted='Deducted from stock',
  low_stock_items='Items needing restock',
  all_ok='Stock levels OK',
  current_stock='Current Stock',
  save_stock='Save Stock',
  unit='unit',
  # ── Reservations ──
  nav_reservations='Reservations',
  res_title='Reservation System',
  new_res='New Reservation',
  res_name='Guest Name',
  res_phone='Phone',
  res_date='Date',
  res_time='Time',
  res_guests='Guests',
  res_notes='Notes',
  res_table='Table',
  res_status_pending='Pending',
  res_status_confirmed='Confirmed',
  res_status_seated='Seated',
  res_status_cancelled='Cancelled',
  res_status_noshow='No Show',
  confirm_res='Confirm',
  seat_res='Seat Guest',
  cancel_res='Cancel',
  noshow_res='No Show',
  res_today="Today's Reservations",
  res_upcoming='Upcoming',
  res_add_ok='✓ Reservation added',
  res_updated='✓ Reservation updated',
  res_cancelled_ok='✓ Reservation cancelled',
  res_no_table='No suitable table found',
  res_conflict='Another reservation exists for this table at the same time',
  guests='guests',
  today='Today',
  tomorrow='Tomorrow',
  edit_res='Edit',
  delete_res='Delete',
  res_deleted='✓ Reservation deleted',
  auto_table='Auto Select',
  # ── Advanced Reports ──
  rep_period='Period',
  rep_today='Today',
  rep_week='This Week',
  rep_month='This Month',
  rep_custom='Custom',
  top_items='Top Selling Items',
  peak_hours='Peak Hours',
  rep_orders='orders',
  rep_revenue='Revenue',
  rep_qty='Qty',
  hour_lbl='Hour',
  day_lbl='Day',
  week_days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
  no_data='No data available',
  rep_summary='Period Summary',
  total_orders='Total Orders',
  total_revenue='Total Revenue',
  paid_count='Paid',
  cancelled_count='Cancelled',
  from_date='From',
  to_date='To',
  # ── Sound ──
  sound_settings='Sound Settings',
  sound_enabled='Enable Sound Notifications',
  sound_new_order='Sound on new order',
  sound_order_ready='Sound on order ready',
  sound_test='Test Sound',
  sound_volume='Volume',
)}

# ══════════════════════════════════════════════════════════════
#  INITIAL DATA
# ══════════════════════════════════════════════════════════════
INIT_MENU = [
  dict(id=1,  a='شاورما دجاج',   e='Chicken Shawarma',  cat='وجبات رئيسية', price=45.0, on=True),
  dict(id=2,  a='شاورما لحم',    e='Meat Shawarma',     cat='وجبات رئيسية', price=55.0, on=True),
  dict(id=3,  a='مكرونة بشاميل', e='Pasta Bechamel',    cat='وجبات رئيسية', price=40.0, on=True),
  dict(id=4,  a='فراخ مشوية',    e='Grilled Chicken',   cat='وجبات رئيسية', price=65.0, on=True),
  dict(id=5,  a='سلطة خضراء',   e='Green Salad',       cat='سلطات',        price=20.0, on=True),
  dict(id=6,  a='سلطة سيزر',    e='Caesar Salad',      cat='سلطات',        price=30.0, on=True),
  dict(id=7,  a='سلطة فتوش',    e='Fattoush',          cat='سلطات',        price=22.0, on=True),
  dict(id=8,  a='عصير برتقال',  e='Orange Juice',      cat='مشروبات',      price=18.0, on=True),
  dict(id=9,  a='مياه معدنية',  e='Mineral Water',     cat='مشروبات',      price= 5.0, on=True),
  dict(id=10, a='كوكاكولا',     e='Coca Cola',         cat='مشروبات',      price=12.0, on=True),
  dict(id=11, a='كنافة',        e='Kunafa',            cat='حلويات',       price=28.0, on=True),
  dict(id=12, a='أم علي',       e='Om Ali',            cat='حلويات',       price=25.0, on=True),
]
INIT_TABLES = [dict(id=i+1, seats=[2,4,4,6,2,4,6,4][i], status='free') for i in range(8)]
CATS = ['وجبات رئيسية', 'سلطات', 'مشروبات', 'حلويات']

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def uid():
    return int(time.time()*1000) + random.randint(0,9999)

def calc_order(items, settings):
    sub  = round(sum(i['qty']*i['price'] for i in items), 2)
    svc  = round(sub  * settings.get('service',0)/100, 2)
    base = sub + svc
    tax  = round(base * settings.get('tax',0)/100, 2)
    tot  = round(base + tax, 2)
    return sub, svc, tax, tot

def diff_items(old_items, new_items):
    old_map = {x['mid']: int(x.get('qty', 0)) for x in old_items}
    new_map = {x['mid']: int(x.get('qty', 0)) for x in new_items}
    all_mids = set(old_map) | set(new_map)
    out = []
    for mid in all_mids:
        delta = new_map.get(mid, 0) - old_map.get(mid, 0)
        if delta == 0:
            continue
        ref = next((x for x in (new_items if delta > 0 else old_items) if x['mid'] == mid), None)
        if not ref:
            continue
        out.append(dict(mid=mid, a=ref.get('a', ''), e=ref.get('e', ''), delta=delta))
    out.sort(key=lambda x: (x['delta'] < 0, x['mid']))
    return out

def fmt_time(ts):
    return datetime.fromtimestamp(ts/1000).strftime('%I:%M %p')

def fmt_date(ts):
    return datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')

def elapsed_m(ts):
    return int((time.time()*1000 - ts)/60000)

def t_str(key):          # shortcut
    return T[APP.lang][key]

# ── Sound Engine ──────────────────────────────────────────────────
def _make_wav_bytes(freq=880, duration=0.18, volume=0.5, sample_rate=22050):
    """Generate a simple sine-wave WAV in memory (no external files needed)."""
    n = int(sample_rate * duration)
    samples = []
    fade = max(1, int(n * 0.15))
    for i in range(n):
        t2 = i / sample_rate
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t2))
        val = max(-32768, min(32767, val))
        samples.append(struct.pack('<h', val))
    data = b''.join(samples)
    num_channels, bits, data_size = 1, 16, len(data)
    byte_rate = sample_rate * num_channels * bits // 8
    block_align = num_channels * bits // 8
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16,
        1, num_channels, sample_rate, byte_rate, block_align, bits,
        b'data', data_size)
    return header + data

_sound_effects = {}

def _get_sfx(name):
    """Lazy-create QSoundEffect for a given beep profile."""
    if name in _sound_effects:
        return _sound_effects[name]
    profiles = dict(
        new_order  = dict(freq=660, duration=0.22, volume=0.6),
        order_ready= dict(freq=880, duration=0.15, volume=0.55),
        test       = dict(freq=740, duration=0.25, volume=0.6),
    )
    p = profiles.get(name, profiles['new_order'])
    wav = _make_wav_bytes(**p)
    b64 = base64.b64encode(wav).decode()
    sfx = QSoundEffect()
    sfx.setSource(QUrl(f"data:audio/wav;base64,{b64}"))
    _sound_effects[name] = sfx
    return sfx

def play_sound(name='new_order'):
    """Play a sound if enabled."""
    if not APP.sound.get('enabled', True): return
    if name == 'new_order'   and not APP.sound.get('new_order', True):   return
    if name == 'order_ready' and not APP.sound.get('order_ready', True): return
    try:
        sfx = _get_sfx(name)
        vol = APP.sound.get('volume', 80) / 100.0
        sfx.setVolume(vol)
        sfx.play()
    except Exception:
        pass   # sound is best-effort

def get_stock(mid):
    """Return current stock for menu item id. -1 = unlimited."""
    return APP.stock.get(mid, -1)

def set_stock(mid, qty):
    APP.stock[mid] = max(-1, int(qty))

def deduct_stock(items):
    """Deduct ordered quantities from stock. Returns list of low-stock item names."""
    low = []
    t = APP.t()
    alert = int(APP.settings.get('stock_alert', 5))
    for item in items:
        mid = item['mid']
        cur = get_stock(mid)
        if cur == -1:
            continue
        new_qty = max(0, cur - item['qty'])
        set_stock(mid, new_qty)
        if new_qty <= alert:
            name = item['a'] if APP.lang=='ar' else item['e']
            low.append(f"{name} ({new_qty} {t['unit']})")
    return low

def restore_stock(items):
    """Restore stock when order is cancelled."""
    for item in items:
        mid = item['mid']
        cur = get_stock(mid)
        if cur == -1:
            continue
        set_stock(mid, cur + item['qty'])

# ══════════════════════════════════════════════════════════════
#  GLOBAL APP STATE
# ══════════════════════════════════════════════════════════════
class AppState:
    def __init__(self):
        self.lang     = 'ar'
        self.user     = None
        self.tables   = copy.deepcopy(INIT_TABLES)
        self.menu     = copy.deepcopy(INIT_MENU)
        self.orders   = []
        self.settings = dict(tax=14.0, service=12.0, stock_alert=5)
        # stock dict: {menu_item_id: qty}  -1 = unlimited
        self.stock        = {}
        # reservations list
        self.reservations = []
        # sound settings
        self.sound = dict(enabled=True, new_order=True, order_ready=True, volume=80)

    def t(self):          return T[self.lang]
    def tbl(self, tid):   return next((x for x in self.tables if x['id']==tid), None)
    def ord(self, oid):   return next((x for x in self.orders  if x['id']==oid), None)
    def active_ord(self, tid):
        return next((o for o in self.orders
                     if o['tableId']==tid and o['status'] not in ('paid','cancelled')), None)

APP = AppState()

def _state_to_dict():
    return dict(
        lang=APP.lang,
        tables=APP.tables,
        menu=APP.menu,
        orders=APP.orders,
        settings=APP.settings,
        stock=APP.stock,
        reservations=APP.reservations,
        sound=APP.sound,
    )

def _apply_state(d):
    if not isinstance(d, dict):
        return
    if 'lang' in d and d['lang'] in ('ar', 'en'):
        APP.lang = d['lang']
    if isinstance(d.get('tables'), list):
        APP.tables = d['tables']
    if isinstance(d.get('menu'), list):
        APP.menu = d['menu']
    if isinstance(d.get('orders'), list):
        APP.orders = d['orders']
    if isinstance(d.get('settings'), dict):
        APP.settings = d['settings']
    if isinstance(d.get('stock'), dict):
        APP.stock = {int(k) if str(k).isdigit() else k: v for k,v in d['stock'].items()}
    if isinstance(d.get('reservations'), list):
        APP.reservations = d['reservations']
    if isinstance(d.get('sound'), dict):
        APP.sound.update(d['sound'])

def _export_payload():
    return dict(
        schema='restaurant-system-backup',
        version=1,
        exportedAt=datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        state=_state_to_dict(),
    )

def _extract_import_state(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid backup file")
    state = payload.get('state') if isinstance(payload.get('state'), dict) else payload
    if not isinstance(state, dict):
        raise ValueError("Invalid backup file")
    filtered = {}
    for key in ('lang', 'tables', 'menu', 'orders', 'settings', 'stock', 'reservations', 'sound'):
        if key not in state:
            continue
        value = state[key]
        if key == 'lang':
            if value in ('ar', 'en'):
                filtered[key] = value
        elif key in ('tables', 'menu', 'orders', 'reservations'):
            if isinstance(value, list):
                filtered[key] = value
        elif key in ('settings', 'stock', 'sound'):
            if isinstance(value, dict):
                filtered[key] = value
    if not filtered:
        raise ValueError("No valid application data found")
    return filtered

def persist_state():
    try:
        save_state(_state_to_dict(), DEFAULT_DB_PATH)
    except Exception:
        # Best-effort persistence; avoid crashing UI.
        pass

_loaded = load_state(DEFAULT_DB_PATH)
if _loaded:
    _apply_state(_loaded)

# ══════════════════════════════════════════════════════════════
#  STYLESHEET
# ══════════════════════════════════════════════════════════════
STYLE = """
* { font-family: 'Segoe UI', Tahoma, Arial; }
QMainWindow, QDialog { background:#0a0a0a; }
QWidget { background:#0a0a0a; color:#e5e7eb; }
QScrollArea { border:none; background:transparent; }
QScrollArea > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { background:#111; width:7px; border-radius:4px; margin:0; }
QScrollBar::handle:vertical { background:#374151; border-radius:4px; min-height:20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QLineEdit {
  background:#111; border:1.5px solid #374151; border-radius:10px;
  padding:8px 14px; color:white; font-size:13px;
}
QLineEdit:focus { border-color:#f59e0b; }
QTextEdit {
  background:#111; border:1.5px solid #374151; border-radius:10px;
  padding:8px 14px; color:white; font-size:13px;
}
QTextEdit:focus { border-color:#f43f5e; }
QComboBox {
  background:#111; border:1.5px solid #374151; border-radius:10px;
  padding:8px 14px; color:white; font-size:13px; min-height:38px;
}
QComboBox::drop-down { border:none; width:22px; }
QComboBox QAbstractItemView { background:#1a1a1a; border:1px solid #374151; color:white; selection-background-color:#d97706; }
QDoubleSpinBox {
  background:#111; border:1.5px solid #374151; border-radius:10px;
  padding:8px 14px; color:white; font-size:18px; font-weight:bold; min-height:42px;
}
QDoubleSpinBox:focus { border-color:#f59e0b; }
QMessageBox { background:#1a1a1a; }
QMessageBox QLabel { color:white; font-size:13px; }
QTabBar::tab {
  background:#111; color:#6b7280; padding:10px 22px;
  border:none; font-weight:bold; font-size:12px;
}
QTabBar::tab:selected  { color:#f59e0b; border-bottom:2px solid #f59e0b; background:#0a0a0a; }
QTabBar::tab:hover     { color:#d1d5db; }
QTabWidget::pane       { border:1px solid #1f2937; background:#0a0a0a; }
"""

# ══════════════════════════════════════════════════════════════
#  REUSABLE WIDGETS
# ══════════════════════════════════════════════════════════════
def lbl(text, color='#e5e7eb', size=13, bold=False, align=Qt.AlignmentFlag.AlignLeft):
    w = QLabel(text)
    weight = 'bold' if bold else 'normal'
    w.setStyleSheet(f'color:{color}; font-size:{size}px; font-weight:{weight}; background:transparent; border:none;')
    w.setAlignment(align)
    return w

def btn(text, color='amber', h=42, fs=13, bold=True):
    PAL = dict(
        amber =('background:#f59e0b;', '#fff', '#d97706', '#c2410c'),
        green =('background:#10b981;', '#fff', '#059669', '#047857'),
        sky   =('background:#0ea5e9;', '#fff', '#0284c7', '#0369a1'),
        rose  =('background:#f43f5e;', '#fff', '#e11d48', '#be123c'),
        gray  =('background:#1f2937;', '#9ca3af', '#374151', '#4b5563'),
        violet=('background:#8b5cf6;', '#fff', '#7c3aed', '#6d28d9'),
        orange=('background:#f97316;', '#fff', '#ea580c', '#c2410c'),
        dark_rose=('background:#4c0519;', '#f43f5e', '#881337', '#9f1239'),
        outline=('background:transparent; border:1.5px solid #374151;', '#9ca3af', '#111', '#1f2937'),
    )
    bg, fg, hov, prs = PAL.get(color, PAL['amber'])
    w_b = 'bold' if bold else 'normal'
    b = QPushButton(text)
    b.setFixedHeight(h)
    b.setStyleSheet(f"""
      QPushButton {{ {bg} color:{fg}; border-radius:10px; padding:0 16px;
        font-size:{fs}px; font-weight:{w_b}; border:none; }}
      QPushButton:hover {{ background:{hov}; color:{fg}; }}
      QPushButton:pressed {{ background:{prs}; }}
      QPushButton:disabled {{ background:#1f2937; color:#4b5563; }}
    """)
    return b

def card_widget(bg='#111111', border='#1f2937', radius=14):
    w = QWidget()
    w.setStyleSheet(f'background:{bg}; border:1.5px solid {border}; border-radius:{radius}px;')
    return w

def divider():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet('background:#1f2937; border:none; max-height:1px;')
    return f

# ── Status Badge ──────────────────────────────────────────────
BADGE_COLORS = dict(
    free      =('#d1fae5','#065f46'),
    occupied  =('#fee2e2','#991b1b'),
    pending   =('#ffedd5','#9a3412'),
    preparing =('#e0f2fe','#075985'),
    ready     =('#ede9fe','#5b21b6'),
    paid      =('#f3f4f6','#374151'),
    cancelled =('#1c0510','#f43f5e'),
)

def status_badge(status, t, fs=11, h=22):
    text = t['status'].get(status, status)
    bg, fg = BADGE_COLORS.get(status, ('#1f2937','#9ca3af'))
    w = QLabel(text)
    w.setStyleSheet(f'background:{bg}; color:{fg}; border:1px solid {fg}; border-radius:10px; padding:2px 9px; font-size:{fs}px; font-weight:bold;')
    w.setAlignment(Qt.AlignmentFlag.AlignCenter)
    w.setFixedHeight(h)
    return w

# ── Toast ─────────────────────────────────────────────────────
class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('background:#111827; color:white; border:1px solid #374151; border-radius:16px; padding:12px 28px; font-size:13px; font-weight:bold;')
        self.hide()
        self._t = QTimer(singleShot=True)
        self._t.timeout.connect(self.hide)

    def show_msg(self, msg):
        self.setText(msg); self.adjustSize()
        pw, ph = self.parent().width(), self.parent().height()
        self.move((pw-self.width())//2, ph-self.height()-28)
        self.show(); self.raise_(); self._t.start(2400)

# ══════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════
class LoginScreen(QWidget):
    logged_in = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._sel = None
        self._rbtn = {}
        self._build()

    def _build(self):
        self.setStyleSheet('background:#0a0a0a;')
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setFixedWidth(400)
        card.setStyleSheet('background:#111; border:1.5px solid #1f2937; border-radius:24px;')
        vl = QVBoxLayout(card)
        vl.setContentsMargins(40,36,40,36); vl.setSpacing(14)

        ico = QLabel('🍴')
        ico.setStyleSheet('font-size:52px; background:transparent; border:none;')
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(ico)

        self.title_l = lbl('', '#fff', 22, True, Qt.AlignmentFlag.AlignCenter)
        self.sub_l   = lbl('', '#6b7280', 13, False, Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(self.title_l); vl.addWidget(self.sub_l)
        vl.addSpacing(4)

        self.name_in = QLineEdit()
        self.name_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_in.setFixedHeight(44)
        vl.addWidget(self.name_in)
        vl.addSpacing(4)

        self.pass_in = QLineEdit()
        self.pass_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pass_in.setFixedHeight(44)
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        vl.addWidget(self.pass_in)
        self.pass_in.hide()

        grid_w = QWidget(); grid_w.setStyleSheet('background:transparent; border:none;')
        grid   = QGridLayout(grid_w); grid.setSpacing(10)
        for idx,(rid,ico2) in enumerate([('admin','👨‍💼'),('cashier','💳'),('waiter','🍽️'),('kitchen','👨‍🍳')]):
            b = QPushButton(); b.setFixedSize(150,82); b.setCheckable(True)
            b.clicked.connect(lambda _,r=rid: self._pick(r))
            self._rbtn[rid] = b; grid.addWidget(b, idx//2, idx%2)
        vl.addWidget(grid_w)
        vl.addSpacing(4)

        self.login_b = btn('', 'amber', 50, 15)
        self.login_b.clicked.connect(self._do)
        vl.addWidget(self.login_b)

        self.lang_b = QPushButton()
        self.lang_b.setStyleSheet('background:transparent; border:none; color:#4b5563; font-size:12px; font-weight:bold;')
        self.lang_b.clicked.connect(self._toggle_lang)
        vl.addWidget(self.lang_b, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.refresh()

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title_l.setText(t['app_name']); self.sub_l.setText(t['select_role'])
        self.name_in.setPlaceholderText(t['enter_name'])
        self.pass_in.setPlaceholderText(t['admin_password_placeholder'])
        self.login_b.setText(f"  {t['login']}  →")
        self.lang_b.setText(t['lang_btn'])
        icons = dict(admin='👨‍💼', cashier='💳', waiter='🍽️', kitchen='👨‍🍳')
        for rid, b in self._rbtn.items():
            b.setText(f"{icons[rid]}\n{t['roles'][rid]}")
            self._style_rb(b, b.isChecked())
        if self._sel == 'admin':
            self.pass_in.show()
        else:
            self.pass_in.hide()

    def _pick(self, rid):
        self._sel = rid
        for r,b in self._rbtn.items():
            b.setChecked(r==rid); self._style_rb(b, r==rid)
        if rid == 'admin':
            self.pass_in.show()
            self.pass_in.setFocus()
        else:
            self.pass_in.clear()
            self.pass_in.hide()

    def _style_rb(self, b, sel):
        if sel:
            b.setStyleSheet('QPushButton{background:#1c1500;border:2px solid #f59e0b;border-radius:14px;color:#f59e0b;font-size:24px;font-weight:bold;}')
        else:
            b.setStyleSheet('QPushButton{background:#111;border:1.5px solid #1f2937;border-radius:14px;color:#6b7280;font-size:24px;font-weight:bold;}QPushButton:hover{border-color:#374151;color:#9ca3af;}')

    def _do(self):
        if not self._sel: return
        t = APP.t()
        if self._sel == 'admin' and not _admin_password_ok(self.pass_in.text().strip()):
            QMessageBox.warning(self, t['login'], t['admin_password_wrong'])
            self.pass_in.selectAll()
            self.pass_in.setFocus()
            return
        name = self.name_in.text().strip() or t['roles'][self._sel]
        self.logged_in.emit(dict(role=self._sel, name=name))

    def _toggle_lang(self):
        APP.lang = 'en' if APP.lang=='ar' else 'ar'
        self.refresh()

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
class Sidebar(QWidget):
    screen_changed = pyqtSignal(str)
    lang_toggled   = pyqtSignal()
    logout         = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(72)
        self.setStyleSheet('background:#050505; border-right:1px solid #0f0f0f;')
        self._btns = {}
        self._cur  = ''
        vl = QVBoxLayout(self)
        vl.setContentsMargins(6,12,6,12); vl.setSpacing(4)

        ico = QLabel('🍴')
        ico.setStyleSheet('font-size:26px; background:transparent; border:none;')
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(ico); vl.addSpacing(6)

        self._btn_area = QVBoxLayout(); self._btn_area.setSpacing(4)
        vl.addLayout(self._btn_area)
        vl.addStretch()

        # Lang
        self.lang_b = QPushButton()
        self.lang_b.setFixedSize(56,28)
        self.lang_b.setStyleSheet('background:transparent; border:none; color:#4b5563; font-size:11px; font-weight:bold;')
        self.lang_b.clicked.connect(self.lang_toggled.emit)
        vl.addWidget(self.lang_b, alignment=Qt.AlignmentFlag.AlignCenter)

        # Logout
        self.logout_b = QPushButton('🚪')
        self.logout_b.setFixedSize(56,56)
        self.logout_b.setStyleSheet('QPushButton{background:transparent;border:none;font-size:24px;border-radius:12px;}QPushButton:hover{background:#1c0510;}')
        self.logout_b.clicked.connect(self.logout.emit)
        vl.addWidget(self.logout_b, alignment=Qt.AlignmentFlag.AlignCenter)

    def build_items(self, role):
        # clear
        while self._btn_area.count():
            item = self._btn_area.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._btns.clear()

        base_items = [
            ('tables','🪑'), ('orders','📋'), ('menu','🍴'),
            ('warehouse','📦'), ('reservations','📅'),
            ('reports','📊'), ('import_export','💾'), ('settings','⚙️')
        ]
        kitchen_items = [('kitchen','👨‍🍳')]
        if role == 'kitchen':
            items = kitchen_items
        elif role == 'waiter':
            items = [('tables','🪑')]
        elif role == 'cashier':
            items = [('tables','🪑'),('orders','📋')]
        else:  # admin
            items = base_items

        t = APP.t()
        for sid, ico in items:
            b = QPushButton(f'{ico}')
            b.setFixedSize(56,56)
            b.clicked.connect(lambda _,s=sid: self.screen_changed.emit(s))
            self._btns[sid] = b
            self._btn_area.addWidget(b, alignment=Qt.AlignmentFlag.AlignCenter)

        self.refresh()

    def set_active(self, sid):
        self._cur = sid
        for s,b in self._btns.items():
            if s == sid:
                b.setStyleSheet('QPushButton{background:#f59e0b;border:none;border-radius:14px;font-size:24px;color:white;}')
            else:
                b.setStyleSheet('QPushButton{background:transparent;border:none;border-radius:14px;font-size:24px;color:#6b7280;}QPushButton:hover{background:#111;}')

    def refresh(self):
        t = APP.t()
        self.lang_b.setText(t['lang_btn'])
        self.set_active(self._cur)

# ══════════════════════════════════════════════════════════════
#  TABLES SCREEN
# ══════════════════════════════════════════════════════════════
class TablesScreen(QWidget):
    table_clicked = pyqtSignal(dict, object)

    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self)
        vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)

        self.title = lbl('', '#fff', 20, True)
        vl.addWidget(self.title)

        # Stats
        stats_row = QHBoxLayout(); stats_row.setSpacing(12)
        self._sf = self._mk_stat('#052e16','#166534','#22c55e')
        self._so = self._mk_stat('#1c0510','#881337','#f43f5e')
        self._sr = self._mk_stat('#150d2a','#4c1d95','#a78bfa')
        for w in [self._sf,self._so,self._sr]: stats_row.addWidget(w)
        vl.addLayout(stats_row)

        # Scroll + Grid
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        ctn = QWidget(); ctn.setStyleSheet('background:transparent;')
        self.grid = QGridLayout(ctn); self.grid.setSpacing(14)
        sc.setWidget(ctn); vl.addWidget(sc)

    def _mk_stat(self, bg, bdr, vc):
        c = QWidget(); c.setFixedHeight(80)
        c.setStyleSheet(f'background:{bg};border:1.5px solid {bdr};border-radius:14px;')
        vl2 = QVBoxLayout(c); vl2.setAlignment(Qt.AlignmentFlag.AlignCenter); vl2.setSpacing(2)
        v = QLabel('0'); v.setStyleSheet(f'color:{vc};font-size:28px;font-weight:bold;background:transparent;border:none;')
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb= QLabel(''); lb.setStyleSheet('color:#6b7280;font-size:11px;background:transparent;border:none;')
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl2.addWidget(v); vl2.addWidget(lb)
        c._v=v; c._l=lb; return c

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"🪑  {t['nav']['tables']}")
        free  = sum(1 for tb in APP.tables if tb['status']=='free')
        occ   = sum(1 for tb in APP.tables if tb['status']=='occupied')
        ready = sum(1 for o  in APP.orders  if o['status']=='ready')
        self._sf._v.setText(str(free));  self._sf._l.setText(t['free_lbl'])
        self._so._v.setText(str(occ));   self._so._l.setText(t['occ_lbl'])
        self._sr._v.setText(str(ready)); self._sr._l.setText(t['ready_lbl'])

        # Rebuild grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Bigger cards: use 3 columns instead of 4
        cols = 3
        for i, tbl in enumerate(APP.tables):
            self.grid.addWidget(self._mk_tbl_card(tbl, t), i//cols, i%cols)

    def _mk_tbl_card(self, tbl, t):
        order  = APP.active_ord(tbl['id'])
        is_rdy = order and order['status']=='ready'
        if   tbl['status']=='free': bg,bdr = '#111','#1f2937'
        elif is_rdy:                bg,bdr = '#150d2a','#6d28d9'
        else:                       bg,bdr = '#1c0510','#881337'

        b = QPushButton()
        # Bigger tile for better readability
        b.setFixedSize(270,230)
        b.setStyleSheet(f'QPushButton{{background:{bg};border:2px solid {bdr};border-radius:18px;}}QPushButton:hover{{border-color:#f59e0b;}}')

        vl = QVBoxLayout(b); vl.setAlignment(Qt.AlignmentFlag.AlignCenter); vl.setSpacing(6)
        icon = '🟣' if is_rdy else ('🟢' if tbl['status']=='free' else '🔴')
        vl.addWidget(lbl(icon,'',42,False,Qt.AlignmentFlag.AlignCenter))
        vl.addWidget(lbl(f"{t['table']} {tbl['id']}",'white',24,True,Qt.AlignmentFlag.AlignCenter))
        vl.addWidget(lbl(f"{tbl['seats']} {t['seats']}",'#9ca3af',17,False,Qt.AlignmentFlag.AlignCenter))
        sb = status_badge(tbl['status'], t, fs=15, h=30); vl.addWidget(sb, alignment=Qt.AlignmentFlag.AlignCenter)
        if order:
            vl.addWidget(lbl(f"{len(order['items'])} {t['item_count']}",'#e5e7eb',16,True,Qt.AlignmentFlag.AlignCenter))
            vl.addWidget(status_badge(order['status'], t, fs=14, h=28), alignment=Qt.AlignmentFlag.AlignCenter)
        b.clicked.connect(lambda _,tb=tbl,o=order: self.table_clicked.emit(tb,o))
        return b

# ══════════════════════════════════════════════════════════════
#  ORDER SCREEN
# ══════════════════════════════════════════════════════════════
class OrderScreen(QWidget):
    go_back   = pyqtSignal()
    order_sent= pyqtSignal(str)   # toast msg
    order_paid= pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.table     = None
        self.exist_ord = None
        self.edit_mode = False
        self._items    = []  # working copy
        self._cur_cat  = 'all'
        self._build()

    # ── Build UI ──────────────────────────────────────────────
    def _build(self):
        root = QHBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── LEFT: Menu ────────────────────────────────────────
        left = QWidget(); left.setStyleSheet('background:transparent;')
        lvl  = QVBoxLayout(left); lvl.setContentsMargins(0,0,0,0); lvl.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setFixedHeight(52)
        hdr.setStyleSheet('background:#050505; border-bottom:1px solid #1f2937;')
        hdr_lay = QHBoxLayout(hdr); hdr_lay.setContentsMargins(16,0,16,0)
        self.back_b = QPushButton()
        self.back_b.setStyleSheet('background:transparent;border:none;color:#6b7280;font-size:13px;font-weight:bold;QPushButton:hover{color:#f59e0b;}')
        self.back_b.clicked.connect(self._on_back)
        self.hdr_title  = lbl('','white',15,True)
        self.hdr_badge  = QLabel(); self.hdr_badge.setStyleSheet('background:transparent;border:none;')
        self.edit_badge = QLabel()
        self.edit_badge.setStyleSheet('background:#1c1500;color:#f59e0b;border:1px solid #854d0e;border-radius:10px;padding:2px 9px;font-size:11px;font-weight:bold;')
        self.edit_badge.hide()
        for w in [self.back_b, self.hdr_title, self.hdr_badge, self.edit_badge]:
            hdr_lay.addWidget(w)
        hdr_lay.addStretch()
        lvl.addWidget(hdr)

        # Categories
        cat_bar = QWidget(); cat_bar.setFixedHeight(50)
        cat_bar.setStyleSheet('background:#050505;border-bottom:1px solid #1f2937;')
        self.cat_lay = QHBoxLayout(cat_bar); self.cat_lay.setContentsMargins(14,0,14,0); self.cat_lay.setSpacing(8)
        lvl.addWidget(cat_bar)

        # Menu grid
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.menu_ctn = QWidget(); self.menu_ctn.setStyleSheet('background:transparent;')
        self.menu_grid= QGridLayout(self.menu_ctn); self.menu_grid.setSpacing(12); self.menu_grid.setContentsMargins(14,14,14,14)
        sc.setWidget(self.menu_ctn); lvl.addWidget(sc)

        root.addWidget(left, stretch=1)

        # ── RIGHT: Summary ────────────────────────────────────
        right = QWidget(); right.setFixedWidth(280)
        right.setStyleSheet('background:#050505;border-left:1px solid #1f2937;')
        rvl = QVBoxLayout(right); rvl.setContentsMargins(0,0,0,0); rvl.setSpacing(0)

        # Order header
        ord_hdr = QWidget(); ord_hdr.setFixedHeight(64)
        ord_hdr.setStyleSheet('background:#050505;border-bottom:1px solid #1f2937;')
        oh_lay = QVBoxLayout(ord_hdr); oh_lay.setContentsMargins(16,8,16,8); oh_lay.setSpacing(2)
        self.ord_num_l = lbl('','white',14,True)
        self.ord_info_l= lbl('','#6b7280',11)
        oh_lay.addWidget(self.ord_num_l); oh_lay.addWidget(self.ord_info_l)
        rvl.addWidget(ord_hdr)

        # Items list
        sc2 = QScrollArea(); sc2.setWidgetResizable(True); sc2.setStyleSheet('background:transparent;border:none;')
        self.items_ctn = QWidget(); self.items_ctn.setStyleSheet('background:transparent;')
        self.items_lay = QVBoxLayout(self.items_ctn); self.items_lay.setContentsMargins(12,12,12,12); self.items_lay.setSpacing(6)
        self.items_lay.addStretch()
        sc2.setWidget(self.items_ctn); rvl.addWidget(sc2, stretch=1)

        # Totals + buttons
        footer = QWidget(); footer.setStyleSheet('background:#050505;border-top:1px solid #1f2937;')
        fvl = QVBoxLayout(footer); fvl.setContentsMargins(14,12,14,14); fvl.setSpacing(8)

        self.sub_row = self._mk_total_row('#9ca3af', '')
        self.svc_row = self._mk_total_row('#22c55e', '')
        self.tax_row = self._mk_total_row('#38bdf8', '')
        self.tot_row = self._mk_total_row('#f59e0b', '', 16)
        self.sub_row.hide(); self.svc_row.hide(); self.tax_row.hide()
        for w in [self.sub_row, self.svc_row, divider(), self.tax_row, divider(), self.tot_row]:
            fvl.addWidget(w)

        fvl.addSpacing(4)
        self.send_b   = btn('', 'sky',   42, 13); fvl.addWidget(self.send_b)
        self.save_b   = btn('', 'sky',   42, 12); fvl.addWidget(self.save_b); self.save_b.hide()
        self.edit_b   = btn('', 'orange',38, 12); fvl.addWidget(self.edit_b); self.edit_b.hide()
        self.cancl_b  = btn('', 'dark_rose',34,11,False); fvl.addWidget(self.cancl_b); self.cancl_b.hide()
        self.pay_b    = btn('', 'green', 44, 13); fvl.addWidget(self.pay_b); self.pay_b.hide()

        self.send_b.clicked.connect(self._do_send)
        self.save_b.clicked.connect(self._do_save_edit)
        self.edit_b.clicked.connect(self._do_enter_edit)
        self.cancl_b.clicked.connect(self._do_cancel_order)
        self.pay_b.clicked.connect(self._show_pay_dialog)
        rvl.addWidget(footer)
        root.addWidget(right)

    def _mk_total_row(self, color, label='', fs=13):
        w = QWidget(); w.setStyleSheet('background:transparent;border:none;')
        hl = QHBoxLayout(w); hl.setContentsMargins(0,0,0,0)
        l = lbl(label, color, fs, fs>13); v = lbl('', color, fs, fs>13)
        hl.addWidget(l); hl.addStretch(); hl.addWidget(v)
        w._l=l; w._v=v; return w

    # ── Load ──────────────────────────────────────────────────
    def load(self, table, existing_order, user_role):
        self.table     = table
        self.exist_ord = existing_order
        self.user_role = user_role
        self.edit_mode = False
        self._items    = copy.deepcopy(existing_order['items']) if existing_order else []
        self._rebuild_ui()

    def _rebuild_ui(self):
        t   = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        is_new   = self.exist_ord is None
        editable = is_new or self.edit_mode
        can_edit = not is_new and self.user_role in ('admin','cashier') and self.exist_ord['status'] not in ('paid',)
        can_pay  = not is_new and self.user_role in ('admin','cashier') and self.exist_ord['status']=='ready' and not self.edit_mode

        self.back_b.setText(f"  {t['exit_edit']}  " if self.edit_mode else f"  {t['back']}  ")
        self.hdr_title.setText(f"{t['table']} {self.table['id']}")
        self.edit_badge.setText(f"✏️ {t['edit_mode']}")
        self.edit_badge.setVisible(self.edit_mode)

        self._rebuild_cats()
        self._rebuild_menu(editable)
        self._rebuild_items(editable)
        self._update_totals()
        self._update_buttons(is_new, editable, can_edit, can_pay, t)

    def _rebuild_cats(self):
        t = APP.t()
        while self.cat_lay.count():
            item = self.cat_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        all_cats = ['all'] + CATS
        for c in all_cats:
            name = t['all_cats'] if c=='all' else (APP.lang=='ar' and c or t['cat_names'].get(c,c))
            b = QPushButton(name); b.setFixedHeight(32)
            active = self._cur_cat==c
            b.setStyleSheet(f"""QPushButton{{
              background:{'#f59e0b' if active else 'transparent'};
              color:{'white' if active else '#6b7280'};
              border:{'none' if active else '1px solid #374151'};
              border-radius:16px; padding:0 14px; font-size:12px; font-weight:bold;
            }}QPushButton:hover{{color:white;}}""")
            b.clicked.connect(lambda _,cat=c: self._set_cat(cat))
            self.cat_lay.addWidget(b)
        self.cat_lay.addStretch()

    def _set_cat(self, cat):
        self._cur_cat = cat
        editable = self.exist_ord is None or self.edit_mode
        self._rebuild_cats(); self._rebuild_menu(editable)

    def _rebuild_menu(self, editable):
        while self.menu_grid.count():
            item = self.menu_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        t = APP.t()
        items = [m for m in APP.menu if m['on'] and (self._cur_cat=='all' or m['cat']==self._cur_cat)]
        for idx, m in enumerate(items):
            in_ord = next((x for x in self._items if x['mid']==m['id']),None)
            qty    = in_ord['qty'] if in_ord else 0
            name   = m['a'] if APP.lang=='ar' else m['e']
            b = QPushButton()
            # Bigger item cards + bigger text/prices
            b.setFixedSize(230,145)
            active_border = '#f59e0b' if qty>0 else '#1f2937'
            b.setStyleSheet(f"""QPushButton{{
              background:#111;border:2px solid {active_border};border-radius:14px;padding:8px;
              text-align:center; color:white;
            }}QPushButton:hover{{border-color:#f59e0b;}}""")
            vl = QVBoxLayout(b); vl.setSpacing(4); vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if qty>0:
                badge_lbl = QLabel(str(qty))
                badge_lbl.setStyleSheet('background:#f59e0b;color:white;border-radius:14px;font-size:18px;font-weight:bold;padding:0 8px;min-width:30px;max-width:34px;min-height:30px;max-height:34px;')
                badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                row = QHBoxLayout(); row.addStretch(); row.addWidget(badge_lbl)
                row_w = QWidget(); row_w.setStyleSheet('background:transparent;border:none;')
                row_w.setLayout(row); row_w.setFixedHeight(34)
                vl.addWidget(row_w)
            vl.addWidget(lbl(name,'white',16,True,Qt.AlignmentFlag.AlignCenter))
            vl.addWidget(lbl(f"{m['price']:.0f} {t['currency']}",'#f59e0b',18,True,Qt.AlignmentFlag.AlignCenter))
            if editable:
                b.clicked.connect(lambda _,mi=m: self._add_item(mi))
            # Use 3 columns still; cards are larger but scrollable
            self.menu_grid.addWidget(b, idx//3, idx%3)

    def _rebuild_items(self, editable):
        t = APP.t()
        while self.items_lay.count():
            item = self.items_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not self._items:
            self.items_lay.addStretch()
            empty = lbl(t['no_items'], '#4b5563', 12, False, Qt.AlignmentFlag.AlignCenter)
            self.items_lay.addWidget(empty, alignment=Qt.AlignmentFlag.AlignCenter)
            self.items_lay.addStretch()
            return

        for item in self._items:
            row_w = QWidget(); row_w.setStyleSheet('background:#111;border:1px solid #1f2937;border-radius:10px;')
            row_w.setFixedHeight(52)
            hl = QHBoxLayout(row_w); hl.setContentsMargins(10,0,10,0)
            name = item['a'] if APP.lang=='ar' else item['e']
            nl = lbl(name,'white',12,True); nl.setMaximumWidth(110)
            pl = lbl(f"{item['qty']*item['price']:.2f} {t['currency']}",'#f59e0b',12,True)
            hl.addWidget(nl); hl.addStretch(); hl.addWidget(pl)
            if editable:
                dec_b = QPushButton('−'); dec_b.setFixedSize(26,26)
                dec_b.setStyleSheet('QPushButton{background:#1c0510;color:#f43f5e;border:none;border-radius:13px;font-size:16px;font-weight:bold;}QPushButton:hover{background:#881337;}')
                qty_l = lbl(str(item['qty']),'white',12,True,Qt.AlignmentFlag.AlignCenter); qty_l.setFixedWidth(22)
                inc_b = QPushButton('+'); inc_b.setFixedSize(26,26)
                inc_b.setStyleSheet('QPushButton{background:#052e16;color:#22c55e;border:none;border-radius:13px;font-size:16px;font-weight:bold;}QPushButton:hover{background:#166534;}')
                dec_b.clicked.connect(lambda _,mid=item['mid']: self._dec(mid))
                inc_b.clicked.connect(lambda _,i=item: self._add_item({'id':i['mid'],'a':i['a'],'e':i['e'],'price':i['price'],'on':True}))
                hl.addWidget(dec_b); hl.addWidget(qty_l); hl.addWidget(inc_b)
            else:
                hl.addWidget(lbl(f"×{item['qty']}",'#4b5563',12,True))
            self.items_lay.addWidget(row_w)
        self.items_lay.addStretch()

    def _update_totals(self):
        t = APP.t()
        sub,svc,tax,tot = calc_order(self._items, APP.settings)
        has_items = len(self._items)>0
        self.sub_row.setVisible(has_items)
        self.svc_row.setVisible(has_items and APP.settings.get('service',0)>0)
        self.tax_row.setVisible(has_items and APP.settings.get('tax',0)>0)

        self.sub_row._l.setText(t['subtotal'])
        self.sub_row._v.setText(f"{sub:.2f} {t['currency']}")
        self.svc_row._l.setText(f"{t['service_lbl']} ({APP.settings.get('service',0):.0f}%)")
        self.svc_row._v.setText(f"+ {svc:.2f} {t['currency']}")
        self.tax_row._l.setText(f"{t['tax_lbl']} ({APP.settings.get('tax',0):.0f}%)")
        self.tax_row._v.setText(f"+ {tax:.2f} {t['currency']}")
        self.tot_row._l.setText(t['total'])
        self.tot_row._v.setText(f"{tot:.2f} {t['currency']}")

    def _update_buttons(self, is_new, editable, can_edit, can_pay, t):
        self.send_b.setText(f"🍳  {t['send_kitchen']}")
        self.save_b.setText(f"✅  {t['save_changes']}")
        self.edit_b.setText(f"✏️  {t['edit_order']}")
        self.cancl_b.setText(f"🗑️  {t['cancel_order']}")
        self.pay_b.setText(f"💳  {t['pay_now']}")

        self.send_b.setVisible(is_new and len(self._items)>0)
        self.save_b.setVisible(self.edit_mode and len(self._items)>0)
        self.edit_b.setVisible(can_edit and not self.edit_mode)
        self.cancl_b.setVisible(can_edit and not self.edit_mode)
        self.pay_b.setVisible(can_pay)

    # ── Actions ───────────────────────────────────────────────
    def _add_item(self, m):
        ex = next((x for x in self._items if x['mid']==m['id']),None)
        if ex: ex['qty'] += 1
        else: self._items.append(dict(mid=m['id'],a=m['a'],e=m['e'],qty=1,price=m['price']))
        editable = self.exist_ord is None or self.edit_mode
        self._rebuild_menu(editable); self._rebuild_items(editable); self._update_totals()
        self._update_buttons(self.exist_ord is None, editable,
                             self.exist_ord is not None and self.user_role in ('admin','cashier') and not self.edit_mode,
                             self.exist_ord is not None and self.user_role in ('admin','cashier') and self.exist_ord['status']=='ready' and not self.edit_mode,
                             APP.t())

    def _dec(self, mid):
        ex = next((x for x in self._items if x['mid']==mid),None)
        if not ex: return
        if ex['qty']>1: ex['qty']-=1
        else: self._items = [x for x in self._items if x['mid']!=mid]
        editable = self.exist_ord is None or self.edit_mode
        self._rebuild_menu(editable); self._rebuild_items(editable); self._update_totals()
        can_edit2 = self.exist_ord is not None and self.user_role in ('admin','cashier') and self.exist_ord['status'] not in ('paid',) and not self.edit_mode
        can_pay2  = self.exist_ord is not None and self.user_role in ('admin','cashier') and self.exist_ord['status']=='ready' and not self.edit_mode
        self._update_buttons(self.exist_ord is None, editable, can_edit2, can_pay2, APP.t())

    def _on_back(self):
        if self.edit_mode:
            self.edit_mode = False; self._items = copy.deepcopy(self.exist_ord['items'])
            self._rebuild_ui()
        else:
            self.go_back.emit()

    def _do_send(self):
        if not self._items: return
        sub,svc,tax,tot = calc_order(self._items, APP.settings)
        new_ord = dict(id=uid(), tableId=self.table['id'], items=copy.deepcopy(self._items),
                       status='pending', subtotal=sub, serviceAmt=svc, taxAmt=tax, total=tot,
                       createdAt=int(time.time()*1000), refunds=[])
        APP.orders.append(new_ord)
        tb = APP.tbl(self.table['id'])
        if tb: tb['status']='occupied'
        low = deduct_stock(self._items)
        persist_state()
        play_sound('new_order')
        msg = APP.t()['sent_ok']
        if low:
            msg += '  |  ' + APP.t()['low_stock_warning'] + ': ' + ', '.join(low)
        self.order_sent.emit(msg)

    def _do_enter_edit(self):
        self.edit_mode = True; self._items = copy.deepcopy(self.exist_ord['items'])
        self._rebuild_ui()

    def _do_save_edit(self):
        if not self._items or not self.exist_ord: return
        o = APP.ord(self.exist_ord['id'])
        if o:
            old_items = copy.deepcopy(o.get('items', []))
            new_items = copy.deepcopy(self._items)
            sub,svc,tax,tot = calc_order(new_items, APP.settings)

            o['items'] = new_items
            o['subtotal'] = sub
            o['serviceAmt'] = svc
            o['taxAmt'] = tax
            o['total'] = tot

            # If kitchen already started/finished, send only delta update and keep status.
            if o.get('status') in ('preparing', 'ready'):
                changes = diff_items(old_items, new_items)
                if changes:
                    o.setdefault('kitchenUpdates', []).append(
                        dict(id=uid(), createdAt=int(time.time()*1000), changes=changes, seen=False)
                    )
            else:
                # Not started yet: normal behavior (kitchen sees full updated order)
                o['status'] = 'pending'
            persist_state()
        self.order_sent.emit(APP.t()['order_updated'])

    def _do_cancel_order(self):
        if not self.exist_ord: return
        t = APP.t()
        reply = QMessageBox.question(self, t['cancel_order'], t['cancel_confirm'],
                                     QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return
        restore_stock(self.exist_ord.get('items', []))
        APP.orders = [o for o in APP.orders if o['id']!=self.exist_ord['id']]
        tb = APP.tbl(self.table['id'])
        if tb: tb['status']='free'
        persist_state()
        self.order_sent.emit(t['order_cancelled'])

    def _show_pay_dialog(self):
        if not self.exist_ord: return
        dlg = PayDialog(self.table, self.exist_ord, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            o = APP.ord(self.exist_ord['id'])
            if o:
                o['status']='paid'; o['paymentMethod']=dlg.method
                o['paidAt']=int(time.time()*1000)
            tb = APP.tbl(self.table['id'])
            if tb: tb['status']='free'
            persist_state()
            self.order_paid.emit(APP.t()['pay_ok'])

# ── Payment Dialog ─────────────────────────────────────────────
class PayDialog(QDialog):
    def __init__(self, table, order, parent=None):
        super().__init__(parent)
        self.method = 'cash'
        self._table = table
        self._order = order
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(f"{t['bill_for']} {table['id']}")
        self.setFixedSize(400,520); self.setStyleSheet('background:#111;')

        sub = order.get('subtotal', order.get('total',0))
        svc = order.get('serviceAmt',0); tax = order.get('taxAmt',0)
        tot = order.get('total',0)

        vl = QVBoxLayout(self); vl.setContentsMargins(24,24,24,24); vl.setSpacing(14)
        vl.addWidget(lbl(f"{t['bill_for']} {table['id']}",'white',17,True))

        # Items area
        items_w = card_widget('#0a0a0a','#1f2937',12); items_l = QVBoxLayout(items_w); items_l.setContentsMargins(14,12,14,12)
        for item in order['items']:
            n = item['a'] if APP.lang=='ar' else item['e']
            hl = QHBoxLayout()
            hl.addWidget(lbl(f"{n} × {item['qty']}",'#d1d5db',12))
            hl.addStretch()
            hl.addWidget(lbl(f"{item['qty']*item['price']:.2f} {t['currency']}",'#d1d5db',12))
            items_l.addLayout(hl)
        items_l.addWidget(divider())
        for label, val, color in [(t['subtotal'],f"{sub:.2f}",'#9ca3af'),
                                   (f"{t['service_lbl']} ({APP.settings.get('service',0):.0f}%)",f"+ {svc:.2f}",'#22c55e'),
                                   (f"{t['tax_lbl']} ({APP.settings.get('tax',0):.0f}%)",f"+ {tax:.2f}",'#38bdf8')]:
            if (('service' in label and svc==0) or ('tax' in label and tax==0)): continue
            hl = QHBoxLayout()
            hl.addWidget(lbl(label,color,12)); hl.addStretch(); hl.addWidget(lbl(val,color,12))
            items_l.addLayout(hl)
        items_l.addWidget(divider())
        hl = QHBoxLayout()
        hl.addWidget(lbl(t['total'],'white',15,True)); hl.addStretch()
        hl.addWidget(lbl(f"{tot:.2f} {t['currency']}",'#f59e0b',15,True))
        items_l.addLayout(hl)
        vl.addWidget(items_w)

        # Method
        method_row = QHBoxLayout(); method_row.setSpacing(10)
        self.cash_b = QPushButton(f"💵  {t['cash']}"); self.cash_b.setFixedHeight(40); self.cash_b.setCheckable(True); self.cash_b.setChecked(True)
        self.card_b = QPushButton(f"💳  {t['card']}"); self.card_b.setFixedHeight(40); self.card_b.setCheckable(True)
        for b in [self.cash_b, self.card_b]:
            b.setStyleSheet('QPushButton{background:#111;border:1.5px solid #374151;border-radius:10px;color:#6b7280;font-size:13px;font-weight:bold;padding:0 12px;}QPushButton:checked{border-color:#f59e0b;color:#f59e0b;background:#1c1500;}')
        self.cash_b.clicked.connect(lambda: self._set_method('cash'))
        self.card_b.clicked.connect(lambda: self._set_method('card'))
        method_row.addWidget(self.cash_b); method_row.addWidget(self.card_b)
        vl.addLayout(method_row)

        # Cash input
        self.cash_section = QWidget(); self.cash_section.setStyleSheet('background:transparent;border:none;')
        cvl = QVBoxLayout(self.cash_section); cvl.setContentsMargins(0,0,0,0); cvl.setSpacing(6)
        cvl.addWidget(lbl(t['received'],'#6b7280',11))
        self.recv_in = QLineEdit(); self.recv_in.setPlaceholderText(f"{tot:.2f}")
        self.recv_in.setAlignment(Qt.AlignmentFlag.AlignCenter); self.recv_in.setFixedHeight(46)
        self.recv_in.textChanged.connect(lambda v: self._update_change(v,tot))
        cvl.addWidget(self.recv_in)
        self.change_l = lbl('','#22c55e',14,True)
        cvl.addWidget(self.change_l)
        vl.addWidget(self.cash_section)

        # PDF / Print
        out_row = QHBoxLayout(); out_row.setSpacing(10)
        pdf_b = btn(f"📄  {t['save_pdf']}", 'amber', 40, 12)
        prn_b = btn(f"🖨️  {t['print_invoice']}", 'sky', 40, 12)
        pdf_b.clicked.connect(lambda: self._save_pdf(tot))
        prn_b.clicked.connect(lambda: self._print_invoice(tot))
        out_row.addWidget(pdf_b); out_row.addWidget(prn_b)
        vl.addLayout(out_row)

        # Buttons
        btns_row = QHBoxLayout(); btns_row.setSpacing(10)
        cancel_b = btn(t['cancel'],'gray',42,13)
        cancel_b.clicked.connect(self.reject)
        confirm_b = btn(f"✅  {t['confirm_payment']}",'green',42,13)
        confirm_b.clicked.connect(self.accept)
        btns_row.addWidget(cancel_b); btns_row.addWidget(confirm_b)
        vl.addLayout(btns_row)

    def _set_method(self, m):
        self.method = m
        self.cash_b.setChecked(m=='cash'); self.card_b.setChecked(m=='card')
        self.cash_section.setVisible(m=='cash')

    def _update_change(self, val, tot):
        t = APP.t()
        try:
            ch = float(val) - tot
            if ch>=0: self.change_l.setText(f"{t['change_lbl']}: {ch:.2f} {t['currency']}")
            else: self.change_l.setText('')
        except: self.change_l.setText('')

    def _invoice_html(self, tot):
        t = APP.t()
        order = self._order
        table = self._table
        rtl = (APP.lang == 'ar')
        sub = order.get('subtotal', order.get('total', 0))
        svc = order.get('serviceAmt', 0)
        tax = order.get('taxAmt', 0)
        created_ts = order.get('createdAt', int(time.time()*1000))
        paid_ts = order.get('paidAt')
        created = fmt_time(created_ts)
        paid_at = fmt_time(paid_ts) if paid_ts else ''
        inv_no = str(order.get('id', ''))
        cashier = (APP.user.get('name') if isinstance(getattr(APP, 'user', None), dict) else '') or ''
        method = order.get('paymentMethod', '')

        rows = []
        for it in order.get('items', []):
            name = it.get('a', '') if APP.lang == 'ar' else it.get('e', '')
            qty = it.get('qty', 0)
            price = it.get('price', 0)
            total_line = qty * price
            if rtl:
                # Visual order (right->left): Item | Qty | Price | Total
                # Achieved by rendering LTR with reversed columns (Total | Price | Qty | Item)
                rows.append(
                    "<tr>"
                    f"<td class='amt'>{total_line:.2f}</td>"
                    f"<td class='price'>{price:.2f}</td>"
                    f"<td class='qty'>{qty}</td>"
                    f"<td class='item'>{name}</td>"
                    "</tr>"
                )
            else:
                rows.append(
                    "<tr>"
                    f"<td class='item'>{name}</td>"
                    f"<td class='qty'>{qty}</td>"
                    f"<td class='price'>{price:.2f}</td>"
                    f"<td class='amt'>{total_line:.2f}</td>"
                    "</tr>"
                )
        rows_html = "\n".join(rows) or "<tr><td class='empty' colspan='4'>—</td></tr>"

        direction = 'rtl' if rtl else 'ltr'
        # For Arabic, we render the table LTR with reversed columns to match the exact
        # receipt column order (rightmost item, leftmost total).
        body_cls = 'rtl' if rtl else 'ltr'
        table_dir = 'ltr' if rtl else direction
        th_item = 'اسم الصنف' if rtl else 'Item'
        th_qty = 'كمية' if rtl else 'Qty'
        th_price = 'السعر' if rtl else 'Price'
        th_amt = 'الإجمالي' if rtl else 'Total'
        sub_lbl = 'المجموع الجزئي' if rtl else t['subtotal']
        svc_lbl = t['service_lbl']
        tax_lbl = t['tax_lbl']
        tot_lbl = t['total']
        font_stack = "Segoe UI, Tahoma, Arial, sans-serif"
        num_font = "Consolas, 'Segoe UI', Tahoma, Arial, sans-serif"
        thank_you = "شكراً لزيارتكم" if rtl else "Thank you"

        # Totals rows rendered inside the same grid (like the sample receipt).
        if rtl:
            vat_lbl = f"ضريبة القيمة المضافة {APP.settings.get('tax',0):.0f}%"
            totals_html = (
                f"<tr class='sumrow'><td class='amt'>{sub:.0f} {t['currency']}</td><td class='lbl' colspan='3'>{sub_lbl}</td></tr>"
                f"<tr class='sumrow'><td class='amt'>{svc:.0f} {t['currency']}</td><td class='lbl' colspan='3'>{svc_lbl} {APP.settings.get('service',0):.0f}%</td></tr>"
                f"<tr class='sumrow'><td class='amt'>{tax:.0f} {t['currency']}</td><td class='lbl' colspan='3'>{vat_lbl}</td></tr>"
                f"<tr class='sumrow grand'><td class='amt'>{tot:.0f} {t['currency']}</td><td class='lbl' colspan='3'>{tot_lbl}</td></tr>"
            )
        else:
            totals_html = (
                f"<tr class='sumrow'><td class='blank' colspan='2'></td><td class='lbl'>{sub_lbl}</td><td class='amt'>{sub:.2f} {t['currency']}</td></tr>"
                f"<tr class='sumrow'><td class='blank' colspan='2'></td><td class='lbl'>{svc_lbl} {APP.settings.get('service',0):.0f}%</td><td class='amt'>{svc:.2f} {t['currency']}</td></tr>"
                f"<tr class='sumrow'><td class='blank' colspan='2'></td><td class='lbl'>{tax_lbl} {APP.settings.get('tax',0):.0f}%</td><td class='amt'>{tax:.2f} {t['currency']}</td></tr>"
                f"<tr class='sumrow grand'><td class='blank' colspan='2'></td><td class='lbl'>{tot_lbl}</td><td class='amt'>{tot:.2f} {t['currency']}</td></tr>"
            )

        return f"""
        <html>
          <head>
            <meta charset="utf-8"/>
            <style>
              @page {{ size: A4; margin: 12mm; }}
              body {{ font-family: {font_stack}; font-size: 12.5px; color: #111; text-align: center; }}
              .receipt {{ width: 80mm; margin: 0 auto; display: inline-block; text-align: {('right' if rtl else 'left')}; direction: {direction}; }}
              .center {{ text-align: center; }}
              .muted {{ color: #555; }}
              .h1 {{ font-size: 18px; font-weight: 800; margin: 0; }}
              .sub {{ font-size: 12px; margin-top: 4px; }}
              .hr {{ border-top: 1px dashed #999; margin: 10px 0; }}
              .meta {{ font-size: 12px; line-height: 1.5; width: 100%; }}
              .meta table {{ width: 100%; border: none; border-collapse: collapse; }}
              .meta td {{ border: none; padding: 2px 0; }}
              .meta .k {{ color: #555; }}
              .meta .v {{ font-family: {num_font}; }}

              /* Excel-like grid (exact like the sample) */
              table.items {{ width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #000; }}
              thead th {{
                font-size: 12px; padding: 7px 6px;
                border: 1px solid #000; background: #fff; color: #111; font-weight: 800;
              }}
              tbody td {{
                padding: 8px 6px; border: 1px solid #000; vertical-align: middle;
              }}
              td.item {{ width: 44%; }}
              td.qty  {{ width: 14%; text-align: center; font-family: {num_font}; }}
              td.price{{ width: 21%; text-align: center; font-family: {num_font}; }}
              td.amt  {{ width: 21%; text-align: center; font-family: {num_font}; font-weight: 700; }}
              td.empty {{ text-align: center; color: #777; padding: 10px 0; }}
              td.lbl {{ text-align: center; font-weight: 700; }}
              td.blank {{ background: #fff; }}
              tr.sumrow td {{ padding: 10px 6px; }}
              tr.sumrow.grand td {{ font-size: 14px; font-weight: 900; }}

              /* Match the exact RTL grid order like the sample receipt */
              table.items {{ direction: {table_dir}; }}
              table.items thead th {{ text-align: center; }}
              body.rtl table.items thead th.item_h {{ text-align: right; }}
              body.ltr table.items thead th.item_h {{ text-align: left; }}
              body.rtl td.item {{ text-align: right; }}
              body.ltr td.item {{ text-align: left; }}

              table.items {{ margin: 0; }}
              .footer {{ margin-top: 14px; }}
            </style>
          </head>
          <body class="{body_cls}">
            <div class="receipt">
              <div class="center">
                <div class="h1">{t['app_name']}</div>
                <div class="sub muted">{t['bill_for']} {table.get('id','?')}</div>
              </div>

              <div class="hr"></div>

              <div class="meta">
                <table>
                  {f"<tr><td class='k'>رقم الفاتورة</td><td class='v' style='text-align:left'>{inv_no}</td></tr>" if (rtl and inv_no) else ""}
                  {f"<tr><td class='k'>Invoice #</td><td class='v' style='text-align:right'>{inv_no}</td></tr>" if ((not rtl) and inv_no) else ""}
                  <tr><td class='k'>{'التاريخ' if rtl else 'Date'}</td><td class='v' style='text-align:{'left' if rtl else 'right'}'>{created}</td></tr>
                  {f"<tr><td class='k'>{'وقت الدفع' if rtl else 'Paid'}</td><td class='v' style='text-align:{'left' if rtl else 'right'}'>{paid_at}</td></tr>" if paid_at else ""}
                  {f"<tr><td class='k'>{'الكاشير' if rtl else 'Cashier'}</td><td class='v' style='text-align:{'left' if rtl else 'right'}'>{cashier}</td></tr>" if cashier else ""}
                  {f"<tr><td class='k'>{'طريقة الدفع' if rtl else 'Method'}</td><td class='v' style='text-align:{'left' if rtl else 'right'}'>{method}</td></tr>" if method else ""}
                </table>
              </div>

              <div class="hr"></div>

              <table class="items">
                <thead>
                  <tr>
                    {(
                      f"<th style='text-align:center'>{th_amt}</th>"
                      f"<th style='text-align:center'>{th_price}</th>"
                      f"<th style='text-align:center'>{th_qty}</th>"
                      f"<th class='item_h'>{th_item}</th>"
                    ) if rtl else (
                      f"<th class='item_h'>{th_item}</th>"
                      f"<th style='text-align:center'>{th_qty}</th>"
                      f"<th style='text-align:center'>{th_price}</th>"
                      f"<th style='text-align:center'>{th_amt}</th>"
                    )}
                  </tr>
                </thead>
                <tbody>
                  {rows_html}
                  {totals_html}
                </tbody>
              </table>

              <div class="hr"></div>

              <div class="footer center muted">{thank_you}</div>
            </div>
          </body>
        </html>
        """

    def _configure_invoice_printer(self, printer: QPrinter):
        # Keep this defensive: printing backends vary and can throw.
        try:
            printer.setResolution(300)
        except Exception:
            pass
        try:
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        except Exception:
            pass
        try:
            printer.setPageMargins(QMarginsF(12, 12, 12, 12), QPageLayout.Unit.Millimeter)
        except Exception:
            try:
                printer.setPageMargins(QMarginsF(12, 12, 12, 12))
            except Exception:
                pass

    def _print_doc_to_printer(self, tot, printer: QPrinter):
        self._configure_invoice_printer(printer)
        doc = QTextDocument()
        try:
            doc.setDefaultFont(QFont("Segoe UI", 11))
        except Exception:
            pass
        doc.setHtml(self._invoice_html(tot))
        # Ensure the document is laid out for the printer page size to avoid odd scaling.
        try:
            page = printer.pageRect(QPrinter.Unit.Point)
            doc.setPageSize(QSizeF(page.size()))
        except Exception:
            pass
        # PyQt6 uses `print()`; some bindings expose `print_()` for compatibility.
        if hasattr(doc, "print"):
            doc.print(printer)
        else:
            doc.print_(printer)

    def _save_pdf(self, tot):
        t = APP.t()
        oid = str(self._order.get('id', '') or '')
        default_name = f"invoice_order_{oid}_table_{self._table.get('id','')}_{fmt_date(int(time.time()*1000))}.pdf" if oid else f"invoice_table_{self._table.get('id','')}_{fmt_date(int(time.time()*1000))}.pdf"
        fn, _ = QFileDialog.getSaveFileName(self, t['save_pdf'], default_name, "PDF (*.pdf)")
        if not fn:
            return
        if not fn.lower().endswith('.pdf'):
            fn += '.pdf'
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        try:
            if oid:
                printer.setDocName(f"Order {oid}")
        except Exception:
            pass
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(fn)
        try:
            self._print_doc_to_printer(tot, printer)
        except Exception as e:
            QMessageBox.critical(self, t['save_pdf'], f"{t['save_pdf']}\n\n{e}")

    def _print_invoice(self, tot):
        t = APP.t()
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        oid = str(self._order.get('id', '') or '')
        try:
            if oid:
                printer.setDocName(f"Order {oid}")
        except Exception:
            pass
        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._print_doc_to_printer(tot, printer)
        except Exception as e:
            QMessageBox.critical(self, t['print_invoice'], f"{t['print_invoice']}\n\n{e}")

# ══════════════════════════════════════════════════════════════
#  KITCHEN SCREEN
# ══════════════════════════════════════════════════════════════
class KitchenScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)
        self.title  = lbl('','white',20,True); vl.addWidget(self.title)
        self.badge_l= lbl('','#f97316',13,True); vl.addWidget(self.badge_l)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.ctn = QWidget(); self.ctn.setStyleSheet('background:transparent;')
        self.grid= QGridLayout(self.ctn); self.grid.setSpacing(14); self.grid.setContentsMargins(0,0,0,0)
        sc.setWidget(self.ctn); vl.addWidget(sc)

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"👨‍🍳  {t['nav']['kitchen']}")
        active = []
        for o in APP.orders:
            has_unseen = any((not u.get('seen')) for u in o.get('kitchenUpdates', []))
            if o['status'] in ('pending', 'preparing') or has_unseen:
                active.append(o)
        n = len(active)
        self.badge_l.setText(f"{n} {t['queue1'] if n==1 else t['queueN']}")

        while self.grid.count():
            i = self.grid.takeAt(0)
            if i.widget(): i.widget().deleteLater()

        if not active:
            self.grid.addWidget(lbl(f"✅  {t['no_orders']}",'#4b5563',14,True,Qt.AlignmentFlag.AlignCenter),0,0)
            return

        # Bigger cards / larger text: use 2 columns instead of 3
        cols = 2
        for idx,o in enumerate(active):
            self.grid.addWidget(self._mk_card(o,t), idx//cols, idx%cols)

    def _mk_card(self, o, t):
        tbl   = APP.tbl(o['tableId'])
        mins  = elapsed_m(o['createdAt'])
        urgent= mins>15
        is_pend = o['status']=='pending'
        hdr_bg  = '#c2410c' if is_pend else '#0c4a6e'
        border  = '#ea580c' if is_pend else '#0369a1'

        card = card_widget('#111', border, 16)
        card.setMinimumSize(520, 420)
        vl   = QVBoxLayout(card); vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setFixedHeight(86)
        hdr.setStyleSheet(f'background:{hdr_bg};border-top-left-radius:14px;border-top-right-radius:14px;')
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(14,0,14,0)
        hl.addWidget(lbl(f"{t['table']} {tbl['id'] if tbl else '?'}",'white',28,True))
        hl.addStretch()
        time_color = '#fca5a5' if urgent else 'white'
        hl.addWidget(lbl(f"{fmt_time(o['createdAt'])} • {mins}{t['mins']}",time_color,20,True))
        hl.addWidget(status_badge(o['status'], t, fs=18, h=38))
        vl.addWidget(hdr)

        # Items
        body = QWidget(); body.setStyleSheet('background:transparent;border:none;')
        bvl  = QVBoxLayout(body); bvl.setContentsMargins(18,16,18,16); bvl.setSpacing(14)

        unseen = [u for u in o.get('kitchenUpdates', []) if not u.get('seen')]
        if unseen:
            agg = {}
            for u in unseen:
                for ch in u.get('changes', []):
                    mid = ch.get('mid')
                    if mid is None:
                        continue
                    if mid not in agg:
                        agg[mid] = dict(mid=mid, a=ch.get('a', ''), e=ch.get('e', ''), delta=0)
                    agg[mid]['delta'] += int(ch.get('delta', 0))

            upd_w = card_widget('#0a0a0a', '#854d0e', 12)
            upd_l = QVBoxLayout(upd_w); upd_l.setContentsMargins(10,8,10,8); upd_l.setSpacing(4)
            upd_l.addWidget(lbl(f"✏️  {t['kitchen_updates']}", '#f59e0b', 20, True))
            for ch in [x for x in agg.values() if x.get('delta')]:
                name = ch['a'] if APP.lang == 'ar' else ch['e']
                d = int(ch['delta'])
                sign = '+' if d > 0 else '−'
                color = '#22c55e' if d > 0 else '#f43f5e'
                hl_u = QHBoxLayout()
                hl_u.addWidget(lbl(name, '#e5e7eb', 19, True))
                hl_u.addStretch()
                hl_u.addWidget(lbl(f"{sign} {abs(d)}", color, 20, True))
                upd_l.addLayout(hl_u)
            bvl.addWidget(upd_w)
            bvl.addWidget(divider())

        for item in o['items']:
            # Item row (bigger text + separator line for clarity)
            hl2 = QHBoxLayout()
            hl2.addWidget(lbl(item['a'] if APP.lang=='ar' else item['e'],'#e5e7eb',30,True))
            hl2.addStretch()
            hl2.addWidget(lbl(f"× {item['qty']}",'#9ca3af',30,True))
            bvl.addLayout(hl2)

            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet('background:#1f2937; border:none; max-height:1px;')
            bvl.addWidget(sep)
        vl.addWidget(body, stretch=1)

        # Action button
        action = None
        if o['status'] == 'pending':
            action = btn(f"🍳  {t['mark_preparing']}", 'sky', 64, 18)
            action.clicked.connect(lambda _, oid=o['id']: self._update(oid, 'preparing'))
        elif o['status'] == 'preparing':
            action = btn(f"✅  {t['mark_ready']}", 'green', 64, 18)
            action.clicked.connect(lambda _, oid=o['id']: self._update(oid, 'ready'))
        elif unseen:
            action = btn(f"✅  {t['ack_updates']}", 'amber', 64, 18)
            action.clicked.connect(lambda _, oid=o['id']: self._ack_updates(oid))
        foot = QWidget(); foot.setStyleSheet('background:transparent;border:none;')
        fvl2 = QVBoxLayout(foot); fvl2.setContentsMargins(10,0,10,10)
        if action:
            fvl2.addWidget(action)
            vl.addWidget(foot)
        return card

    def _update(self, oid, status):
        o = APP.ord(oid)
        if o: o['status'] = status
        if status == 'ready':
            play_sound('order_ready')
        persist_state()
        self.refresh()

    def _ack_updates(self, oid):
        o = APP.ord(oid)
        if not o:
            return
        for u in o.get('kitchenUpdates', []):
            u['seen'] = True
        persist_state()
        self.refresh()

# ══════════════════════════════════════════════════════════════
#  MENU MANAGEMENT SCREEN
# ══════════════════════════════════════════════════════════════
class MenuScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)
        self.title = lbl('','white',20,True); vl.addWidget(self.title)
        hl = QHBoxLayout(); hl.addStretch()
        self.add_b = btn('','amber',38,12); self.add_b.clicked.connect(self._add); hl.addWidget(self.add_b)
        vl.addLayout(hl)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.ctn = QWidget(); self.ctn.setStyleSheet('background:transparent;')
        self.body= QVBoxLayout(self.ctn); self.body.setContentsMargins(0,0,0,0); self.body.setSpacing(12)
        sc.setWidget(self.ctn); vl.addWidget(sc)

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"🍴  {t['nav']['menu']}")
        self.add_b.setText(f"+  {t['add_item']}")
        while self.body.count():
            i = self.body.takeAt(0)
            if i.widget(): i.widget().deleteLater()

        for cat in CATS:
            cat_items = [m for m in APP.menu if m['cat']==cat]
            if not cat_items: continue
            cat_name = cat if APP.lang=='ar' else t['cat_names'].get(cat,cat)
            sec = QLabel(cat_name.upper())
            sec.setStyleSheet('color:#4b5563;font-size:10px;font-weight:bold;letter-spacing:2px;background:transparent;border:none;')
            self.body.addWidget(sec)
            card = card_widget(); cl = QVBoxLayout(card); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
            for idx,m in enumerate(cat_items):
                if idx>0: cl.addWidget(divider())
                cl.addWidget(self._mk_row(m,t))
            self.body.addWidget(card)
        self.body.addStretch()

    def _mk_row(self, m, t):
        w = QWidget(); w.setFixedHeight(52); w.setStyleSheet('background:transparent;border:none;')
        hl= QHBoxLayout(w); hl.setContentsMargins(16,0,16,0)
        dot = QLabel('●'); dot.setStyleSheet(f"color:{'#22c55e' if m['on'] else '#374151'};font-size:10px;background:transparent;border:none;"); dot.setFixedWidth(16)
        name= m['a'] if APP.lang=='ar' else m['e']
        alt = m['e'] if APP.lang=='ar' else m['a']
        vl2 = QVBoxLayout()
        vl2.addWidget(lbl(name,'white',13,True))
        vl2.addWidget(lbl(alt,'#4b5563',10))
        price_l = lbl(f"{m['price']:.0f} {t['currency']}",'#f59e0b',13,True)
        avail_b = QPushButton(t['available'] if m['on'] else t['unavailable'])
        avail_b.setFixedSize(80,26)
        col = '#166534' if m['on'] else '#374151'; fg2 = '#22c55e' if m['on'] else '#6b7280'
        avail_b.setStyleSheet(f'QPushButton{{background:transparent;border:1px solid {col};border-radius:13px;color:{fg2};font-size:11px;font-weight:bold;}}QPushButton:hover{{background:{col};}}')
        avail_b.clicked.connect(lambda _,mi=m: self._toggle(mi['id']))
        edit_b = btn(t['edit_item'],'sky',28,11); edit_b.setFixedWidth(60)
        edit_b.clicked.connect(lambda _,mi=m: self._edit(mi))
        del_b  = btn(t['del_item'],'rose',28,11); del_b.setFixedWidth(60)
        del_b.clicked.connect(lambda _,mi=m: self._del(mi['id']))
        hl.addWidget(dot); hl.addLayout(vl2); hl.addStretch()
        hl.addWidget(price_l); hl.addSpacing(8)
        hl.addWidget(avail_b); hl.addSpacing(6)
        hl.addWidget(edit_b);  hl.addSpacing(4)
        hl.addWidget(del_b)
        return w

    def _toggle(self, mid):
        m = next((x for x in APP.menu if x['id']==mid),None)
        if m: m['on']=not m['on']
        self.refresh()

    def _del(self, mid):
        t = APP.t()
        if QMessageBox.question(self,t['del_item'],t['del_confirm'],QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            APP.menu = [m for m in APP.menu if m['id']!=mid]
            self.refresh()

    def _add(self): self._open_form(None)
    def _edit(self, m): self._open_form(m)

    def _open_form(self, m):
        dlg = MenuItemDialog(m, self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if m:
                for key,val in data.items(): m[key]=val
            else:
                data['id']=uid(); data['on']=True
                APP.menu.append(data)
            self.refresh()

class MenuItemDialog(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(t['edit_item'] if item else t['add_item'])
        self.setFixedSize(380,360); self.setStyleSheet('background:#111;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,24,24,24); vl.setSpacing(12)
        vl.addWidget(lbl(t['edit_item'] if item else t['add_item'],'white',17,True))
        vl.addWidget(lbl(t['item_ar'],'#6b7280',11))
        self.ar_in = QLineEdit(item['a'] if item else ''); vl.addWidget(self.ar_in)
        vl.addWidget(lbl(t['item_en'],'#6b7280',11))
        self.en_in = QLineEdit(item['e'] if item else ''); self.en_in.setLayoutDirection(Qt.LayoutDirection.LeftToRight); vl.addWidget(self.en_in)
        vl.addWidget(lbl(t['category'],'#6b7280',11))
        self.cat_cb = QComboBox()
        for c in CATS: self.cat_cb.addItem(c if APP.lang=='ar' else t['cat_names'].get(c,c), c)
        if item:
            idx = CATS.index(item['cat']) if item['cat'] in CATS else 0
            self.cat_cb.setCurrentIndex(idx)
        vl.addWidget(self.cat_cb)
        vl.addWidget(lbl(f"{t['price']} ({t['currency']})  " if 'price' in t else f"{t['currency']}  ",'#6b7280',11))
        self.price_in = QLineEdit(str(int(item['price'])) if item else ''); self.price_in.setLayoutDirection(Qt.LayoutDirection.LeftToRight); vl.addWidget(self.price_in)
        btns = QHBoxLayout(); btns.setSpacing(10)
        ok_b = btn(t['save'],'amber',42,13); ok_b.clicked.connect(self.accept)
        cancel_b = btn(t['cancel'],'gray',42,13); cancel_b.clicked.connect(self.reject)
        btns.addWidget(cancel_b); btns.addWidget(ok_b)
        vl.addLayout(btns)

    def get_data(self):
        return dict(
            a=self.ar_in.text().strip(),
            e=self.en_in.text().strip(),
            cat=self.cat_cb.currentData(),
            price=float(self.price_in.text() or '0'),
        )

# ══════════════════════════════════════════════════════════════
#  SETTINGS SCREEN
# ══════════════════════════════════════════════════════════════
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  IMPORT / EXPORT SCREEN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class ImportExportScreen(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.title = lbl('', 'white', 20, True)
        root.addWidget(self.title)

        summary_card = card_widget('#111', '#1f2937', 14)
        summary_lay = QVBoxLayout(summary_card)
        summary_lay.setContentsMargins(18, 14, 18, 14)
        summary_lay.setSpacing(10)
        self.summary_title = lbl('', 'white', 15, True)
        self.summary_note = lbl('', '#6b7280', 12)
        summary_lay.addWidget(self.summary_title)
        summary_lay.addWidget(self.summary_note)
        summary_lay.addWidget(divider())
        stats_w = QWidget(); stats_w.setStyleSheet('background:transparent;border:none;')
        stats = QGridLayout(stats_w); stats.setContentsMargins(0, 4, 0, 0); stats.setSpacing(10)
        self.stat_labels = {}
        stat_defs = [('tables', '#0f172a'), ('menu', '#052e16'), ('orders', '#1c1500'),
                     ('reservations', '#0c1a27'), ('stock', '#111827')]
        for idx, (key, bg) in enumerate(stat_defs):
            card = card_widget(bg, '#1f2937', 12)
            vl = QVBoxLayout(card)
            vl.setContentsMargins(14, 12, 14, 12)
            vl.setSpacing(2)
            self.stat_labels[key] = lbl('0', 'white', 20, True)
            self.stat_labels[f'{key}_name'] = lbl('', '#9ca3af', 11)
            vl.addWidget(self.stat_labels[f'{key}_name'])
            vl.addWidget(self.stat_labels[key])
            stats.addWidget(card, idx // 3, idx % 3)
        summary_lay.addWidget(stats_w)
        root.addWidget(summary_card)

        export_card = card_widget('#052e16', '#166534', 14)
        export_lay = QVBoxLayout(export_card)
        export_lay.setContentsMargins(18, 14, 18, 14)
        export_lay.setSpacing(8)
        self.export_title = lbl('', 'white', 15, True)
        self.export_note = lbl('', '#bbf7d0', 12)
        self.export_path = lbl('', '#86efac', 11)
        self.export_b = btn('', 'green', 46, 14)
        self.export_b.clicked.connect(self._export_backup)
        export_lay.addWidget(self.export_title)
        export_lay.addWidget(self.export_note)
        export_lay.addWidget(self.export_path)
        export_lay.addWidget(self.export_b)
        root.addWidget(export_card)

        import_card = card_widget('#1c1500', '#854d0e', 14)
        import_lay = QVBoxLayout(import_card)
        import_lay.setContentsMargins(18, 14, 18, 14)
        import_lay.setSpacing(8)
        self.import_title = lbl('', 'white', 15, True)
        self.import_note = lbl('', '#fde68a', 12)
        self.import_b = btn('', 'orange', 46, 14)
        self.import_b.clicked.connect(self._import_backup)
        self.status_l = lbl('', '#9ca3af', 11)
        import_lay.addWidget(self.import_title)
        import_lay.addWidget(self.import_note)
        import_lay.addWidget(self.import_b)
        import_lay.addWidget(self.status_l)
        root.addWidget(import_card)

        root.addStretch(1)
        self.refresh()

    def refresh(self):
        t = APP.t()
        rtl = APP.lang == 'ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"💾  {t['nav']['import_export']}")
        self.summary_title.setText('Backup summary' if APP.lang == 'en' else 'ملخص النسخة الاحتياطية')
        self.summary_note.setText('Current data that will be exported or replaced on import.' if APP.lang == 'en'
                                  else 'البيانات الحالية التي سيتم تصديرها أو استبدالها عند الاستيراد.')
        counts = dict(
            tables=len(APP.tables),
            menu=len(APP.menu),
            orders=len(APP.orders),
            reservations=len(APP.reservations),
            stock=len(APP.stock),
        )
        labels = {
            'tables': 'Tables' if APP.lang == 'en' else 'الطاولات',
            'menu': 'Menu items' if APP.lang == 'en' else 'أصناف المنيو',
            'orders': 'Orders' if APP.lang == 'en' else 'الطلبات',
            'reservations': 'Reservations' if APP.lang == 'en' else 'الحجوزات',
            'stock': 'Stock records' if APP.lang == 'en' else 'سجلات المخزون',
        }
        for key, val in counts.items():
            self.stat_labels[key].setText(str(val))
            self.stat_labels[f'{key}_name'].setText(labels[key])
        self.export_title.setText('Export a full backup' if APP.lang == 'en' else 'تصدير نسخة احتياطية كاملة')
        self.export_note.setText('Creates a JSON file with tables, menu, orders, settings, stock, reservations, and sound.'
                                 if APP.lang == 'en'
                                 else 'ينشئ ملف JSON يحتوي على الطاولات والمنيو والطلبات والإعدادات والمخزون والحجوزات والصوت.')
        self.export_b.setText('  Export backup' if APP.lang == 'en' else '  تصدير النسخة')
        self.export_path.setText('')
        self.import_title.setText('Import a backup' if APP.lang == 'en' else 'استيراد نسخة احتياطية')
        self.import_note.setText('Select a JSON backup to restore the app state.' if APP.lang == 'en'
                                 else 'اختر ملف JSON لاسترجاع حالة التطبيق.')
        self.import_b.setText('  Import backup' if APP.lang == 'en' else '  استيراد النسخة')
        self.status_l.setText('')

    def _export_backup(self):
        t = APP.t()
        default_name = f"restaurant-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            t['nav']['import_export'],
            default_name,
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        if not path.lower().endswith('.json'):
            path += '.json'
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(_export_payload(), fh, ensure_ascii=False, indent=2)
        except Exception as exc:
            QMessageBox.critical(self, t['nav']['import_export'], str(exc))
            return
        self.export_path.setText(path)
        self.status_l.setText('Backup exported successfully.' if APP.lang == 'en' else 'تم تصدير النسخة بنجاح.')
        QMessageBox.information(self, t['nav']['import_export'], self.status_l.text())

    def _import_backup(self):
        t = APP.t()
        path, _ = QFileDialog.getOpenFileName(
            self,
            t['nav']['import_export'],
            '',
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                payload = json.load(fh)
            state = _extract_import_state(payload)
        except Exception as exc:
            QMessageBox.critical(self, t['nav']['import_export'], str(exc))
            return

        confirm_text = (
            f"This will replace the current data with the backup from:\n{path}\n\nContinue?"
            if APP.lang == 'en'
            else f"سيتم استبدال البيانات الحالية بالنسخة الموجودة في:\n{path}\n\nهل تريد المتابعة؟"
        )
        if QMessageBox.question(self, t['nav']['import_export'], confirm_text) != QMessageBox.StandardButton.Yes:
            return

        try:
            _apply_state(state)
            persist_state()
        except Exception as exc:
            QMessageBox.critical(self, t['nav']['import_export'], str(exc))
            return

        self.status_l.setText('Backup imported successfully.' if APP.lang == 'en' else 'تم استيراد النسخة بنجاح.')
        self.data_changed.emit()
        QMessageBox.information(self, t['nav']['import_export'], self.status_l.text())

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')

        root = QVBoxLayout(self)
        root.setContentsMargins(24,20,24,20)
        root.setSpacing(16)

        self.title = lbl('','white',20,True)
        root.addWidget(self.title)

        # Make settings scrollable to avoid clipped/odd sizing on smaller windows.
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setStyleSheet('background:transparent;border:none;')
        ctn = QWidget()
        ctn.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(ctn)
        vl.setContentsMargins(0,0,0,0)
        vl.setSpacing(16)
        sc.setWidget(ctn)
        root.addWidget(sc, stretch=1)

        # Tables management (admin only)
        self.tables_card = card_widget('#111', '#1f2937', 14)
        tm_vl = QVBoxLayout(self.tables_card); tm_vl.setContentsMargins(18,14,18,14); tm_vl.setSpacing(10)
        self.tables_title = lbl('', 'white', 15, True); tm_vl.addWidget(self.tables_title)
        tm_vl.addWidget(divider())
        row = QWidget(); row.setStyleSheet('background:transparent;border:none;')
        row_l = QHBoxLayout(row); row_l.setContentsMargins(0,0,0,0); row_l.setSpacing(10)
        self.tbl_combo = QComboBox()
        self.tbl_combo.setMinimumHeight(48)
        self.tbl_combo.setStyleSheet('font-size:14px;')
        self.seats_spin = QSpinBox(); self.seats_spin.setRange(1, 20); self.seats_spin.setValue(4)
        self.seats_spin.setFixedSize(140, 48); self.seats_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seats_spin.setStyleSheet('font-size:14px; font-weight:bold;')
        self.add_tbl_b = btn('', 'amber', 48, 13)
        self.rm_tbl_b  = btn('', 'rose',  48, 13)
        self.add_tbl_b.clicked.connect(self._add_table)
        self.rm_tbl_b.clicked.connect(self._remove_table)
        row_l.addWidget(self.tbl_combo, stretch=1)
        row_l.addWidget(self.seats_spin)
        row_l.addWidget(self.add_tbl_b)
        row_l.addWidget(self.rm_tbl_b)
        tm_vl.addWidget(row)
        vl.addWidget(self.tables_card)
        # Service
        svc_card = card_widget('#052e16','#166534',14); svl = QVBoxLayout(svc_card); svl.setContentsMargins(18,14,18,14)
        hl_s = QHBoxLayout()
        sv_info = QVBoxLayout()
        self.svc_lbl = lbl('','white',15,True); self.svc_note = lbl('','#6b7280',12)
        sv_info.addWidget(self.svc_lbl); sv_info.addWidget(self.svc_note)
        self.svc_spin = QDoubleSpinBox(); self.svc_spin.setRange(0,100); self.svc_spin.setSingleStep(0.5); self.svc_spin.setDecimals(1)
        self.svc_spin.setFixedSize(120,54); self.svc_spin.setSuffix(' %')
        self.svc_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl_s.addLayout(sv_info); hl_s.addStretch(); hl_s.addWidget(self.svc_spin)
        svl.addLayout(hl_s); vl.addWidget(svc_card)
        # Tax
        tax_card = card_widget('#0c1a27','#0369a1',14); tvl = QVBoxLayout(tax_card); tvl.setContentsMargins(18,14,18,14)
        hl_t = QHBoxLayout()
        tx_info= QVBoxLayout()
        self.tax_lbl = lbl('','white',15,True); self.tax_note= lbl('','#6b7280',12)
        tx_info.addWidget(self.tax_lbl); tx_info.addWidget(self.tax_note)
        self.tax_spin= QDoubleSpinBox(); self.tax_spin.setRange(0,100); self.tax_spin.setSingleStep(0.5); self.tax_spin.setDecimals(1)
        self.tax_spin.setFixedSize(120,54); self.tax_spin.setSuffix(' %')
        self.tax_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl_t.addLayout(tx_info); hl_t.addStretch(); hl_t.addWidget(self.tax_spin)
        tvl.addLayout(hl_t); vl.addWidget(tax_card)
        # Preview
        prev_card = card_widget('#1c1500','#854d0e',14); pvl = QVBoxLayout(prev_card); pvl.setContentsMargins(18,14,18,14)
        self.prev_title = lbl('','#854d0e',12,True); pvl.addWidget(self.prev_title)
        pvl.addWidget(divider())
        rows_w = QWidget(); rows_w.setStyleSheet('background:transparent;border:none;')
        self.prev_lay = QVBoxLayout(rows_w); self.prev_lay.setContentsMargins(0,8,0,0); self.prev_lay.setSpacing(6)
        pvl.addWidget(rows_w); vl.addWidget(prev_card)
        self.svc_spin.valueChanged.connect(self._update_preview)
        self.tax_spin.valueChanged.connect(self._update_preview)
        # Sound settings card
        snd_card = card_widget('#0d1117','#1f2937',14)
        svl2 = QVBoxLayout(snd_card); svl2.setContentsMargins(18,14,18,14); svl2.setSpacing(10)
        self.snd_title = lbl('','white',15,True); svl2.addWidget(self.snd_title)
        svl2.addWidget(divider())
        # Enable toggle
        self.snd_enable_b = QPushButton(); self.snd_enable_b.setCheckable(True); self.snd_enable_b.setFixedHeight(42)
        self.snd_enable_b.clicked.connect(self._toggle_sound)
        svl2.addWidget(self.snd_enable_b)
        # New order toggle
        self.snd_new_b = QPushButton(); self.snd_new_b.setCheckable(True); self.snd_new_b.setFixedHeight(38)
        self.snd_new_b.clicked.connect(lambda: self._toggle_snd_type('new_order'))
        svl2.addWidget(self.snd_new_b)
        # Order ready toggle
        self.snd_ready_b = QPushButton(); self.snd_ready_b.setCheckable(True); self.snd_ready_b.setFixedHeight(38)
        self.snd_ready_b.clicked.connect(lambda: self._toggle_snd_type('order_ready'))
        svl2.addWidget(self.snd_ready_b)
        # Volume
        vol_row = QHBoxLayout()
        self.vol_lbl = lbl('','#9ca3af',12); vol_row.addWidget(self.vol_lbl)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal); self.vol_slider.setRange(0,100)
        self.vol_slider.setFixedHeight(28)
        self.vol_slider.setStyleSheet('QSlider::groove:horizontal{background:#1f2937;height:4px;border-radius:2px;}QSlider::handle:horizontal{background:#f59e0b;width:16px;height:16px;border-radius:8px;margin:-6px 0;}QSlider::sub-page:horizontal{background:#f59e0b;border-radius:2px;}')
        self.vol_slider.valueChanged.connect(lambda v: self._on_vol(v))
        vol_row.addWidget(self.vol_slider,stretch=1)
        self.vol_val_l = lbl('','#f59e0b',12,True); vol_row.addWidget(self.vol_val_l)
        svl2.addLayout(vol_row)
        # Test button
        self.snd_test_b = btn('','gray',40,13); self.snd_test_b.clicked.connect(lambda: play_sound('test'))
        svl2.addWidget(self.snd_test_b)
        vl.addWidget(snd_card)

        self.save_b = btn('','amber',50,15); vl.addWidget(self.save_b)
        self.save_b.clicked.connect(self._save)

        self.db_setup_b = btn('🗄️  إعداد قاعدة البيانات','gray',46,13)
        self.db_setup_b.clicked.connect(self._open_db_setup)
        vl.addWidget(self.db_setup_b)

        self.change_pw_b = btn('🔑  تغيير كلمة مرور المدير','gray',46,13)
        self.change_pw_b.clicked.connect(self._open_change_password)
        vl.addWidget(self.change_pw_b)

        self.refresh()

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"⚙️  {t['settings']}")

        is_admin = bool(APP.user and APP.user.get('role') == 'admin')
        self.tables_card.setVisible(is_admin)
        self.db_setup_b.setVisible(is_admin)
        self.change_pw_b.setVisible(is_admin)
        if is_admin:
            self.tables_title.setText(f"🪑  {t['tables_mgmt']}")
            self.seats_spin.setPrefix(f"{t['seats_lbl']}: ")
            self.add_tbl_b.setText(f"+  {t['add_table']}")
            self.rm_tbl_b.setText(f"−  {t['remove_table']}")
            self._refresh_tables_combo()

        self.svc_lbl.setText(t['service_lbl']); self.svc_note.setText(t['svc_note'])
        self.tax_lbl.setText(t['tax_lbl']);     self.tax_note.setText(t['tax_note'])
        self.svc_spin.setValue(APP.settings.get('service',12))
        self.tax_spin.setValue(APP.settings.get('tax',14))
        self.save_b.setText(t['save_settings'])
        self.prev_title.setText(f"{t['preview']} — {t['example_on']} 100 {t['currency']}")
        self._update_preview()
        # Sound
        self.snd_title.setText(f"🔊  {t['sound_settings']}")
        self._refresh_sound_ui()

    def _update_preview(self):
        t = APP.t()
        s = dict(service=self.svc_spin.value(), tax=self.tax_spin.value())
        sub,svc,tax,tot = calc_order([dict(qty=1,price=100)],s)
        while self.prev_lay.count():
            i = self.prev_lay.takeAt(0)
            if i.widget(): i.widget().deleteLater()
        for label,val,color in [
            (t['subtotal'],f"100.00 {t['currency']}","#9ca3af"),
            (f"{t['service_lbl']} ({self.svc_spin.value():.1f}%)",f"+ {svc:.2f} {t['currency']}","#22c55e"),
            (f"{t['tax_lbl']} ({self.tax_spin.value():.1f}%)",f"+ {tax:.2f} {t['currency']}","#38bdf8"),
            (t['total'],f"{tot:.2f} {t['currency']}","#f59e0b"),
        ]:
            hl = QHBoxLayout()
            hl.addWidget(lbl(label,color,12,label==t['total']))
            hl.addStretch()
            hl.addWidget(lbl(val,color,12,label==t['total']))
            row_w = QWidget(); row_w.setStyleSheet('background:transparent;border:none;')
            row_w.setLayout(hl); self.prev_lay.addWidget(row_w)

    def _save(self):
        APP.settings['service'] = self.svc_spin.value()
        APP.settings['tax']     = self.tax_spin.value()
        APP.sound['volume']     = self.vol_slider.value()
        persist_state()
        self.save_b.setText(APP.t()['settings_saved'])
        QTimer.singleShot(2200, lambda: self.save_b.setText(APP.t()['save_settings']))

    def _refresh_sound_ui(self):
        t = APP.t()
        en  = APP.sound.get('enabled', True)
        no  = APP.sound.get('new_order', True)
        rdy = APP.sound.get('order_ready', True)
        vol = APP.sound.get('volume', 80)
        self._style_toggle(self.snd_enable_b, en, t['sound_enabled'])
        self._style_toggle(self.snd_new_b,    no,  f"  🎵  {t['sound_new_order']}", small=True)
        self._style_toggle(self.snd_ready_b,  rdy, f"  🔔  {t['sound_order_ready']}", small=True)
        self.snd_new_b.setEnabled(en); self.snd_ready_b.setEnabled(en)
        self.vol_slider.setValue(vol); self.vol_val_l.setText(f"{vol}%")
        self.snd_test_b.setText(f"🔊  {t['sound_test']}")
        self.vol_lbl.setText(f"{t['sound_volume']}: ")

    def _style_toggle(self, b, active, label, small=False):
        fs = 11 if small else 13
        if active:
            b.setStyleSheet(f'QPushButton{{background:#052e16;border:1.5px solid #166534;border-radius:10px;color:#22c55e;font-size:{fs}px;font-weight:bold;padding:0 12px;}}')
            b.setText(f"✅  {label}")
        else:
            b.setStyleSheet(f'QPushButton{{background:#111;border:1.5px solid #374151;border-radius:10px;color:#4b5563;font-size:{fs}px;font-weight:bold;padding:0 12px;}}')
            b.setText(f"⬜  {label}")

    def _toggle_sound(self):
        APP.sound['enabled'] = not APP.sound.get('enabled', True)
        self._refresh_sound_ui()

    def _toggle_snd_type(self, key):
        APP.sound[key] = not APP.sound.get(key, True)
        self._refresh_sound_ui()

    def _on_vol(self, v):
        APP.sound['volume'] = v
        self.vol_val_l.setText(f"{v}%")

    def _refresh_tables_combo(self):
        cur = self.tbl_combo.currentData()
        self.tbl_combo.blockSignals(True)
        self.tbl_combo.clear()
        t = APP.t()
        for tb in APP.tables:
            self.tbl_combo.addItem(f"{t['table']} {tb['id']}", tb['id'])
        if cur is not None:
            idx = self.tbl_combo.findData(cur)
            if idx >= 0:
                self.tbl_combo.setCurrentIndex(idx)
        self.tbl_combo.blockSignals(False)

    def _add_table(self):
        next_id = (max([tb['id'] for tb in APP.tables]) + 1) if APP.tables else 1
        seats = int(self.seats_spin.value())
        APP.tables.append(dict(id=next_id, seats=seats, status='free'))
        persist_state()
        self._refresh_tables_combo()
        QMessageBox.information(self, APP.t()['tables_mgmt'], APP.t()['table_added'])

    def _remove_table(self):
        tid = self.tbl_combo.currentData()
        if tid is None:
            return
        tb = APP.tbl(tid)
        active = APP.active_ord(tid)
        if not tb or tb.get('status') != 'free' or active:
            QMessageBox.warning(self, APP.t()['tables_mgmt'], APP.t()['table_remove_busy'])
            return
        APP.tables = [x for x in APP.tables if x['id'] != tid]
        persist_state()
        self._refresh_tables_combo()
        QMessageBox.information(self, APP.t()['tables_mgmt'], APP.t()['table_removed'])

    def _open_db_setup(self):
        if not (APP.user and APP.user.get('role') == 'admin'):
            QMessageBox.warning(self, APP.t()['settings'], "هذه الصلاحية متاحة للمدير فقط.")
            return
        from .db_setup import DBSetupDialog
        dlg = DBSetupDialog(self)
        dlg.exec()

    def _open_change_password(self):
        if not (APP.user and APP.user.get('role') == 'admin'):
            QMessageBox.warning(self, APP.t()['settings'], "هذه الصلاحية متاحة للمدير فقط.")
            return
        from .admin_auth import verify_admin_password, set_admin_password

        old_pw, ok = QInputDialog.getText(
            self, "تغيير كلمة مرور المدير", "كلمة المرور الحالية:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if not verify_admin_password(old_pw.strip()):
            QMessageBox.warning(self, "خطأ", "كلمة المرور الحالية غير صحيحة.")
            return

        new_pw, ok = QInputDialog.getText(
            self, "تغيير كلمة مرور المدير", "كلمة المرور الجديدة (6 أحرف على الأقل):",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        new_pw = new_pw.strip()
        if len(new_pw) < 6:
            QMessageBox.warning(self, "خطأ", "كلمة المرور الجديدة قصيرة جداً (6 أحرف على الأقل).")
            return

        confirm_pw, ok = QInputDialog.getText(
            self, "تغيير كلمة مرور المدير", "تأكيد كلمة المرور الجديدة:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return
        if confirm_pw.strip() != new_pw:
            QMessageBox.warning(self, "خطأ", "كلمة المرور الجديدة وتأكيدها غير متطابقين.")
            return

        set_admin_password(new_pw)
        QMessageBox.information(
            self, "تم",
            "تم تغيير كلمة مرور المدير بنجاح.\n"
            "يمكنك الآن حذف ملف RestaurantManager_ADMIN_PASSWORD.txt من سطح المكتب إن وُجد."
        )

# ══════════════════════════════════════════════════════════════
#  REPORTS SCREEN
# ══════════════════════════════════════════════════════════════
class BarChart(QWidget):
    """Minimal bar chart widget — no external lib needed."""
    def __init__(self, data=None, color='#f59e0b', h=120, show_labels=True):
        super().__init__()
        self.data  = data or []   # list of (label, value)
        self.color = color
        self.show_labels = show_labels
        self.setFixedHeight(h)
        self.setStyleSheet('background:transparent;border:none;')

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, _):
        if not self.data: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        n   = len(self.data)
        pad = 6
        bot = 28 if self.show_labels else 6
        top = 8
        draw_h = H - bot - top
        max_v = max(v for _,v in self.data) or 1
        bar_w = max(4, (W - pad*(n+1)) // n)

        bar_color  = QColor(self.color)
        dim_color  = QColor(self.color); dim_color.setAlpha(60)
        text_color = QColor('#6b7280')
        val_color  = QColor('#e5e7eb')

        for i,(label,val) in enumerate(self.data):
            bh   = int(draw_h * val / max_v)
            x    = pad + i*(bar_w + pad)
            y    = top + draw_h - bh
            # Bar
            col = bar_color if val == max_v else dim_color
            p.setBrush(col); p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x, y, bar_w, bh, 3, 3)
            # Value on top
            if val > 0:
                p.setPen(val_color)
                p.setFont(QFont('Arial', 8, QFont.Weight.Bold))
                p.drawText(x, y-2, bar_w, 14, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom, str(int(val)) if val==int(val) else f"{val:.0f}")
            # X label
            if self.show_labels:
                p.setPen(text_color)
                p.setFont(QFont('Arial', 8))
                p.drawText(x, H-bot, bar_w, bot, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop, str(label)[:4])
        p.end()


class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._period = 'today'
        self._from   = datetime.now().date()
        self._to     = datetime.now().date()
        self.setStyleSheet('background:transparent;')
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        # ── Top toolbar ───────────────────────────────────────
        toolbar = QWidget(); toolbar.setFixedHeight(52)
        toolbar.setStyleSheet('background:#050505;border-bottom:1px solid #1f2937;')
        tl = QHBoxLayout(toolbar); tl.setContentsMargins(20,0,20,0); tl.setSpacing(8)
        self.title = lbl('','white',18,True); tl.addWidget(self.title)
        tl.addStretch()
        self._period_btns = {}
        for pid in ['today','week','month','custom']:
            b = QPushButton(); b.setFixedHeight(32); b.setCheckable(True)
            b.clicked.connect(lambda _,p=pid: self._set_period(p))
            self._period_btns[pid] = b; tl.addWidget(b)
        # Custom date pickers (hidden by default)
        self.from_d = QDateEdit(); self.from_d.setCalendarPopup(True); self.from_d.setFixedSize(120,32)
        self.from_d.setStyleSheet('QDateEdit{background:#111;border:1px solid #374151;border-radius:8px;color:white;padding:0 6px;font-size:12px;}')
        self.to_d   = QDateEdit(); self.to_d.setCalendarPopup(True);   self.to_d.setFixedSize(120,32)
        self.to_d.setStyleSheet('QDateEdit{background:#111;border:1px solid #374151;border-radius:8px;color:white;padding:0 6px;font-size:12px;}')
        self.from_d.hide(); self.to_d.hide()
        tl.addWidget(self.from_d); tl.addWidget(self.to_d)
        outer.addWidget(toolbar)

        # ── Scrollable body ───────────────────────────────────
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        body_w = QWidget(); body_w.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(body_w); vl.setContentsMargins(22,18,22,18); vl.setSpacing(14)

        # Summary stats row (4 cards)
        stats = QHBoxLayout(); stats.setSpacing(10)
        self._s_rev  = self._mk_stat('#1c1500','#854d0e','#f59e0b')
        self._s_cnt  = self._mk_stat('#0c1a27','#0369a1','#38bdf8')
        self._s_avg  = self._mk_stat('#150d2a','#4c1d95','#a78bfa')
        self._s_net  = self._mk_stat('#051a0d','#166534','#22c55e')
        for c in [self._s_rev,self._s_cnt,self._s_avg,self._s_net]: stats.addWidget(c)
        vl.addLayout(stats)

        # Cancelled / refund row
        self.net_w = QWidget(); self.net_w.setStyleSheet('background:#111;border:1px solid #1f2937;border-radius:12px;'); self.net_w.hide()
        hl_n = QHBoxLayout(self.net_w); hl_n.setContentsMargins(16,10,16,10)
        self.refund_l = lbl('','#9ca3af',12); self.net_l = lbl('','#f43f5e',13,True)
        hl_n.addWidget(self.refund_l); hl_n.addStretch(); hl_n.addWidget(self.net_l)
        vl.addWidget(self.net_w)

        # ── Peak hours chart ──────────────────────────────────
        ph_card = card_widget('#111','#1f2937',12)
        ph_vl = QVBoxLayout(ph_card); ph_vl.setContentsMargins(16,12,16,12); ph_vl.setSpacing(8)
        self.peak_title = lbl('','white',13,True); ph_vl.addWidget(self.peak_title)
        self.peak_chart = BarChart(color='#0ea5e9', h=130)
        ph_vl.addWidget(self.peak_chart)
        vl.addWidget(ph_card)

        # ── Top items chart ───────────────────────────────────
        ti_card = card_widget('#111','#1f2937',12)
        ti_vl = QVBoxLayout(ti_card); ti_vl.setContentsMargins(16,12,16,12); ti_vl.setSpacing(8)
        self.items_title = lbl('','white',13,True); ti_vl.addWidget(self.items_title)
        self.items_chart = BarChart(color='#f59e0b', h=140, show_labels=True)
        ti_vl.addWidget(self.items_chart)
        self.items_list_w = QWidget(); self.items_list_w.setStyleSheet('background:transparent;border:none;')
        self.items_list_vl = QVBoxLayout(self.items_list_w); self.items_list_vl.setContentsMargins(0,4,0,0); self.items_list_vl.setSpacing(3)
        ti_vl.addWidget(self.items_list_w)
        vl.addWidget(ti_card)

        # ── Recent orders list ────────────────────────────────
        ord_card = card_widget('#111','#1f2937',12)
        ord_vl = QVBoxLayout(ord_card); ord_vl.setContentsMargins(0,0,0,0); ord_vl.setSpacing(0)
        hdr_row = QWidget(); hdr_row.setFixedHeight(40); hdr_row.setStyleSheet('background:transparent;border:none;')
        hrl = QHBoxLayout(hdr_row); hrl.setContentsMargins(16,0,16,0)
        self.ord_list_title = lbl('','white',13,True); hrl.addWidget(self.ord_list_title)
        hrl.addStretch()
        self.hint_l = lbl('','#374151',11); hrl.addWidget(self.hint_l)
        ord_vl.addWidget(hdr_row); ord_vl.addWidget(divider())
        self.list_w  = QWidget(); self.list_w.setStyleSheet('background:transparent;')
        self.list_vl = QVBoxLayout(self.list_w); self.list_vl.setContentsMargins(8,4,8,8); self.list_vl.setSpacing(3)
        ord_vl.addWidget(self.list_w)
        vl.addWidget(ord_card)
        vl.addStretch()
        sc.setWidget(body_w); outer.addWidget(sc)

    def _mk_stat(self, bg, border, vc):
        c = QWidget(); c.setFixedHeight(78); c.setStyleSheet(f'background:{bg};border:1.5px solid {border};border-radius:14px;')
        vl2 = QVBoxLayout(c); vl2.setAlignment(Qt.AlignmentFlag.AlignCenter); vl2.setSpacing(1)
        v = QLabel('—'); v.setStyleSheet(f'color:{vc};font-size:17px;font-weight:bold;background:transparent;border:none;')
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb = QLabel(''); lb.setStyleSheet('color:#6b7280;font-size:10px;background:transparent;border:none;')
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl2.addWidget(v); vl2.addWidget(lb); c._v=v; c._l=lb; return c

    def _set_period(self, p):
        self._period = p
        show_custom = (p == 'custom')
        self.from_d.setVisible(show_custom); self.to_d.setVisible(show_custom)
        if p == 'today':
            d = datetime.now().date(); self._from = d; self._to = d
        elif p == 'week':
            d = datetime.now().date(); self._from = d - timedelta(days=d.weekday()); self._to = d
        elif p == 'month':
            d = datetime.now().date(); self._from = d.replace(day=1); self._to = d
        elif p == 'custom':
            self._from = self.from_d.date().toPyDate()
            self._to   = self.to_d.date().toPyDate()
        self.refresh()

    def _get_period_orders(self):
        from_ts = int(datetime(*self._from.timetuple()[:6]).timestamp() * 1000)
        to_ts   = int(datetime(*self._to.timetuple()[:6]).timestamp() * 1000) + 86400000
        return [o for o in APP.orders if from_ts <= o.get('createdAt',0) < to_ts]

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"📊  {t['nav']['reports']}")

        # Refresh period buttons
        period_labels = dict(today=t['rep_today'], week=t['rep_week'], month=t['rep_month'], custom=t['rep_custom'])
        for pid, b in self._period_btns.items():
            active = pid == self._period
            b.setText(period_labels[pid])
            if active:
                b.setStyleSheet('QPushButton{background:#f59e0b;border:none;border-radius:10px;color:white;font-size:12px;font-weight:bold;padding:0 12px;}')
            else:
                b.setStyleSheet('QPushButton{background:transparent;border:1px solid #374151;border-radius:10px;color:#6b7280;font-size:12px;font-weight:bold;padding:0 12px;}QPushButton:hover{color:white;}')

        # Custom date pickers
        self.from_d.setDate(QDate(self._from.year, self._from.month, self._from.day))
        self.to_d.setDate(QDate(self._to.year, self._to.month, self._to.day))
        if self._period == 'custom':
            self._from = self.from_d.date().toPyDate()
            self._to   = self.to_d.date().toPyDate()

        p_ords  = self._get_period_orders()
        paid    = [o for o in p_ords if o['status']=='paid' and not o.get('cancelled')]
        canc    = [o for o in p_ords if o.get('cancelled')]
        rev     = sum(o.get('total',0) for o in paid)
        canc_rev= sum(o.get('total',0) for o in canc)
        ref_rev = sum(sum(r.get('amount',0) for r in o.get('refunds',[])) for o in p_ords)
        net_rev = rev - canc_rev - ref_rev
        avg     = (rev/len(paid) if paid else 0)

        self._s_rev._v.setText(f"{rev:.0f} {t['currency']}"); self._s_rev._l.setText(t['rep_revenue'])
        self._s_cnt._v.setText(str(len(p_ords)));              self._s_cnt._l.setText(t['total_orders'])
        self._s_avg._v.setText(f"{avg:.0f} {t['currency']}"); self._s_avg._l.setText(t['avg_order'])
        self._s_net._v.setText(f"{net_rev:.0f} {t['currency']}"); self._s_net._l.setText(t['net_rev'])

        has_ded = (canc_rev+ref_rev) > 0
        self.net_w.setVisible(has_ded)
        if has_ded:
            self.refund_l.setText(f"{t['total_refunds']}: - {canc_rev+ref_rev:.2f} {t['currency']}")
            self.net_l.setText(f"  {len(canc)} {t['cancelled_count']} • {len([o for o in p_ords if o.get('refunds')])} ↩")

        # ── Peak hours chart ──────────────────────────────────
        self.peak_title.setText(f"🕐  {t['peak_hours']}")
        hour_counts = defaultdict(int)
        for o in paid:
            h = datetime.fromtimestamp(o['createdAt']/1000).hour
            hour_counts[h] += 1
        if hour_counts:
            peak_data = [(f"{h}:00", hour_counts.get(h,0)) for h in range(6,24)]
            self.peak_chart.set_data(peak_data)
        else:
            self.peak_chart.set_data([])

        # ── Top items chart ───────────────────────────────────
        self.items_title.setText(f"🏆  {t['top_items']}")
        item_totals = defaultdict(lambda: dict(qty=0, rev=0.0, name_ar='', name_en=''))
        for o in paid:
            for it in o.get('items',[]):
                mid = it.get('mid', it.get('id', ''))
                item_totals[mid]['qty']     += it.get('qty',0)
                item_totals[mid]['rev']     += it.get('qty',0)*it.get('price',0)
                item_totals[mid]['name_ar']  = it.get('a','')
                item_totals[mid]['name_en']  = it.get('e','')
        top = sorted(item_totals.items(), key=lambda x: x[1]['qty'], reverse=True)[:8]
        if top:
            chart_data = [(v['name_ar'][:4] if APP.lang=='ar' else v['name_en'][:5], v['qty']) for _,v in top]
            self.items_chart.set_data(chart_data)
        else:
            self.items_chart.set_data([])

        while self.items_list_vl.count():
            i = self.items_list_vl.takeAt(0)
            if i.widget(): i.widget().deleteLater()
        for rank,(mid,v) in enumerate(top,1):
            name = v['name_ar'] if APP.lang=='ar' else v['name_en']
            row_w = QWidget(); row_w.setFixedHeight(32); row_w.setStyleSheet('background:transparent;border:none;')
            hl = QHBoxLayout(row_w); hl.setContentsMargins(0,0,0,0)
            rank_l = lbl(f"#{rank}", ['#f59e0b','#9ca3af','#cd7f32'][rank-1] if rank<=3 else '#4b5563', 11, True)
            rank_l.setFixedWidth(26)
            hl.addWidget(rank_l)
            hl.addWidget(lbl(name,'white',12,True))
            hl.addStretch()
            hl.addWidget(lbl(f"{v['qty']} {t['rep_qty']}",'#38bdf8',12,True))
            hl.addSpacing(12)
            hl.addWidget(lbl(f"{v['rev']:.0f} {t['currency']}",'#f59e0b',12,True))
            self.items_list_vl.addWidget(row_w)
        if not top:
            self.items_list_vl.addWidget(lbl(t['no_data'],'#4b5563',12,False,Qt.AlignmentFlag.AlignCenter))

        # ── Recent orders list ────────────────────────────────
        self.ord_list_title.setText(t['recent'])
        self.hint_l.setText(t['click_inv'])
        while self.list_vl.count():
            i = self.list_vl.takeAt(0)
            if i.widget(): i.widget().deleteLater()
        for o in list(reversed(p_ords))[:25]:
            self.list_vl.addWidget(self._mk_ord_row(o,t))
        self.list_vl.addStretch()

    def _mk_ord_row(self, o, t):
        is_paid= o['status']=='paid'
        is_canc= o.get('cancelled',False)
        w = QWidget(); w.setFixedHeight(56)
        w.setStyleSheet(f'background:{"#111" if not is_canc else "#0a0a0a"};border:1px solid {"#1f2937" if not is_canc else "#111"};border-radius:10px;')
        if is_paid:
            w.setCursor(Qt.CursorShape.PointingHandCursor)

        hl = QHBoxLayout(w); hl.setContentsMargins(14,0,14,0)
        vl2= QVBoxLayout(); vl2.setSpacing(2)
        vl2.addWidget(lbl(f"{t['table']} {o['tableId']} • {len(o['items'])} {t['item_count']}"
                          +(' ['+t['status']['cancelled']+']' if is_canc else '')
                          +(' ↩' if o.get('refunds') else ''),
                          '#4b5563' if is_canc else 'white', 13, True))
        vl2.addWidget(lbl(f"{fmt_date(o['createdAt'])} {fmt_time(o['createdAt'])}",'#4b5563',10))
        price_l = lbl(f"{o.get('total',0):.2f} {t['currency']}",
                      '#4b5563' if is_canc else '#f59e0b', 13, True)
        if is_canc: price_l.setStyleSheet(price_l.styleSheet()+'text-decoration:line-through;')
        sb = status_badge('cancelled' if is_canc else o['status'], t)
        hl.addLayout(vl2); hl.addStretch(); hl.addWidget(price_l); hl.addSpacing(8); hl.addWidget(sb)
        if is_paid:
            gear = lbl(' ⚙️','#4b5563',12); hl.addWidget(gear)
            w.mousePressEvent = lambda _,ord=o: self._open_inv(ord)
        return w

    def _open_inv(self, o):
        dlg = InvoiceDialog(o, self)
        dlg.exec()
        self.refresh()

# ── Invoice Management Dialog ─────────────────────────────────
class InvoiceDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(t['inv_mgmt'])
        self.setFixedSize(480, 580); self.setStyleSheet('background:#111;')
        vl = QVBoxLayout(self); vl.setContentsMargins(0,0,0,0)

        # Title bar
        hdr = QWidget(); hdr.setFixedHeight(60); hdr.setStyleSheet('background:#0a0a0a;border-bottom:1px solid #1f2937;')
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20,0,20,0)
        hl.addWidget(lbl(t['inv_mgmt'],'white',16,True))
        hl.addStretch()
        close_b = QPushButton('×'); close_b.setFixedSize(32,32)
        close_b.setStyleSheet('QPushButton{background:transparent;border:none;color:#6b7280;font-size:22px;font-weight:bold;}QPushButton:hover{color:white;}')
        close_b.clicked.connect(self.accept)
        hl.addWidget(close_b); vl.addWidget(hdr)

        if not order.get('cancelled'):
            tabs = QTabWidget(); tabs.setDocumentMode(True)
            tabs.addTab(self._build_view_tab(t), f"📄 {t['nav']['orders'] if False else ('الفاتورة' if APP.lang=='ar' else 'Invoice')}")
            tabs.addTab(self._build_return_tab(t), f"↩️ {t['return_items']}")
            tabs.addTab(self._build_cancel_tab(t), f"❌ {t['cancel_inv']}")
            vl.addWidget(tabs)
        else:
            vl.addWidget(self._build_view_tab(t))

    def _build_view_tab(self, t):
        w = QScrollArea(); w.setWidgetResizable(True); w.setStyleSheet('background:transparent;border:none;')
        ctn = QWidget(); ctn.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(ctn); vl.setContentsMargins(20,16,20,16); vl.setSpacing(10)

        items_c = card_widget('#0a0a0a','#1f2937',12); il = QVBoxLayout(items_c); il.setContentsMargins(14,12,14,12); il.setSpacing(6)
        for item in self.order['items']:
            n = item['a'] if APP.lang=='ar' else item['e']
            avail = self._get_avail(item)
            retd  = item['qty']-avail
            hl = QHBoxLayout()
            hl.addWidget(lbl(f"{n} × {item['qty']}" + (f"  ↩{retd}" if retd>0 else ''),
                             '#4b5563' if retd==item['qty'] else '#e5e7eb', 12))
            hl.addStretch()
            hl.addWidget(lbl(f"{item['qty']*item['price']:.2f} {t['currency']}",
                             '#4b5563' if retd==item['qty'] else '#f59e0b', 12, True))
            il.addLayout(hl)
        il.addWidget(divider())
        for label,val,color in [
            (t['subtotal'],f"{self.order.get('subtotal',self.order.get('total',0)):.2f}",'#9ca3af'),
            (f"{t['service_lbl']} ({APP.settings.get('service',0):.0f}%)",f"+ {self.order.get('serviceAmt',0):.2f}",'#22c55e'),
            (f"{t['tax_lbl']} ({APP.settings.get('tax',0):.0f}%)",f"+ {self.order.get('taxAmt',0):.2f}",'#38bdf8'),
            (t['total'],f"{self.order.get('total',0):.2f}",'#f59e0b'),
        ]:
            if 'service' in label and self.order.get('serviceAmt',0)==0: continue
            if 'tax' in label and self.order.get('taxAmt',0)==0: continue
            hl = QHBoxLayout()
            is_total = label==t['total']
            hl.addWidget(lbl(label,color,12+2*is_total,is_total))
            hl.addStretch(); hl.addWidget(lbl(f"{val} {t['currency']}",color,12+2*is_total,is_total))
            il.addLayout(hl)
        vl.addWidget(items_c)

        # Refunds history
        if self.order.get('refunds'):
            ref_c = card_widget('#1c0510','#881337',12); rl = QVBoxLayout(ref_c); rl.setContentsMargins(14,12,14,12)
            rl.addWidget(lbl(t['refunds_hist'],'#f43f5e',11,True)); rl.addWidget(divider())
            for ref in self.order['refunds']:
                desc = ', '.join(f"{i['a'] if APP.lang=='ar' else i['e']} ×{i['qty']}" for i in ref['items'])
                hl = QHBoxLayout()
                hl.addWidget(lbl(f"{fmt_time(ref['at'])} — {desc}",'#9ca3af',11))
                hl.addStretch()
                hl.addWidget(lbl(f"- {ref['amount']:.2f} {t['currency']}",'#f43f5e',11,True))
                rl.addLayout(hl)
                if ref.get('reason'):
                    rl.addWidget(lbl(ref['reason'],'#4b5563',10))
            vl.addWidget(ref_c)

        if self.order.get('cancelled'):
            cc = card_widget('#1c0510','#881337',12); cl = QVBoxLayout(cc); cl.setContentsMargins(14,12,14,12)
            cl.addWidget(lbl(f"❌ {t['cancelled_inv']}",'#f43f5e',15,True,Qt.AlignmentFlag.AlignCenter))
            if self.order.get('cancelReason'):
                cl.addWidget(lbl(self.order['cancelReason'],'#6b7280',12,False,Qt.AlignmentFlag.AlignCenter))
            vl.addWidget(cc)

        vl.addStretch(); w.setWidget(ctn); return w

    def _build_return_tab(self, t):
        w = QScrollArea(); w.setWidgetResizable(True); w.setStyleSheet('background:transparent;border:none;')
        ctn = QWidget(); ctn.setStyleSheet('background:transparent;')
        vl  = QVBoxLayout(ctn); vl.setContentsMargins(20,16,20,16); vl.setSpacing(10)
        vl.addWidget(lbl(t['return_title'],'#9ca3af',12))

        self._ret_spins = {}
        for item in self.order['items']:
            avail = self._get_avail(item)
            if avail==0: continue
            name = item['a'] if APP.lang=='ar' else item['e']
            row  = card_widget(); rl = QHBoxLayout(row); rl.setContentsMargins(14,10,14,10)
            rl.addWidget(lbl(name,'white',13,True))
            rl.addStretch()
            rl.addWidget(lbl(f"{t['avail_qty']}: {avail}/{item['qty']}",'#6b7280',11))
            sp = QSpinBox(); sp.setRange(0,avail); sp.setValue(0); sp.setFixedSize(80,34)
            sp.setStyleSheet('QSpinBox{background:#0a0a0a;border:1px solid #374151;border-radius:8px;color:white;font-size:14px;font-weight:bold;}')
            self._ret_spins[item['mid']] = (sp, item)
            rl.addSpacing(8); rl.addWidget(sp); vl.addWidget(row)

        vl.addWidget(lbl(t['reason'],'#6b7280',11))
        self.ret_reason = QLineEdit(); self.ret_reason.setPlaceholderText(t['enter_reason']); vl.addWidget(self.ret_reason)

        self.ret_total_l = lbl('','#f43f5e',13,True); vl.addWidget(self.ret_total_l)
        for spin,_ in self._ret_spins.values():
            spin.valueChanged.connect(self._update_refund_preview)
        self._update_refund_preview()

        conf_b = btn(f"↩️  {t['confirm_return']}",'rose',44,13)
        conf_b.clicked.connect(lambda: self._do_return(t)); vl.addWidget(conf_b)
        vl.addStretch(); w.setWidget(ctn); return w

    def _update_refund_preview(self):
        t = APP.t()
        items = [dict(qty=sp.value(), price=item['price'], mid=item['mid'],a=item['a'],e=item['e'])
                 for sp,(item) in self._ret_spins.values() if sp.value()>0]
        if items:
            _,_,_,amt = calc_order(items, APP.settings)
            self.ret_total_l.setText(f"{t['refund_amt']}: - {amt:.2f} {t['currency']}")
        else:
            self.ret_total_l.setText('')

    def _do_return(self, t):
        items = [dict(qty=sp.value(), price=item['price'], mid=item['mid'],a=item['a'],e=item['e'])
                 for sp,item in self._ret_spins.values() if sp.value()>0]
        if not items: return
        _,_,_,amt = calc_order(items, APP.settings)
        ref = dict(id=uid(), items=items, reason=self.ret_reason.text().strip(),
                   at=int(time.time()*1000), amount=amt)
        o = APP.ord(self.order['id'])
        if o:
            o.setdefault('refunds',[]).append(ref)
            self.order = o
        QMessageBox.information(self, '', t['refund_ok']); self.accept()

    def _build_cancel_tab(self, t):
        w = QWidget(); w.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(w); vl.setContentsMargins(20,20,20,20); vl.setSpacing(14)

        warn = card_widget('#1c0510','#881337',14); wl = QVBoxLayout(warn); wl.setContentsMargins(20,16,20,16)
        wl.addWidget(lbl('⚠️','',32,False,Qt.AlignmentFlag.AlignCenter))
        wl.addWidget(lbl(t['cancel_inv'],'white',16,True,Qt.AlignmentFlag.AlignCenter))
        wl.addWidget(lbl(t['inv_cancel_confirm'],'#9ca3af',12,False,Qt.AlignmentFlag.AlignCenter))
        wl.addWidget(lbl(f"- {self.order.get('total',0):.2f} {t['currency']}",'#f43f5e',20,True,Qt.AlignmentFlag.AlignCenter))
        vl.addWidget(warn)

        vl.addWidget(lbl(f"* {t['reason']}","#f43f5e",11,True))
        self.canc_reason = QLineEdit(); self.canc_reason.setPlaceholderText(t['enter_reason']); vl.addWidget(self.canc_reason)
        canc_b = btn(f"❌  {t['cancel_inv']}",'rose',46,13)
        canc_b.clicked.connect(lambda: self._do_cancel(t)); vl.addWidget(canc_b)
        vl.addStretch(); return w

    def _do_cancel(self, t):
        reason = self.canc_reason.text().strip()
        if not reason:
            QMessageBox.warning(self,'',t['enter_reason']); return
        o = APP.ord(self.order['id'])
        if o:
            o['cancelled']=True; o['cancelReason']=reason
            o['cancelledAt']=int(time.time()*1000)
            self.order = o
        QMessageBox.information(self,'',t['inv_cancelled']); self.accept()

    def _get_avail(self, item):
        retd = sum(ri['qty'] for ref in self.order.get('refunds',[]) for ri in ref['items'] if ri['mid']==item['mid'])
        return item['qty']-retd

# ══════════════════════════════════════════════════════════════
#  ALL ORDERS SCREEN  (cashier / admin)
# ══════════════════════════════════════════════════════════════
class OrdersScreen(QWidget):
    open_order = pyqtSignal(dict, object)

    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)
        self.title = lbl('','white',20,True); vl.addWidget(self.title)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.ctn = QWidget(); self.ctn.setStyleSheet('background:transparent;')
        self.body= QVBoxLayout(self.ctn); self.body.setContentsMargins(0,0,0,0); self.body.setSpacing(6)
        sc.setWidget(self.ctn); vl.addWidget(sc)

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"📋  {t['nav']['orders']}")
        while self.body.count():
            i = self.body.takeAt(0)
            if i.widget(): i.widget().deleteLater()

        active = [o for o in APP.orders if o['status'] not in ('paid',)]
        if not active:
            self.body.addWidget(lbl(t['no_orders'],'#4b5563',14,True,Qt.AlignmentFlag.AlignCenter))
        for o in reversed(active):
            self.body.addWidget(self._mk_row(o,t))
        self.body.addStretch()

    def _mk_row(self, o, t):
        tbl = APP.tbl(o['tableId'])
        w   = QWidget(); w.setFixedHeight(72)
        w.setStyleSheet('background:#111;border:1px solid #1f2937;border-radius:12px;')
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        hl  = QHBoxLayout(w); hl.setContentsMargins(16,0,16,0)
        vl2 = QVBoxLayout(); vl2.setSpacing(3)
        vl2.addWidget(lbl(f"{t['table']} {o['tableId']} • {len(o['items'])} {t['item_count']}",'white',14,True))
        preview = ', '.join((i['a'] if APP.lang=='ar' else i['e'])+f" ×{i['qty']}" for i in o['items'][:3])
        vl2.addWidget(lbl(preview,'#4b5563',11))
        vl2.addWidget(lbl(f"{fmt_time(o['createdAt'])} • {elapsed_m(o['createdAt'])} {t['mins']}",'#374151',10))
        hl.addLayout(vl2); hl.addStretch()
        hl.addWidget(lbl(f"{o.get('total',0):.2f} {t['currency']}",'#f59e0b',13,True))
        hl.addSpacing(10); hl.addWidget(status_badge(o['status'],t))
        w.mousePressEvent = lambda _,tb=tbl,ord=o: tbl and self.open_order.emit(tb,ord)
        return w


# ══════════════════════════════════════════════════════════════
#  RESERVATION SCREEN
# ══════════════════════════════════════════════════════════════
RES_COLORS = dict(
    pending   =('#1c1500','#854d0e','#f59e0b'),
    confirmed =('#052e16','#166534','#22c55e'),
    seated    =('#0c1a27','#0369a1','#38bdf8'),
    cancelled =('#1c0510','#881337','#f43f5e'),
    noshow    =('#111','#374151','#4b5563'),
)

def _res_status_label(status, t):
    return t.get(f'res_status_{status}', status)

class ReservationDialog(QDialog):
    def __init__(self, res=None, parent=None):
        super().__init__(parent)
        self.res = res
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(t['edit_res'] if res else t['new_res'])
        self.setFixedSize(420, 460); self.setStyleSheet('background:#111;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,22,24,22); vl.setSpacing(11)
        vl.addWidget(lbl(t['edit_res'] if res else t['new_res'],'white',17,True))
        vl.addWidget(lbl(t['res_name'],'#6b7280',11))
        self.name_in = QLineEdit(res['name'] if res else ''); self.name_in.setFixedHeight(40); vl.addWidget(self.name_in)
        vl.addWidget(lbl(t['res_phone'],'#6b7280',11))
        self.phone_in = QLineEdit(res.get('phone','') if res else ''); self.phone_in.setFixedHeight(40)
        self.phone_in.setLayoutDirection(Qt.LayoutDirection.LeftToRight); vl.addWidget(self.phone_in)
        dt_row = QHBoxLayout(); dt_row.setSpacing(10)
        date_vl = QVBoxLayout(); date_vl.addWidget(lbl(t['res_date'],'#6b7280',11))
        self.date_e = QDateEdit(); self.date_e.setCalendarPopup(True); self.date_e.setFixedHeight(40)
        self.date_e.setStyleSheet('QDateEdit{background:#111;border:1.5px solid #374151;border-radius:10px;color:white;padding:0 10px;font-size:13px;}')
        if res:
            d = datetime.fromtimestamp(res['ts']/1000).date()
            self.date_e.setDate(QDate(d.year,d.month,d.day))
        else:
            self.date_e.setDate(QDate.currentDate())
        date_vl.addWidget(self.date_e); dt_row.addLayout(date_vl)
        time_vl = QVBoxLayout(); time_vl.addWidget(lbl(t['res_time'],'#6b7280',11))
        self.time_e = QTimeEdit(); self.time_e.setFixedHeight(40)
        self.time_e.setStyleSheet('QTimeEdit{background:#111;border:1.5px solid #374151;border-radius:10px;color:white;padding:0 10px;font-size:13px;}')
        if res:
            hm = datetime.fromtimestamp(res['ts']/1000)
            self.time_e.setTime(QTime(hm.hour, hm.minute))
        else:
            self.time_e.setTime(QTime(19, 0))
        time_vl.addWidget(self.time_e); dt_row.addLayout(time_vl); vl.addLayout(dt_row)
        gt_row = QHBoxLayout(); gt_row.setSpacing(10)
        g_vl = QVBoxLayout(); g_vl.addWidget(lbl(t['res_guests'],'#6b7280',11))
        self.guests_sp = QSpinBox(); self.guests_sp.setRange(1,20)
        self.guests_sp.setValue(res.get('guests',2) if res else 2); self.guests_sp.setFixedHeight(40)
        self.guests_sp.setStyleSheet('QSpinBox{background:#111;border:1.5px solid #374151;border-radius:10px;color:white;padding:0 10px;font-size:14px;font-weight:bold;}')
        g_vl.addWidget(self.guests_sp); gt_row.addLayout(g_vl)
        t_vl = QVBoxLayout(); t_vl.addWidget(lbl(t['res_table'],'#6b7280',11))
        self.table_cb = QComboBox(); self.table_cb.setFixedHeight(40)
        self.table_cb.addItem(t['auto_table'], None)
        for tb in sorted(APP.tables, key=lambda x: x['id']):
            self.table_cb.addItem(f"{t['table']} {tb['id']} ({tb['seats']} {t['seats']})", tb['id'])
        if res and res.get('tableId'):
            idx = self.table_cb.findData(res['tableId'])
            if idx >= 0: self.table_cb.setCurrentIndex(idx)
        t_vl.addWidget(self.table_cb); gt_row.addLayout(t_vl); vl.addLayout(gt_row)
        vl.addWidget(lbl(t['res_notes'],'#6b7280',11))
        self.notes_in = QLineEdit(res.get('notes','') if res else ''); self.notes_in.setFixedHeight(38); vl.addWidget(self.notes_in)
        btns = QHBoxLayout(); btns.setSpacing(10)
        cancel_b = btn(t['cancel'],'gray',42,13); cancel_b.clicked.connect(self.reject)
        ok_b     = btn(t['save'],'amber',42,13);  ok_b.clicked.connect(self._validate)
        btns.addWidget(cancel_b); btns.addWidget(ok_b); vl.addLayout(btns)

    def _validate(self):
        if not self.name_in.text().strip(): self.name_in.setFocus(); return
        self.accept()

    def get_data(self):
        qd = self.date_e.date(); qt = self.time_e.time()
        dt = datetime(qd.year(), qd.month(), qd.day(), qt.hour(), qt.minute())
        return dict(name=self.name_in.text().strip(), phone=self.phone_in.text().strip(),
                    ts=int(dt.timestamp()*1000), guests=self.guests_sp.value(),
                    tableId=self.table_cb.currentData(), notes=self.notes_in.text().strip())


class ReservationsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._filter = 'today'
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)
        hdr = QHBoxLayout()
        self.title = lbl('','white',20,True); hdr.addWidget(self.title); hdr.addStretch()
        self.new_b = btn('','amber',36,12); self.new_b.clicked.connect(self._new_res); hdr.addWidget(self.new_b)
        vl.addLayout(hdr)
        tabs_row = QHBoxLayout(); tabs_row.setSpacing(8)
        self._filter_btns = {}
        for fid in ['today','upcoming','all']:
            b = QPushButton(); b.setFixedHeight(30); b.setCheckable(True)
            b.clicked.connect(lambda _,f=fid: self._set_filter(f))
            self._filter_btns[fid] = b; tabs_row.addWidget(b)
        tabs_row.addStretch(); vl.addLayout(tabs_row)
        sr = QHBoxLayout(); sr.setSpacing(10)
        self._st_total    = self._mk_mini('#1c1500','#f59e0b')
        self._st_confirmed= self._mk_mini('#052e16','#22c55e')
        self._st_seated   = self._mk_mini('#0c1a27','#38bdf8')
        self._st_noshow   = self._mk_mini('#111','#4b5563')
        for s in [self._st_total,self._st_confirmed,self._st_seated,self._st_noshow]: sr.addWidget(s)
        vl.addLayout(sr)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.ctn = QWidget(); self.ctn.setStyleSheet('background:transparent;')
        self.body = QVBoxLayout(self.ctn); self.body.setContentsMargins(0,0,0,0); self.body.setSpacing(8)
        sc.setWidget(self.ctn); vl.addWidget(sc)

    def _mk_mini(self, bg, vc):
        c = QWidget(); c.setFixedHeight(56)
        c.setStyleSheet(f'background:{bg};border:1px solid {vc}44;border-radius:12px;')
        vl2 = QVBoxLayout(c); vl2.setAlignment(Qt.AlignmentFlag.AlignCenter); vl2.setSpacing(1)
        v = QLabel('0'); v.setStyleSheet(f'color:{vc};font-size:20px;font-weight:bold;background:transparent;border:none;')
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb= QLabel(''); lb.setStyleSheet('color:#6b7280;font-size:10px;background:transparent;border:none;')
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl2.addWidget(v); vl2.addWidget(lb); c._v=v; c._l=lb; return c

    def _set_filter(self, f):
        self._filter = f; self.refresh()

    def _get_filtered(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        res = APP.reservations
        if self._filter == 'today':
            res = [r for r in res if fmt_date(r['ts'])==today_str]
        elif self._filter == 'upcoming':
            cutoff = int(time.time()*1000)
            res = [r for r in res if r['ts']>=cutoff and r.get('status','pending') not in ('cancelled','noshow')]
        return sorted(res, key=lambda r: r['ts'])

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"📅  {t['res_title']}")
        self.new_b.setText(f"+  {t['new_res']}")
        flabels = dict(today=t['today'], upcoming=t['res_upcoming'], all=t['recent'])
        for fid,b in self._filter_btns.items():
            b.setText(flabels[fid]); active = fid==self._filter
            if active: b.setStyleSheet('QPushButton{background:#f59e0b;border:none;border-radius:14px;color:white;font-size:12px;font-weight:bold;padding:0 14px;}')
            else: b.setStyleSheet('QPushButton{background:transparent;border:1px solid #374151;border-radius:14px;color:#6b7280;font-size:12px;font-weight:bold;padding:0 14px;}QPushButton:hover{color:white;}')
        def sc(status): return sum(1 for r in APP.reservations if r.get('status','pending')==status)
        self._st_total._v.setText(str(len(APP.reservations))); self._st_total._l.setText(t['res_title'][:6])
        self._st_confirmed._v.setText(str(sc('confirmed'))); self._st_confirmed._l.setText(t['res_status_confirmed'])
        self._st_seated._v.setText(str(sc('seated')));      self._st_seated._l.setText(t['res_status_seated'])
        self._st_noshow._v.setText(str(sc('noshow')));      self._st_noshow._l.setText(t['res_status_noshow'])
        while self.body.count():
            i = self.body.takeAt(0)
            if i.widget(): i.widget().deleteLater()
        filtered = self._get_filtered()
        if not filtered:
            self.body.addWidget(lbl(t['no_data'],'#4b5563',13,False,Qt.AlignmentFlag.AlignCenter))
        else:
            groups = defaultdict(list)
            for r in filtered: groups[fmt_date(r['ts'])].append(r)
            today_str = datetime.now().strftime('%Y-%m-%d')
            tmrw_str  = (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d')
            for date_str in sorted(groups):
                day_label = t['today'] if date_str==today_str else (t['tomorrow'] if date_str==tmrw_str else date_str)
                sec = QLabel(day_label.upper())
                sec.setStyleSheet('color:#4b5563;font-size:10px;font-weight:bold;letter-spacing:2px;background:transparent;border:none;padding-top:4px;')
                self.body.addWidget(sec)
                for r in groups[date_str]: self.body.addWidget(self._mk_row(r,t))
        self.body.addStretch()

    def _mk_row(self, r, t):
        status = r.get('status','pending')
        bg,bdr,vc = RES_COLORS.get(status, RES_COLORS['pending'])
        can_manage = APP.user and APP.user.get('role') in ('admin','cashier')
        card = QWidget(); card.setStyleSheet(f'background:{bg};border:1.5px solid {bdr};border-radius:14px;')
        card.setFixedHeight(82)
        hl = QHBoxLayout(card); hl.setContentsMargins(16,0,14,0)
        info = QVBoxLayout(); info.setSpacing(2)
        res_dt = datetime.fromtimestamp(r['ts']/1000)
        time_str = res_dt.strftime('%I:%M %p')
        guests_str = f"{r.get('guests',1)} {t['guests']}"
        table_str  = f"  •  {t['table']} {r.get('tableId','?')}" if r.get('tableId') else ''
        info.addWidget(lbl(f"{time_str}  {guests_str}{table_str}",vc,12,True))
        info.addWidget(lbl(r.get('name','?'),'white',14,True))
        if r.get('phone'): info.addWidget(lbl(r['phone'],'#6b7280',11))
        if r.get('notes'): info.addWidget(lbl(r['notes'],'#4b5563',10))
        hl.addLayout(info); hl.addStretch()
        right = QVBoxLayout(); right.setAlignment(Qt.AlignmentFlag.AlignCenter); right.setSpacing(4)
        sb_lbl = QLabel(_res_status_label(status,t))
        sb_lbl.setStyleSheet(f'background:transparent;color:{vc};font-size:11px;font-weight:bold;border:1px solid {bdr};border-radius:8px;padding:2px 8px;')
        right.addWidget(sb_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        if can_manage and status not in ('cancelled','noshow','seated'):
            act_row = QHBoxLayout(); act_row.setSpacing(4)
            if status=='pending':
                cb2=QPushButton(f"✅"); cb2.setFixedSize(26,26)
                cb2.setStyleSheet('QPushButton{background:#166534;border:none;border-radius:8px;color:#22c55e;font-size:12px;}QPushButton:hover{background:#14532d;}')
                cb2.setToolTip(t['confirm_res'])
                cb2.clicked.connect(lambda _,rid=r['id']: self._update_status(rid,'confirmed'))
                act_row.addWidget(cb2)
            if status=='confirmed':
                sb2=QPushButton(f"🪑"); sb2.setFixedSize(26,26)
                sb2.setStyleSheet('QPushButton{background:#0c4a6e;border:none;border-radius:8px;color:#38bdf8;font-size:12px;}QPushButton:hover{background:#075985;}')
                sb2.setToolTip(t['seat_res'])
                sb2.clicked.connect(lambda _,rid=r['id']: self._update_status(rid,'seated'))
                act_row.addWidget(sb2)
            for ico_tip,st in [('👤',t['noshow_res'])]:
                xb=QPushButton(ico_tip); xb.setFixedSize(26,26)
                xb.setStyleSheet('QPushButton{background:#374151;border:none;border-radius:8px;color:#9ca3af;font-size:11px;}QPushButton:hover{background:#4b5563;}')
                xb.setToolTip(st); xb.clicked.connect(lambda _,rid=r['id']: self._update_status(rid,'noshow'))
                act_row.addWidget(xb)
            eb=QPushButton('✏️'); eb.setFixedSize(26,26)
            eb.setStyleSheet('QPushButton{background:#374151;border:none;border-radius:8px;color:#9ca3af;font-size:11px;}QPushButton:hover{background:#4b5563;}')
            eb.clicked.connect(lambda _,rv=r: self._edit_res(rv)); act_row.addWidget(eb)
            db=QPushButton('🗑️'); db.setFixedSize(26,26)
            db.setStyleSheet('QPushButton{background:#374151;border:none;border-radius:8px;color:#9ca3af;font-size:11px;}QPushButton:hover{background:#881337;}')
            db.clicked.connect(lambda _,rid=r['id']: self._delete_res(rid)); act_row.addWidget(db)
            right.addLayout(act_row)
        hl.addLayout(right)
        return card

    def _new_res(self):
        dlg = ReservationDialog(parent=self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            data=dlg.get_data(); data['id']=uid(); data['status']='pending'; data['createdAt']=int(time.time()*1000)
            APP.reservations.append(data); persist_state(); self.refresh()

    def _edit_res(self, r):
        dlg = ReservationDialog(res=r, parent=self)
        if dlg.exec()==QDialog.DialogCode.Accepted:
            data=dlg.get_data()
            idx=next((i for i,rv in enumerate(APP.reservations) if rv['id']==r['id']),None)
            if idx is not None: APP.reservations[idx].update(data)
            persist_state(); self.refresh()

    def _update_status(self, rid, status):
        r=next((rv for rv in APP.reservations if rv['id']==rid),None)
        if r: r['status']=status; persist_state(); self.refresh()

    def _delete_res(self, rid):
        t=APP.t()
        if QMessageBox.question(self,'',t['delete_res'],QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            APP.reservations=[r for r in APP.reservations if r['id']!=rid]; persist_state(); self.refresh()


# ══════════════════════════════════════════════════════════════
#  WAREHOUSE / INVENTORY SCREEN  (Admin only)
# ══════════════════════════════════════════════════════════════
class WarehouseScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background:transparent;')
        vl = QVBoxLayout(self); vl.setContentsMargins(24,20,24,20); vl.setSpacing(14)

        # Header row
        hdr = QHBoxLayout()
        self.title = lbl('','white',20,True); hdr.addWidget(self.title); hdr.addStretch()
        self.alert_badge = QLabel(); self.alert_badge.hide()
        self.alert_badge.setStyleSheet('background:#1c0510;color:#f43f5e;border:1px solid #881337;border-radius:12px;padding:4px 12px;font-size:12px;font-weight:bold;')
        hdr.addWidget(self.alert_badge)
        vl.addLayout(hdr)

        # Alert threshold setting row
        thresh_card = card_widget('#1c1500','#854d0e',12)
        tl = QHBoxLayout(thresh_card); tl.setContentsMargins(16,10,16,10)
        self.thresh_lbl  = lbl('','#f59e0b',13,True)
        self.thresh_note = lbl('','#6b7280',11)
        info_vl = QVBoxLayout(); info_vl.addWidget(self.thresh_lbl); info_vl.addWidget(self.thresh_note)
        self.thresh_spin = QSpinBox(); self.thresh_spin.setRange(0,999); self.thresh_spin.setFixedSize(90,38)
        self.thresh_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thresh_spin.setStyleSheet('QSpinBox{background:#0a0a0a;border:1px solid #854d0e;border-radius:8px;color:#f59e0b;font-size:16px;font-weight:bold;}')
        tl.addLayout(info_vl); tl.addStretch(); tl.addWidget(self.thresh_spin)
        vl.addWidget(thresh_card)

        # Main list
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet('background:transparent;border:none;')
        self.ctn = QWidget(); self.ctn.setStyleSheet('background:transparent;')
        self.body = QVBoxLayout(self.ctn); self.body.setContentsMargins(0,0,0,0); self.body.setSpacing(6)
        sc.setWidget(self.ctn); vl.addWidget(sc)

        # Save button
        self.save_b = btn('','green',44,13); vl.addWidget(self.save_b)
        self.save_b.clicked.connect(self._save_all)
        self._spins = {}   # mid -> QSpinBox
        self.refresh()

    def refresh(self):
        t = APP.t(); rtl = APP.lang=='ar'
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.title.setText(f"📦  {t['warehouse_title']}")
        self.save_b.setText(f"💾  {t['save_stock']}")
        self.thresh_lbl.setText(t['stock_alert_lbl'])
        self.thresh_note.setText(t['stock_alert_note'])

        alert = int(APP.settings.get('stock_alert',5))
        self.thresh_spin.setValue(alert)

        # Count low stock items
        low_items = []
        for m in APP.menu:
            s = get_stock(m['id'])
            if s != -1 and s <= alert:
                low_items.append(m['a'] if APP.lang=='ar' else m['e'])

        if low_items:
            self.alert_badge.setText(f"⚠️  {t['low_stock_items']}: {len(low_items)}")
            self.alert_badge.show()
        else:
            self.alert_badge.hide()

        # Rebuild items list
        while self.body.count():
            i = self.body.takeAt(0)
            if i.widget(): i.widget().deleteLater()
        self._spins.clear()

        # Section headers per category
        for cat in CATS:
            cat_items = [m for m in APP.menu if m['cat']==cat]
            if not cat_items: continue
            cat_name = cat if APP.lang=='ar' else t['cat_names'].get(cat,cat)
            sec = QLabel(cat_name.upper())
            sec.setStyleSheet('color:#4b5563;font-size:10px;font-weight:bold;letter-spacing:2px;background:transparent;border:none;')
            self.body.addWidget(sec)
            cat_card = card_widget(); cl = QVBoxLayout(cat_card); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
            for idx, m in enumerate(cat_items):
                if idx>0: cl.addWidget(divider())
                cl.addWidget(self._mk_row(m, t, alert))
            self.body.addWidget(cat_card)
        self.body.addStretch()

    def _mk_row(self, m, t, alert):
        stock = get_stock(m['id'])
        is_low = stock != -1 and stock <= alert
        is_out = stock == 0
        name = m['a'] if APP.lang=='ar' else m['e']

        w = QWidget(); w.setFixedHeight(60)
        bg = '#1c0510' if is_out else ('#120c00' if is_low else 'transparent')
        w.setStyleSheet(f'background:{bg};border:none;')
        hl = QHBoxLayout(w); hl.setContentsMargins(16,0,16,0)

        # Name + status
        name_vl = QVBoxLayout(); name_vl.setSpacing(2)
        name_lbl = lbl(name, '#f43f5e' if is_out else ('#f59e0b' if is_low else 'white'), 13, True)
        name_vl.addWidget(name_lbl)
        if is_out:
            name_vl.addWidget(lbl(f"🚫 {t['out_of_stock']}", '#f43f5e', 10))
        elif is_low:
            name_vl.addWidget(lbl(f"⚠️ {t['low_stock_warning']}", '#f59e0b', 10))
        hl.addLayout(name_vl); hl.addStretch()

        # Current qty label
        qty_text = t['unlimited'] if stock==-1 else f"{stock} {t['unit']}"
        hl.addWidget(lbl(qty_text, '#6b7280' if stock==-1 else ('#f43f5e' if is_out else ('#f59e0b' if is_low else '#e5e7eb')), 12, True))
        hl.addSpacing(12)

        # SpinBox for new quantity (-1 for unlimited)
        sp = QSpinBox()
        sp.setRange(-1, 9999)
        sp.setValue(stock)
        sp.setFixedSize(110, 36)
        sp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sp.setSpecialValueText(t['unlimited'])
        border_col = '#f43f5e' if is_out else ('#854d0e' if is_low else '#374151')
        sp.setStyleSheet(f'QSpinBox{{background:#0a0a0a;border:1.5px solid {border_col};border-radius:8px;color:white;font-size:13px;font-weight:bold;}}')
        sp.valueChanged.connect(lambda v, mid=m['id'], s=sp: self._on_change(mid, v, s, alert))
        self._spins[m['id']] = sp
        hl.addWidget(sp)

        # Quick +10 / +50 buttons
        for delta, col in [('+10','gray'),('+50','gray')]:
            qb = QPushButton(delta); qb.setFixedSize(44,32)
            qb.setStyleSheet('QPushButton{background:#1f2937;color:#9ca3af;border:none;border-radius:8px;font-size:11px;font-weight:bold;}QPushButton:hover{background:#374151;color:white;}')
            qb.clicked.connect(lambda _,mid=m['id'],d=int(delta): self._quick_add(mid, d))
            hl.addWidget(qb)

        return w

    def _on_change(self, mid, val, sp, alert):
        # Live color feedback
        if val==0:
            sp.setStyleSheet('QSpinBox{background:#0a0a0a;border:1.5px solid #f43f5e;border-radius:8px;color:#f43f5e;font-size:13px;font-weight:bold;}')
        elif val!=-1 and val<=alert:
            sp.setStyleSheet('QSpinBox{background:#0a0a0a;border:1.5px solid #854d0e;border-radius:8px;color:#f59e0b;font-size:13px;font-weight:bold;}')
        else:
            sp.setStyleSheet('QSpinBox{background:#0a0a0a;border:1.5px solid #374151;border-radius:8px;color:white;font-size:13px;font-weight:bold;}')

    def _quick_add(self, mid, delta):
        if mid not in self._spins: return
        sp = self._spins[mid]
        cur = sp.value()
        sp.setValue(cur + delta if cur != -1 else delta)

    def _save_all(self):
        # Save alert threshold
        APP.settings['stock_alert'] = self.thresh_spin.value()
        # Save all stock values
        for mid, sp in self._spins.items():
            set_stock(mid, sp.value())
        persist_state()
        t = APP.t()
        self.save_b.setText(f"✅ {t['stock_updated']}")
        QTimer.singleShot(2000, lambda: self.save_b.setText(f"💾  {t['save_stock']}"))
        self.refresh()


# ══════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🍴 Restaurant Manager")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)
        self.setStyleSheet(STYLE)

        self.toast   = None
        self._screen = 'tables'

        central = QWidget()
        self.setCentralWidget(central)
        self.root_lay = QVBoxLayout(central)
        self.root_lay.setContentsMargins(0,0,0,0); self.root_lay.setSpacing(0)

        # Top bar
        self.topbar = QWidget(); self.topbar.setFixedHeight(44)
        self.topbar.setStyleSheet('background:#050505;border-bottom:1px solid #0f0f0f;')
        tbl = QHBoxLayout(self.topbar); tbl.setContentsMargins(20,0,20,0)
        self.top_app  = lbl('','#374151',13,True)
        self.top_user = lbl('','#4b5563',12)
        self.switch_user_b = QPushButton('🔁')
        self.switch_user_b.setToolTip('Switch')
        self.switch_user_b.setFixedSize(36, 30)
        self.switch_user_b.setStyleSheet(
            "QPushButton{background:transparent;border:1px solid #111827;color:#9ca3af;border-radius:10px;}"
            "QPushButton:hover{border-color:#f59e0b;color:#f59e0b;background:#0a0a0a;}"
        )
        self.switch_user_b.clicked.connect(self._switch_user)

        tbl.addWidget(self.top_app); tbl.addStretch(); tbl.addWidget(self.top_user); tbl.addWidget(self.switch_user_b)
        self.root_lay.addWidget(self.topbar)

        # Body
        body = QWidget(); body_lay = QHBoxLayout(body); body_lay.setContentsMargins(0,0,0,0); body_lay.setSpacing(0)
        self.root_lay.addWidget(body, stretch=1)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.screen_changed.connect(self._switch_screen)
        self.sidebar.lang_toggled.connect(self._toggle_lang)
        self.sidebar.logout.connect(self._do_logout)
        body_lay.addWidget(self.sidebar)

        # Stack
        self.stack = QStackedWidget(); self.stack.setStyleSheet('background:#0a0a0a;')
        body_lay.addWidget(self.stack, stretch=1)

        # Screens
        self.login_sc   = LoginScreen(); self.login_sc.logged_in.connect(self._on_login)
        self.tables_sc  = TablesScreen(); self.tables_sc.table_clicked.connect(self._open_table)
        self.order_sc   = OrderScreen()
        self.order_sc.go_back.connect(self._back_to_prev)
        self.order_sc.order_sent.connect(self._post_order)
        self.order_sc.order_paid.connect(self._post_order)
        self.kitchen_sc = KitchenScreen()
        self.menu_sc    = MenuScreen()
        self.reports_sc = ReportsScreen()
        self.settings_sc= SettingsScreen()
        self.orders_sc    = OrdersScreen(); self.orders_sc.open_order.connect(self._open_table)
        self.warehouse_sc    = WarehouseScreen()
        self.reservations_sc = ReservationsScreen()
        self.import_export_sc = ImportExportScreen()
        self.import_export_sc.data_changed.connect(self._after_data_changed)

        for sc in [self.login_sc,self.tables_sc,self.order_sc,self.kitchen_sc,
                   self.menu_sc,self.reports_sc,self.settings_sc,self.orders_sc,
                   self.warehouse_sc, self.reservations_sc, self.import_export_sc]:
            self.stack.addWidget(sc)

        # Toast
        self.toast = Toast(central)
        self.toast.setMinimumWidth(200)

        # Kitchen auto-refresh timer
        self._ktimer = QTimer(); self._ktimer.timeout.connect(self._auto_refresh)
        self._ktimer.start(8000)

        self._show_login()

    def _show_login(self):
        self.sidebar.hide(); self.topbar.hide()
        self.login_sc.refresh()
        self.stack.setCurrentWidget(self.login_sc)

    def _on_login(self, user):
        APP.user = user
        self.sidebar.show(); self.topbar.show()
        self.sidebar.build_items(user['role'])
        self.top_app.setText(APP.t()['app_name'])
        self.top_user.setText(f"{APP.t()['welcome']}, {user['name']}  •  {APP.t()['roles'][user['role']]}")
        self.switch_user_b.setToolTip(APP.t().get('switch_user', 'Switch user'))
        first = 'kitchen' if user['role']=='kitchen' else ('orders' if user['role']=='cashier' else 'tables')
        self._switch_screen(first)

    def _switch_screen(self, sid):
        if sid == self._screen and sid != 'order': pass
        self._screen = sid
        self.sidebar.set_active(sid)
        SCREENS = dict(tables=self.tables_sc, orders=self.orders_sc, kitchen=self.kitchen_sc,
                       menu=self.menu_sc, reports=self.reports_sc, settings=self.settings_sc, order=self.order_sc,
                       warehouse=self.warehouse_sc, import_export=self.import_export_sc,
                       reservations=self.reservations_sc)
        sc = SCREENS.get(sid)
        if sc:
            if hasattr(sc,'refresh') and sid!='order': sc.refresh()
            self.stack.setCurrentWidget(sc)

    def _open_table(self, tbl, order):
        self._prev_screen = self._screen
        self.order_sc.load(tbl, order, APP.user['role'])
        self._screen = 'order'
        self.sidebar.set_active('tables')
        self.stack.setCurrentWidget(self.order_sc)

    def _back_to_prev(self):
        self._switch_screen(getattr(self,'_prev_screen','tables'))

    def _post_order(self, msg):
        self.toast.show_msg(msg)
        self._switch_screen(getattr(self,'_prev_screen','tables'))

    def _toggle_lang(self):
        APP.lang = 'en' if APP.lang=='ar' else 'ar'
        rtl = APP.lang=='ar'
        QApplication.instance().setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.top_app.setText(APP.t()['app_name'])
        if APP.user:
            self.top_user.setText(f"{APP.t()['welcome']}, {APP.user['name']}  •  {APP.t()['roles'][APP.user['role']]}")
            self.switch_user_b.setToolTip(APP.t().get('switch_user', 'Switch user'))
        self.sidebar.refresh()
        cur = self._screen
        for sc in [self.tables_sc,self.orders_sc,self.kitchen_sc,self.menu_sc,self.reports_sc,self.settings_sc,self.warehouse_sc,self.reservations_sc,self.import_export_sc]:
            if hasattr(sc,'refresh'): sc.refresh()
        if cur == 'order' and self.order_sc.table:
            self.order_sc._rebuild_ui()

    def _after_data_changed(self):
        self.top_app.setText(APP.t()['app_name'])
        if APP.user:
            self.top_user.setText(f"{APP.t()['welcome']}, {APP.user['name']}  •  {APP.t()['roles'][APP.user['role']]}")
            self.switch_user_b.setToolTip(APP.t().get('switch_user', 'Switch user'))
        self.sidebar.build_items(APP.user['role'] if APP.user else 'admin')
        for sc in [self.tables_sc,self.orders_sc,self.kitchen_sc,self.menu_sc,self.reports_sc,self.settings_sc,self.warehouse_sc,self.reservations_sc,self.import_export_sc]:
            if hasattr(sc,'refresh'):
                sc.refresh()
        if self._screen == 'order':
            self._switch_screen('tables')

    def _do_logout(self):
        APP.user = None
        self._show_login()

    def _switch_user(self):
        APP.user = None
        self._show_login()

    def _auto_refresh(self):
        if APP.user and self._screen in ('tables','kitchen','orders','warehouse','reservations','import_export'):
            sc = dict(tables=self.tables_sc,kitchen=self.kitchen_sc,orders=self.orders_sc,warehouse=self.warehouse_sc,reservations=self.reservations_sc,import_export=self.import_export_sc).get(self._screen)
            if sc and hasattr(sc,'refresh'): sc.refresh()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.toast:
            pw,ph = self.centralWidget().width(), self.centralWidget().height()
            self.toast.move((pw-self.toast.width())//2, ph-self.toast.height()-28)

def run(argv=None) -> int:
    argv = sys.argv if argv is None else argv

    app = QApplication(argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)  # Default Arabic
    app.setStyle('Fusion')

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor('#0a0a0a'))
    pal.setColor(QPalette.ColorRole.WindowText,       QColor('#e5e7eb'))
    pal.setColor(QPalette.ColorRole.Base,             QColor('#111111'))
    pal.setColor(QPalette.ColorRole.AlternateBase,    QColor('#1a1a1a'))
    pal.setColor(QPalette.ColorRole.Text,             QColor('#e5e7eb'))
    pal.setColor(QPalette.ColorRole.Button,           QColor('#1f2937'))
    pal.setColor(QPalette.ColorRole.ButtonText,       QColor('#e5e7eb'))
    pal.setColor(QPalette.ColorRole.Highlight,        QColor('#f59e0b'))
    pal.setColor(QPalette.ColorRole.HighlightedText,  QColor('#000000'))
    app.setPalette(pal)
    app.setStyleSheet(STYLE)

    # ── أول تشغيل: اعرض شاشة إعداد قاعدة البيانات إن لم تكن موجودة ──
    from .db_config import get_config, save_config, _DEFAULTS
    from .db_setup import DBSetupDialog
    from .admin_auth import ensure_admin_password_exists
    if not get_config().get("setup_completed", False):
        dlg = DBSetupDialog()
        dlg.exec()
        # نضمن وجود setup_completed=True دائماً بعد إغلاق الشاشة (حتى لو
        # المستخدم ألغى أو قفل النافذة بدون ضغط "حفظ") لتفادي إعادة عرضها كل تشغيل.
        if not get_config().get("setup_completed", False):
            save_config({**_DEFAULTS, "setup_completed": True})

    # يضمن وجود كلمة مرور مدير عشوائية وآمنة (لا توجد قيمة ثابتة في الكود).
    ensure_admin_password_exists()

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(run())
