import sys
import os
import datetime
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox, QCheckBox,
    QStackedWidget, QFrame, QDialog, QMessageBox, QSystemTrayIcon, QMenu, QSizePolicy, QProgressBar,
    QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QTime, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QAction

from config_manager import ConfigManager
from audio_manager import AudioManager
from app_blocker import AppBlocker
from asset_helper import get_asset_path, get_tinted_pixmap
from overlays import WaterOverlayWindow, PushupsOverlayWindow, StartScheduleOverlayWindow, ExerciseOverlayWindow, EXERCISES_LIST

MOTIVATIONAL_STUDY_QUOTES = [
    "💡 استمر! كل دقيقة تدرسها الآن تقربك من هدفك العظيم.",
    "🔥 العزيمة هي القوة التي تحول الأحلام إلى واقع. واصل التركيز!",
    "🎯 النجاح هو مجمل خطوات صغيرة تتكرر يومياً. أنت تصنع مستقبلك الآن!",
    "⭐ تذكر لماذا بدأت! التركيز اليوم هو سر التميز غداً.",
    "🧠 عقلك يتعلم وينمو مع كل معلومة تقرأها. أحسنت الصنع!",
    "🚀 لا تتوقف عندما تتعب، توقف عندما تنتهي! أنت أقوى من المشتتات.",
    "💎 الإنتاجية ليست حظاً، بل هي التزام وشغف. واصل بطل!",
    "🏆 الإنجاز الحقيقي يبدأ بالانضباط الذاتي. أنت في الطريق الصحيح.",
    "⚡ التركيز العميق هو مهارة الناجحين. ابقَ متيقظاً ومتحفزاً!",
    "🌟 كل دقيقة تركيز هي استثمار في مستقبلك الباهر!"
]

def format_12h(time_str):
    """Converts '16:00' to '04:00 مساءً'."""
    try:
        t = QTime.fromString(time_str, "hh:mm")
        h = t.hour()
        m = t.minute()
        am_pm = "مساءً" if h >= 12 else "صباحاً"
        h_12 = h % 12
        if h_12 == 0:
            h_12 = 12
        return f"{h_12:02d}:{m:02d} {am_pm}"
    except Exception:
        return time_str

RANKS = [
    (0,       "مبتدئ أول 🥉",      "#94A3B8", "بداية الرحلة والالتزام 🌱"),
    (300,     "مبتدئ ثاني 🥉",     "#94A3B8", "خطوات ثابتة نحو النجاح 🚶‍♂️"),
    (800,     "مبتدئ ثالث 🥉",     "#94A3B8", "تأسيس عادة التركيز اليومية 🎯"),
    (1500,    "متقدم أول 🥈",      "#38BDF8", "انطلاقة قوية وزيادة الإنتاجية 🚀"),
    (3000,    "متقدم ثاني 🥈",     "#38BDF8", "تجاوز المشتتات بثقة 💪"),
    (5000,    "متقدم ثالث 🥈",     "#38BDF8", "إتقان إدارة الوقت والجهد ⏱️"),
    (8000,    "مجتهد أول 🥇",      "#F59E0B", "التزام عالي وأثر ملموس 🌟"),
    (12000,   "مجتهد ثاني 🥇",     "#F59E0B", "شغف متواصل بدون توقف 🔥"),
    (17000,   "مجتهد ثالث 🥇",     "#F59E0B", "نموذج يُحتذى به في الانضباط 🏆"),
    (23000,   "متفوق أول 💠",      "#A855F7", "تركيز عميق وإنجازات متتالية 💎"),
    (30000,   "متفوق ثاني 💠",     "#A855F7", "قوة إرادة وصمود في وجه التشتت 🛡️"),
    (38000,   "متفوق ثالث 💠",     "#A855F7", "أداء استثنائي يتجاوز التوقعات ⚡"),
    (48000,   "نخبة أول 👑",       "#EC4899", "المربع الذهبي للإنتاجية العالية 👑"),
    (60000,   "نخبة ثاني 👑",       "#EC4899", "إتقان شامل واستمرارية بلا استسلام 🛡️"),
    (72000,   "نخبة ثالث 👑",       "#EC4899", "من القلائل الذين وصلوا لهذه المهارة 🔥"),
    (82000,   "قدوة عظيمة 🌟",     "#EAB308", "مكانة رفيعة وإنجاز يومي مبهر 🌟"),
    (90000,   "قدوة تاريخية 🌌",   "#3B82F6", "رمز حقيقي للتركيز والمثابرة 🌌"),
    (100000,  "قدوة اسطورية ⚡",   "#EF4444", "قمة المجد! أسطورة خالدة في الإنتاجية 👑⚡"),
]

ALL_BADGES = [
    # 💧 قسم الماء (6 أوسمة)
    {"id": "b_water_1", "cat": "water", "title": "💧 قطرة البداية",        "desc": "شرب 3 أكواب ماء في يوم واحد",     "pts": 20,  "water_min": 3},
    {"id": "b_water_2", "cat": "water", "title": "🚿 المنتعش",              "desc": "شرب 6 أكواب في يوم واحد",         "pts": 40,  "water_min": 6},
    {"id": "b_water_3", "cat": "water", "title": "🌊 نهر الانتعاش",         "desc": "شرب 20 كوب إجمالاً",              "pts": 80,  "water_total": 20},
    {"id": "b_water_4", "cat": "water", "title": "🐳 محيط الهيدرات",        "desc": "شرب 50 كوب إجمالاً",              "pts": 150, "water_total": 50},
    {"id": "b_water_5", "cat": "water", "title": "🌍 بحر الصحة",            "desc": "شرب 100 كوب إجمالاً",             "pts": 280, "water_total": 100},
    {"id": "b_water_6", "cat": "water", "title": "🔱 سيد المياه الأبدي",    "desc": "شرب 250 كوب إجمالاً",             "pts": 500, "water_total": 250},

    # 🏋️ قسم التمارين (6 أوسمة)
    {"id": "b_pushups_1", "cat": "pushups", "title": "🏋️ الدفعة الأولى",   "desc": "إنجاز 10 ضغطات في جلسة واحدة",   "pts": 25,  "pushups_min": 10},
    {"id": "b_pushups_2", "cat": "pushups", "title": "💪 عضلات من حديد",    "desc": "إنجاز 30 ضغطة في جلسة واحدة",     "pts": 50,  "pushups_min": 30},
    {"id": "b_pushups_3", "cat": "pushups", "title": "🥊 المقاتل الصلب",    "desc": "إنجاز 100 ضغطة إجمالاً",           "pts": 120, "pushups_total": 100},
    {"id": "b_pushups_4", "cat": "pushups", "title": "🦾 أسد القوة",        "desc": "إنجاز 300 ضغطة إجمالاً",           "pts": 250, "pushups_total": 300},
    {"id": "b_pushups_5", "cat": "pushups", "title": "🏆 وحش اللياقة",      "desc": "إنجاز 750 ضغطة إجمالاً",           "pts": 450, "pushups_total": 750},
    {"id": "b_pushups_6", "cat": "pushups", "title": "⚡ إله التمارين",      "desc": "إنجاز 1500 ضغطة إجمالاً",          "pts": 800, "pushups_total": 1500},

    # 🎓 قسم التعلم والتركيز (7 أوسمة)
    {"id": "b_learn_1", "cat": "learn", "title": "🎓 شرارة التركيز",        "desc": "30 دقيقة تعلم في يوم واحد",       "pts": 30,  "learn_day": 30},
    {"id": "b_learn_2", "cat": "learn", "title": "📖 الطالب المجتهد",       "desc": "60 دقيقة تعلم في يوم واحد",       "pts": 60,  "learn_day": 60},
    {"id": "b_learn_3", "cat": "learn", "title": "🧠 عقل من نار",           "desc": "120 دقيقة تعلم في يوم واحد",      "pts": 120, "learn_day": 120},
    {"id": "b_learn_4", "cat": "learn", "title": "🚀 المتعلم الشغوف",       "desc": "300 دقيقة تعلم إجمالاً (5 ساعات)","pts": 200, "learn_total": 300},
    {"id": "b_learn_5", "cat": "learn", "title": "🌌 عقلية العلماء",        "desc": "1200 دقيقة (20 ساعة) إجمالاً",    "pts": 450, "learn_total": 1200},
    {"id": "b_learn_6", "cat": "learn", "title": "👁️ سيد المعرفة",          "desc": "3000 دقيقة (50 ساعة) إجمالاً",    "pts": 900, "learn_total": 3000},
    {"id": "b_learn_7", "cat": "learn", "title": "🌟 أسطورة التعلم",        "desc": "6000 دقيقة (100 ساعة) إجمالاً",   "pts": 1500,"learn_total": 6000},

    # 📋 قسم المهام (6 أوسمة)
    {"id": "b_tasks_1", "cat": "tasks", "title": "📝 خطوة الألف ميل",       "desc": "إكمال أول مهمة يومية",            "pts": 20,  "tasks_done": 1},
    {"id": "b_tasks_2", "cat": "tasks", "title": "✅ منجز اليوم",            "desc": "إكمال 5 مهام في يوم واحد",         "pts": 50,  "tasks_done": 5},
    {"id": "b_tasks_3", "cat": "tasks", "title": "📋 قاهر المهام",           "desc": "إكمال 10 مهام إجمالاً",            "pts": 100, "tasks_total": 10},
    {"id": "b_tasks_4", "cat": "tasks", "title": "🎯 قناص الأهداف",          "desc": "إكمال 30 مهمة إجمالاً",            "pts": 250, "tasks_total": 30},
    {"id": "b_tasks_5", "cat": "tasks", "title": "🔥 آلة الإنجاز",           "desc": "إكمال 75 مهمة إجمالاً",            "pts": 450, "tasks_total": 75},
    {"id": "b_tasks_6", "cat": "tasks", "title": "👑 ملك الإنجاز الأبدي",   "desc": "إكمال 200 مهمة إجمالاً",           "pts": 800, "tasks_total": 200},

    # ⚡ قسم النقاط والرانك (5 أوسمة خاصة)
    {"id": "b_score_1",  "cat": "score", "title": "🌱 أول خطوة",            "desc": "جمع 300 نقطة",                      "pts": 0,   "score_min": 300},
    {"id": "b_score_2",  "cat": "score", "title": "🔥 ألفان نقطة",          "desc": "جمع 2000 نقطة إجمالاً",            "pts": 0,   "score_min": 2000},
    {"id": "b_score_3",  "cat": "score", "title": "💎 نادي العشرة آلاف",    "desc": "جمع 10000 نقطة إجمالاً",           "pts": 0,   "score_min": 10000},
    {"id": "b_score_4",  "cat": "score", "title": "👑 سيد النقاط",          "desc": "جمع 50000 نقطة إجمالاً",           "pts": 0,   "score_min": 50000},
    {"id": "b_score_5",  "cat": "score", "title": "🌌 اسطورة الأوسمة",     "desc": "جمع 100000 نقطة إجمالاً (القمة)",  "pts": 0,   "score_min": 100000},
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cfg_mgr = ConfigManager()
        self.config = self.cfg_mgr.config
        self.audio_mgr = AudioManager(enabled=self.config.get("sound_enabled", True))
        self.app_blocker = AppBlocker(audio_mgr=self.audio_mgr)
        self.app_blocker.set_blocked_apps(self.config.get("blocked_apps", []))
        self.app_blocker.set_blocked_websites(self.config.get("blocked_websites", []))

        # Check daily stats reset
        today_str = datetime.date.today().isoformat()
        if self.config.get("daily_stats", {}).get("date") != today_str:
            self.config["daily_stats"] = {
                "date": today_str,
                "water_count": 0,
                "pushups_count": 0,
                "learning_minutes": 0
            }
            self.cfg_mgr.save_config()

        self.water_timer_counter = 0
        self.pushups_timer_counter = 0
        self.study_motivate_counter = 0
        self.last_triggered_schedule_key = ""

        # ✅ منع تكرار شاشات التذكير
        self._water_overlay_open = False
        self._pushups_overlay_open = False
        self._schedule_overlay_open = False

        self.current_task_filter = "all"
        self.current_badge_filter = "all"

        self.setWindowTitle("مركز الإنتاجية الذكي | Productivity Hub")
        self.resize(1080, 740)
        self.setMinimumSize(940, 660)

        self.setup_styles()
        self.setup_ui()
        self.setup_system_tray()
        self.setup_background_timers()

        # Initial button state check
        is_session_active = self.config.get("manual_session_active", False)
        self.app_blocker.is_active = is_session_active
        self.update_status_ui(is_session_active)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #090D16;
            }
            QWidget {
                color: #F8FAFC;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#Sidebar {
                background-color: #0F172A;
                border-right: 1px solid #1E293B;
            }
            QPushButton#NavBtn {
                background-color: transparent;
                color: #94A3B8;
                font-size: 17px;
                font-weight: bold;
                text-align: left;
                padding: 14px 18px;
                border-radius: 12px;
                border: none;
            }
            QPushButton#NavBtn:hover {
                background-color: #1E293B;
                color: #38BDF8;
            }
            QPushButton#NavBtn[active="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                border-left: 4px solid #38BDF8;
            }
            QFrame#Card {
                background-color: #111827;
                border: 1px solid #1F293D;
                border-radius: 20px;
                padding: 22px;
            }
            QLabel#CardTitle {
                font-size: 22px;
                font-weight: bold;
                color: #38BDF8;
            }
            QLabel#StatValue {
                font-size: 36px;
                font-weight: bold;
                color: #38BDF8;
            }
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: white;
                font-size: 17px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 12px;
                border: 1px solid #38BDF8;
            }
            QPushButton#PrimaryBtn:hover {
                background: #0284C7;
            }
            QPushButton#PresetBtn {
                background: rgba(14, 165, 233, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38BDF8;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 18px;
                border-radius: 12px;
            }
            QPushButton#PresetBtn:hover {
                background: #0284C7;
                color: white;
                border-color: #38BDF8;
            }
            QPushButton#FinishBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #991B1B);
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 14px 28px;
                border-radius: 12px;
                border: 1px solid #EF4444;
            }
            QPushButton#FinishBtn:hover {
                background: #EF4444;
            }
            QPushButton#IconTrashBtn {
                background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 10px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }
            QPushButton#IconTrashBtn:hover {
                background-color: #DC2626;
                border-color: #EF4444;
            }
            QListWidget {
                background-color: #0B0F19;
                border: 1px solid #1F293D;
                border-radius: 14px;
                padding: 10px;
                font-size: 16px;
            }
            QListWidget::item {
                background-color: #111827;
                border: 1px solid #1F293D;
                border-radius: 12px;
                margin-bottom: 8px;
            }
            QListWidget::item:hover {
                background-color: #1F293D;
            }
            QLineEdit, QComboBox {
                background-color: #0B0F19;
                border: 1px solid #1F293D;
                border-radius: 10px;
                padding: 10px 14px;
                color: #F8FAFC;
                font-size: 16px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #0F172A;
                color: white;
                selection-background-color: #0284C7;
            }
            QCheckBox {
                font-size: 16px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 1px solid #1F293D;
                background-color: #0B0F19;
            }
            QCheckBox::indicator:checked {
                background-color: #0284C7;
                border-color: #38BDF8;
            }
            QProgressBar {
                background-color: #0B0F19;
                border: 1px solid #1F293D;
                border-radius: 10px;
                height: 24px;
                text-align: center;
                color: #F8FAFC;
                font-weight: bold;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #10B981);
                border-radius: 9px;
            }
            QPushButton#FilterBtn {
                background-color: #1E293B;
                color: #94A3B8;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QPushButton#FilterBtn:hover {
                background-color: #334155;
                color: white;
            }
            QPushButton#FilterBtn[active="true"] {
                background-color: #0284C7;
                color: white;
                border-color: #38BDF8;
            }
        """)

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(270)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        sidebar_layout.setSpacing(14)

        # Header with ORIGINAL natural logo
        header_box = QHBoxLayout()
        logo_path = get_asset_path("logo.png")
        if logo_path and os.path.exists(logo_path):
            logo_lbl = QLabel()
            pix = QPixmap(logo_path).scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            header_box.addWidget(logo_lbl)

        app_title = QLabel("مركز الإنتاجية")
        app_title.setStyleSheet("font-size: 23px; font-weight: bold; color: #38BDF8;")
        header_box.addWidget(app_title)
        header_box.addStretch()

        sidebar_layout.addLayout(header_box)
        sidebar_layout.addSpacing(15)

        self.btn_nav_dash = self.create_nav_button(" الرئيسية", "homelogo.png", 0)
        self.btn_nav_tasks = self.create_nav_button(" المهام اليومية", "bullseye-arrowlogo.png", 1)
        self.btn_nav_badge = self.create_nav_button(" الإحصائيات والأوسمة", "bullseye-arrowlogo.png", 2)
        self.btn_nav_sched = self.create_nav_button(" جدول التعلم", "calendarlogo.png", 3)
        self.btn_nav_block = self.create_nav_button(" التطبيقات الممنوعة", "forbiddenapps.png", 4)
        self.btn_nav_web_block = self.create_nav_button(" المواقع المحظورة", "forbiddenapps.png", 5)
        self.btn_nav_sets = self.create_nav_button(" الإعدادات والاختبار", "settingslogo.png", 6)

        self.btn_nav_dash.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_nav_dash)
        sidebar_layout.addWidget(self.btn_nav_tasks)
        sidebar_layout.addWidget(self.btn_nav_badge)
        sidebar_layout.addWidget(self.btn_nav_sched)
        sidebar_layout.addWidget(self.btn_nav_block)
        sidebar_layout.addWidget(self.btn_nav_web_block)
        sidebar_layout.addWidget(self.btn_nav_sets)
        sidebar_layout.addStretch()

        ver_lbl = QLabel("الإصدار الأسطوري 6.0 ⚡")
        ver_lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(ver_lbl)

        # Stacked Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_dashboard_page())
        self.pages.addWidget(self.create_tasks_page())
        self.pages.addWidget(self.create_analytics_page())
        self.pages.addWidget(self.create_schedules_page())
        self.pages.addWidget(self.create_blocked_apps_page())
        self.pages.addWidget(self.create_blocked_websites_page())
        self.pages.addWidget(self.create_settings_page())

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

    def create_nav_button(self, text, icon_filename, page_index):
        btn = QPushButton(text)
        btn.setObjectName("NavBtn")
        btn.setCursor(Qt.PointingHandCursor)

        pix = get_tinted_pixmap(icon_filename, "#FFFFFF", QSize(24, 24))
        if not pix.isNull():
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(24, 24))

        btn.clicked.connect(lambda: self.switch_page(page_index))
        return btn

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        nav_btns = [self.btn_nav_dash, self.btn_nav_tasks, self.btn_nav_badge, self.btn_nav_sched, self.btn_nav_block, self.btn_nav_web_block, self.btn_nav_sets]
        for i, btn in enumerate(nav_btns):
            btn.setProperty("active", "true" if i == index else "false")
            btn.setStyle(btn.style())

    # Page 1: Dashboard
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(22)

        # Status Card
        self.status_card = QFrame()
        self.status_card.setObjectName("Card")
        self.status_card.setStyleSheet("background-color: #111827; border-left: 6px solid #64748B;")

        status_layout = QHBoxLayout(self.status_card)
        
        status_info = QVBoxLayout()
        self.lbl_status_title = QLabel("حالة جلسة التعلم: غير نشطة")
        self.lbl_status_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #94A3B8;")
        self.lbl_status_desc = QLabel("عند بدء التعلم، يتم حظر التطبيقات الممنوعة تلقائياً لحمايتك من التشتت.")
        self.lbl_status_desc.setStyleSheet("font-size: 15px; color: #CBD5E1;")
        
        status_info.addWidget(self.lbl_status_title)
        status_info.addWidget(self.lbl_status_desc)

        # Action Buttons Layout
        btn_box = QVBoxLayout()
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_start_learning = QPushButton(" بدء جلسة التعلم الآن")
        self.btn_start_learning.setObjectName("PrimaryBtn")
        self.btn_start_learning.setCursor(Qt.PointingHandCursor)
        play_pix = get_tinted_pixmap("playlogonotpauselogolikeinyoutube.png", "#FFFFFF", QSize(26, 26))
        if not play_pix.isNull():
            self.btn_start_learning.setIcon(QIcon(play_pix))
            self.btn_start_learning.setIconSize(QSize(26, 26))
        self.btn_start_learning.clicked.connect(self.start_manual_session)

        self.btn_finish_learning = QPushButton(" لقد أنهيت التعلم")
        self.btn_finish_learning.setObjectName("FinishBtn")
        self.btn_finish_learning.setCursor(Qt.PointingHandCursor)
        pause_pix = get_tinted_pixmap("pauselogo.png", "#FFFFFF", QSize(26, 26))
        if not pause_pix.isNull():
            self.btn_finish_learning.setIcon(QIcon(pause_pix))
            self.btn_finish_learning.setIconSize(QSize(26, 26))
        self.btn_finish_learning.clicked.connect(self.finish_learning_session)

        btn_box.addWidget(self.btn_start_learning)
        btn_box.addWidget(self.btn_finish_learning)

        status_layout.addLayout(status_info)
        status_layout.addStretch()
        status_layout.addLayout(btn_box)

        layout.addWidget(self.status_card)

        # Stats Header
        stats_header = QHBoxLayout()
        target_pix = get_tinted_pixmap("bullseye-arrowlogo.png", "#38BDF8", QSize(32, 32))
        if not target_pix.isNull():
            ic_lbl = QLabel()
            ic_lbl.setPixmap(target_pix)
            stats_header.addWidget(ic_lbl)

        stats_title = QLabel("إحصائيات الإنجاز اليومي")
        stats_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F8FAFC;")
        stats_header.addWidget(stats_title)
        stats_header.addStretch()

        layout.addLayout(stats_header)

        # Stats Grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(18)

        # Water Stat
        card_water = QFrame()
        card_water.setObjectName("Card")
        wl = QVBoxLayout(card_water)
        water_pix = get_tinted_pixmap("waterlogo.png", "#38BDF8", QSize(48, 48))
        if not water_pix.isNull():
            w_ic = QLabel()
            w_ic.setPixmap(water_pix)
            wl.addWidget(w_ic)
        wl.addWidget(QLabel("شرب الماء اليومي"))
        self.lbl_stat_water = QLabel(f"{self.config['daily_stats']['water_count']} أكواب")
        self.lbl_stat_water.setObjectName("StatValue")
        self.lbl_stat_water.setStyleSheet("color: #38BDF8;")
        wl.addWidget(self.lbl_stat_water)

        # Pushups Stat
        card_pushups = QFrame()
        card_pushups.setObjectName("Card")
        pl = QVBoxLayout(card_pushups)
        gym_pix = get_tinted_pixmap("gymlogo.png", "#FB923C", QSize(48, 48))
        if not gym_pix.isNull():
            g_ic = QLabel()
            g_ic.setPixmap(gym_pix)
            pl.addWidget(g_ic)
        pl.addWidget(QLabel("تمارين الضغط"))
        self.lbl_stat_pushups = QLabel(f"{self.config['daily_stats']['pushups_count']} ضغطات")
        self.lbl_stat_pushups.setObjectName("StatValue")
        self.lbl_stat_pushups.setStyleSheet("color: #FB923C;")
        pl.addWidget(self.lbl_stat_pushups)

        # Learning Time Stat
        card_session = QFrame()
        card_session.setObjectName("Card")
        sl = QVBoxLayout(card_session)
        clock_pix = get_tinted_pixmap("clocklogo.png", "#10B981", QSize(48, 48))
        if not clock_pix.isNull():
            c_ic = QLabel()
            c_ic.setPixmap(clock_pix)
            sl.addWidget(c_ic)
        sl.addWidget(QLabel("وقت التعلم اليوم"))
        self.lbl_stat_time = QLabel(f"{self.config['daily_stats']['learning_minutes']} دقيقة")
        self.lbl_stat_time.setObjectName("StatValue")
        self.lbl_stat_time.setStyleSheet("color: #10B981;")
        sl.addWidget(self.lbl_stat_time)

        stats_grid.addWidget(card_water)
        stats_grid.addWidget(card_pushups)
        stats_grid.addWidget(card_session)

        layout.addLayout(stats_grid)

        # 📋 To-Do List Card
        card_tasks = QFrame()
        card_tasks.setObjectName("Card")
        tasks_layout = QVBoxLayout(card_tasks)
        tasks_layout.setSpacing(14)

        # Header Row
        tasks_header = QHBoxLayout()
        lbl_tasks_title = QLabel("📋 قائمة المهام اليومية")
        lbl_tasks_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        
        self.lbl_task_progress = QLabel("إنجاز المهام: 0%")
        self.lbl_task_progress.setStyleSheet("font-size: 15px; font-weight: bold; color: #10B981;")

        # Filter Buttons
        filter_box = QHBoxLayout()
        filter_box.setSpacing(6)
        self.btn_filter_all = QPushButton("الكل")
        self.btn_filter_active = QPushButton("النشطة ⏳")
        self.btn_filter_completed = QPushButton("المكتملة ✅")

        for b, f_val in [(self.btn_filter_all, "all"), (self.btn_filter_active, "active"), (self.btn_filter_completed, "completed")]:
            b.setObjectName("FilterBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda ch, val=f_val: self.set_task_filter(val))

        filter_box.addWidget(self.btn_filter_all)
        filter_box.addWidget(self.btn_filter_active)
        filter_box.addWidget(self.btn_filter_completed)

        tasks_header.addWidget(lbl_tasks_title)
        tasks_header.addSpacing(15)
        tasks_header.addLayout(filter_box)
        tasks_header.addStretch()
        tasks_header.addWidget(self.lbl_task_progress)
        tasks_layout.addLayout(tasks_header)

        # Progress Bar
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setRange(0, 100)
        self.task_progress_bar.setValue(0)
        tasks_layout.addWidget(self.task_progress_bar)

        # Add Task Input Row
        add_task_box = QHBoxLayout()
        self.txt_task_input = QLineEdit()
        self.txt_task_input.setPlaceholderText("اكتب مهمة جديدة هنا وأضغط إضافة أو Enter...")
        self.txt_task_input.returnPressed.connect(self.add_task)

        btn_add_task = QPushButton("إضافة مهمة ➕")
        btn_add_task.setObjectName("PrimaryBtn")
        btn_add_task.setCursor(Qt.PointingHandCursor)
        btn_add_task.clicked.connect(self.add_task)

        add_task_box.addWidget(self.txt_task_input, 1)
        add_task_box.addWidget(btn_add_task, 0)
        tasks_layout.addLayout(add_task_box)

        # List Widget for Tasks
        self.list_tasks = QListWidget()
        self.list_tasks.setMinimumHeight(150)
        self.list_tasks.setMaximumHeight(220)
        tasks_layout.addWidget(self.list_tasks)

        layout.addWidget(card_tasks)
        self.reload_tasks_list()

        return page

    # Page 1.5: Dedicated Tasks Page (Full spacious view for daily tasks)
    def create_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Title Row
        title_box = QHBoxLayout()
        target_pix = get_tinted_pixmap("bullseye-arrowlogo.png", "#38BDF8", QSize(36, 36))
        if not target_pix.isNull():
            ic_lbl = QLabel()
            ic_lbl.setPixmap(target_pix)
            title_box.addWidget(ic_lbl)

        title = QLabel("📋 قائمة المهام والتركيز اليومي")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F8FAFC;")
        title_box.addWidget(title)
        title_box.addStretch()

        layout.addLayout(title_box)

        desc = QLabel("نظّم مهامك وأهدافك اليومية، تابع نسبة الإنجاز واستمتع بيوم أكثر إنتاجية بدون مشتتات.")
        desc.setStyleSheet("color: #94A3B8; font-size: 15px;")
        layout.addWidget(desc)

        # Top Overview Card (3 Stat Columns: Total, Pending, Completed + Progress Bar)
        overview_card = QFrame()
        overview_card.setObjectName("Card")
        ov_layout = QVBoxLayout(overview_card)
        ov_layout.setSpacing(14)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        # Total Card
        c_tot = QFrame()
        c_tot.setStyleSheet("background-color: #0B0F19; border: 1px solid #1F293D; border-radius: 14px; padding: 12px 16px;")
        l_tot = QVBoxLayout(c_tot)
        l_tot.addWidget(QLabel("إجمالي المهام"))
        self.lbl_task_stat_total = QLabel("0")
        self.lbl_task_stat_total.setObjectName("StatValue")
        self.lbl_task_stat_total.setStyleSheet("font-size: 26px; color: #38BDF8; font-weight: bold;")
        l_tot.addWidget(self.lbl_task_stat_total)

        # Pending Card
        c_pen = QFrame()
        c_pen.setStyleSheet("background-color: #0B0F19; border: 1px solid #1F293D; border-radius: 14px; padding: 12px 16px;")
        l_pen = QVBoxLayout(c_pen)
        l_pen.addWidget(QLabel("قيد الانتظار ⏳"))
        self.lbl_task_stat_pending = QLabel("0")
        self.lbl_task_stat_pending.setObjectName("StatValue")
        self.lbl_task_stat_pending.setStyleSheet("font-size: 26px; color: #FB923C; font-weight: bold;")
        l_pen.addWidget(self.lbl_task_stat_pending)

        # Completed Card
        c_don = QFrame()
        c_don.setStyleSheet("background-color: #0B0F19; border: 1px solid #1F293D; border-radius: 14px; padding: 12px 16px;")
        l_don = QVBoxLayout(c_don)
        l_don.addWidget(QLabel("المهام المكتملة ✅"))
        self.lbl_task_stat_done = QLabel("0")
        self.lbl_task_stat_done.setObjectName("StatValue")
        self.lbl_task_stat_done.setStyleSheet("font-size: 26px; color: #10B981; font-weight: bold;")
        l_don.addWidget(self.lbl_task_stat_done)

        stats_row.addWidget(c_tot)
        stats_row.addWidget(c_pen)
        stats_row.addWidget(c_don)
        ov_layout.addLayout(stats_row)

        # Progress Bar Header
        pb_header = QHBoxLayout()
        lbl_pb_title = QLabel("مؤشر إنجاز اليوم:")
        lbl_pb_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC;")
        self.lbl_task_page_percent = QLabel("0%")
        self.lbl_task_page_percent.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")

        pb_header.addWidget(lbl_pb_title)
        pb_header.addStretch()
        pb_header.addWidget(self.lbl_task_page_percent)
        ov_layout.addLayout(pb_header)

        self.task_page_progress_bar = QProgressBar()
        self.task_page_progress_bar.setRange(0, 100)
        self.task_page_progress_bar.setValue(0)
        ov_layout.addWidget(self.task_page_progress_bar)

        layout.addWidget(overview_card)

        # Add Task Input Box Card
        add_card = QFrame()
        add_card.setObjectName("Card")
        add_layout = QHBoxLayout(add_card)
        add_layout.setSpacing(12)

        self.txt_task_page_input = QLineEdit()
        self.txt_task_page_input.setPlaceholderText("اكتب المهمة الجديدة هنا (مثال: مذاكرة 40 دقيقة لغة عربية)...")
        self.txt_task_page_input.setStyleSheet("font-size: 16px; padding: 10px 14px;")
        self.txt_task_page_input.returnPressed.connect(self.add_task_from_page)

        btn_add = QPushButton("➕ إضافة المهمة الآن")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("padding: 10px 20px; font-size: 16px;")
        btn_add.clicked.connect(self.add_task_from_page)

        add_layout.addWidget(self.txt_task_page_input, 1)
        add_layout.addWidget(btn_add)
        layout.addWidget(add_card)

        # Filter Buttons & Main Task List
        filter_header = QHBoxLayout()
        lbl_list_title = QLabel("قائمة المهام اليومية:")
        lbl_list_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F8FAFC;")
        filter_header.addWidget(lbl_list_title)
        filter_header.addSpacing(15)

        filter_box = QHBoxLayout()
        filter_box.setSpacing(8)
        self.btn_filter_page_all = QPushButton("الكل")
        self.btn_filter_page_active = QPushButton("النشطة ⏳")
        self.btn_filter_page_completed = QPushButton("المكتملة ✅")

        for b, f_val in [(self.btn_filter_page_all, "all"), (self.btn_filter_page_active, "active"), (self.btn_filter_page_completed, "completed")]:
            b.setObjectName("FilterBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda ch, val=f_val: self.set_task_filter(val))

        filter_box.addWidget(self.btn_filter_page_all)
        filter_box.addWidget(self.btn_filter_page_active)
        filter_box.addWidget(self.btn_filter_page_completed)

        filter_header.addLayout(filter_box)
        filter_header.addStretch()
        layout.addLayout(filter_header)

        # Large Spacious Task List Widget
        self.list_tasks_page = QListWidget()
        self.list_tasks_page.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.list_tasks_page)

        return page

    # Page 1.8: Analytics & Gamification Showcase
    def create_analytics_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Scroll Area to hold everything
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background: #0B0F19; width: 8px; border-radius: 4px; } QScrollBar::handle:vertical { background: #1F293D; border-radius: 4px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        scroll.setWidget(scroll_widget)
        page_layout.addWidget(scroll)

        # ── Header ──────────────────────────────────────────────────────────
        title_box = QHBoxLayout()
        title = QLabel("🏆 مركز الإنجاز والأوسمة")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #F8FAFC;")
        title_box.addWidget(title)
        title_box.addStretch()
        layout.addLayout(title_box)

        desc = QLabel("تابع رانكك، نقاطك، وأوسمة إنجازك. كل عمل صغير يصنع فرقاً كبيراً! 🚀")
        desc.setStyleSheet("color: #94A3B8; font-size: 15px;")
        layout.addWidget(desc)

        # ── Rank & Score Card ────────────────────────────────────────────────
        rank_card = QFrame()
        rank_card.setObjectName("Card")
        rank_card.setStyleSheet("""
            QFrame#Card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A1040, stop:0.5 #111827, stop:1 #0F1C2E);
                border: 1px solid #2D3A50;
                border-radius: 20px;
            }
        """)
        rc_layout = QVBoxLayout(rank_card)
        rc_layout.setContentsMargins(26, 22, 26, 22)
        rc_layout.setSpacing(14)

        # Top row: score + rank badge
        top_row = QHBoxLayout()

        score_vbox = QVBoxLayout()
        score_label_title = QLabel("⚡ نقاط الإنتاجية")
        score_label_title.setStyleSheet("font-size: 15px; color: #94A3B8; font-weight: bold;")
        self.lbl_user_score_value = QLabel(f"{self.config.get('user_score', 0)}")
        self.lbl_user_score_value.setStyleSheet("font-size: 52px; font-weight: bold; color: #F59E0B;")
        score_pts_lbl = QLabel("نقطة")
        score_pts_lbl.setStyleSheet("font-size: 18px; color: #94A3B8;")
        score_vbox.addWidget(score_label_title)
        score_vbox.addWidget(self.lbl_user_score_value)
        score_vbox.addWidget(score_pts_lbl)

        top_row.addLayout(score_vbox)
        top_row.addStretch()

        rank_vbox = QVBoxLayout()
        rank_vbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rank_lbl_title = QLabel("🎖️ رانكك الحالي")
        rank_lbl_title.setStyleSheet("font-size: 14px; color: #94A3B8; text-align: right;")
        rank_lbl_title.setAlignment(Qt.AlignRight)
        self.lbl_level_badge = QLabel("مبتدئ أول 🥉")
        self.lbl_level_badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(148,163,184,0.25), stop:1 rgba(148,163,184,0.1));
            color: #94A3B8;
            border: 1px solid #94A3B8;
            font-size: 20px;
            font-weight: bold;
            border-radius: 14px;
            padding: 12px 22px;
        """)
        self.lbl_level_badge.setAlignment(Qt.AlignCenter)
        self.lbl_rank_desc = QLabel("بداية الرحلة والالتزام 🌱")
        self.lbl_rank_desc.setStyleSheet("font-size: 13px; color: #64748B; text-align: right;")
        self.lbl_rank_desc.setAlignment(Qt.AlignRight)
        rank_vbox.addWidget(rank_lbl_title)
        rank_vbox.addWidget(self.lbl_level_badge)
        rank_vbox.addWidget(self.lbl_rank_desc)
        top_row.addLayout(rank_vbox)

        rc_layout.addLayout(top_row)

        # Progress to next rank
        prog_row = QHBoxLayout()
        prog_row.setSpacing(10)
        self.lbl_rank_progress_text = QLabel("التقدم نحو الرانك التالي:")
        self.lbl_rank_progress_text.setStyleSheet("font-size: 13px; color: #94A3B8;")
        self.lbl_rank_next_pts = QLabel("")
        self.lbl_rank_next_pts.setStyleSheet("font-size: 13px; color: #38BDF8; font-weight: bold;")
        prog_row.addWidget(self.lbl_rank_progress_text)
        prog_row.addStretch()
        prog_row.addWidget(self.lbl_rank_next_pts)
        rc_layout.addLayout(prog_row)

        self.rank_progress_bar = QProgressBar()
        self.rank_progress_bar.setRange(0, 100)
        self.rank_progress_bar.setValue(0)
        self.rank_progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0B0F19;
                border: 1px solid #1F293D;
                border-radius: 10px;
                height: 18px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F59E0B, stop:1 #EF4444);
                border-radius: 9px;
            }
        """)
        rc_layout.addWidget(self.rank_progress_bar)

        layout.addWidget(rank_card)

        # ── Rank Progression Road Map ────────────────────────────────────────
        road_card = QFrame()
        road_card.setObjectName("Card")
        road_layout = QVBoxLayout(road_card)
        road_layout.setContentsMargins(22, 18, 22, 18)
        road_layout.setSpacing(10)

        road_title = QLabel("🗺️ خريطة الرانكات والمستويات")
        road_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        road_layout.addWidget(road_title)

        road_subtitle = QLabel("مسيرة الإنجاز من المبتدئ إلى القدوة الأسطورية:")
        road_subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        road_layout.addWidget(road_subtitle)

        # Grid of ranks (3 per row)
        self.ranks_grid_layout = QGridLayout()
        self.ranks_grid_layout.setSpacing(8)
        road_layout.addLayout(self.ranks_grid_layout)

        layout.addWidget(road_card)

        # ── Weekly Progress Card ─────────────────────────────────────────────
        weekly_card = QFrame()
        weekly_card.setObjectName("Card")
        wk_layout = QVBoxLayout(weekly_card)
        wk_layout.setSpacing(14)

        wk_header = QHBoxLayout()
        wk_title = QLabel("📊 الإنجاز الأسبوعي (آخر 7 أيام)")
        wk_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        wk_header.addWidget(wk_title)
        wk_header.addStretch()
        self.lbl_best_day = QLabel("")
        self.lbl_best_day.setStyleSheet("font-size: 13px; color: #10B981; font-weight: bold;")
        wk_header.addWidget(self.lbl_best_day)
        wk_layout.addLayout(wk_header)

        # Weekly Bars Container
        bars_container = QWidget()
        bars_container.setStyleSheet("background: transparent;")
        self.weekly_bars_layout = QHBoxLayout(bars_container)
        self.weekly_bars_layout.setSpacing(10)
        self.weekly_bars_layout.setContentsMargins(0, 0, 0, 0)
        wk_layout.addWidget(bars_container)

        layout.addWidget(weekly_card)

        # ── Badges Gallery ───────────────────────────────────────────────────
        badges_outer = QFrame()
        badges_outer.setObjectName("Card")
        badges_outer_layout = QVBoxLayout(badges_outer)
        badges_outer_layout.setContentsMargins(22, 18, 22, 18)
        badges_outer_layout.setSpacing(16)

        bg_header = QHBoxLayout()
        bg_title = QLabel("🎖️ معرض الأوسمة والتحديات")
        bg_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F8FAFC;")
        bg_header.addWidget(bg_title)
        bg_header.addStretch()
        self.lbl_badges_count = QLabel("")
        self.lbl_badges_count.setStyleSheet("font-size: 14px; color: #10B981; font-weight: bold;")
        bg_header.addWidget(self.lbl_badges_count)
        badges_outer_layout.addLayout(bg_header)

        # Badge filter buttons
        badge_filter_row = QHBoxLayout()
        badge_filter_row.setSpacing(8)
        self.btn_badge_filter_all = QPushButton("الكل")
        self.btn_badge_filter_water = QPushButton("💧 الماء")
        self.btn_badge_filter_pushups = QPushButton("🏋️ التمارين")
        self.btn_badge_filter_learn = QPushButton("🎓 التعلم")
        self.btn_badge_filter_tasks = QPushButton("📋 المهام")
        self.btn_badge_filter_score = QPushButton("⚡ النقاط")

        badge_filters = [
            (self.btn_badge_filter_all, "all"),
            (self.btn_badge_filter_water, "water"),
            (self.btn_badge_filter_pushups, "pushups"),
            (self.btn_badge_filter_learn, "learn"),
            (self.btn_badge_filter_tasks, "tasks"),
            (self.btn_badge_filter_score, "score"),
        ]
        for b, f_val in badge_filters:
            b.setObjectName("FilterBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda ch, v=f_val: self.set_badge_filter(v))
            badge_filter_row.addWidget(b)
        badge_filter_row.addStretch()
        badges_outer_layout.addLayout(badge_filter_row)

        # Badges Grid (scrollable, 4 per row)
        self.badges_scroll_grid = QGridLayout()
        self.badges_scroll_grid.setSpacing(12)
        badges_outer_layout.addLayout(self.badges_scroll_grid)

        layout.addWidget(badges_outer)
        layout.addStretch()

        self.reload_analytics_ui()
        return page

    # Page 2: Schedules (SUPER EASY 1-CLICK PRESETS + EASY DROPDOWN PICKER)
    def create_schedules_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)

        title = QLabel("📅 جدول مواعيد التعلم التلقائي")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # ⚡ 1-CLICK INSTANT PRESETS CARD
        preset_card = QFrame()
        preset_card.setObjectName("Card")
        preset_layout = QVBoxLayout(preset_card)
        preset_layout.setSpacing(12)

        preset_title = QLabel("⚡ إضافة سريعة بنقرة واحدة (من الآن):")
        preset_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #38BDF8;")
        preset_layout.addWidget(preset_title)

        preset_btns_box = QHBoxLayout()
        preset_btns_box.setSpacing(12)

        btn_p30 = QPushButton("⚡ 30 دقيقة الآن")
        btn_p30.setObjectName("PresetBtn")
        btn_p30.setCursor(Qt.PointingHandCursor)
        btn_p30.clicked.connect(lambda: self.add_quick_preset(30, "جلسة سريعة (30 دقيقة)"))

        btn_p45 = QPushButton("⏱️ 45 دقيقة الآن")
        btn_p45.setObjectName("PresetBtn")
        btn_p45.setCursor(Qt.PointingHandCursor)
        btn_p45.clicked.connect(lambda: self.add_quick_preset(45, "جلسة تركيز (45 دقيقة)"))

        btn_p60 = QPushButton("🎓 ساعة كاملة الآن")
        btn_p60.setObjectName("PresetBtn")
        btn_p60.setCursor(Qt.PointingHandCursor)
        btn_p60.clicked.connect(lambda: self.add_quick_preset(60, "جلسة تعلم (ساعة)"))

        btn_p120 = QPushButton("🚀 ساعتان الآن")
        btn_p120.setObjectName("PresetBtn")
        btn_p120.setCursor(Qt.PointingHandCursor)
        btn_p120.clicked.connect(lambda: self.add_quick_preset(120, "جلسة مكثفة (ساعتان)"))

        preset_btns_box.addWidget(btn_p30)
        preset_btns_box.addWidget(btn_p45)
        preset_btns_box.addWidget(btn_p60)
        preset_btns_box.addWidget(btn_p120)

        preset_layout.addLayout(preset_btns_box)
        layout.addWidget(preset_card)

        # Schedules List
        self.list_schedules = QListWidget()
        self.list_schedules.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.reload_schedules_list()
        layout.addWidget(self.list_schedules)

        # EASY CUSTOM TIME PICKER CARD
        add_box = QFrame()
        add_box.setObjectName("Card")
        add_vbox = QVBoxLayout(add_box)
        add_vbox.setSpacing(10)

        custom_lbl = QLabel("🕒 تحديد موعد خاص بسهولة:")
        custom_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        add_vbox.addWidget(custom_lbl)

        row_inputs = QHBoxLayout()
        row_inputs.setSpacing(10)

        self.txt_sched_name = QLineEdit()
        self.txt_sched_name.setPlaceholderText("اسم الجلسة (اختياري)")

        # Start Time Easy Dropdowns
        self.cmb_start_hour = QComboBox()
        for h in range(1, 13):
            self.cmb_start_hour.addItem(f"{h:02d}")
        self.cmb_start_hour.setCurrentText("04")

        self.cmb_start_min = QComboBox()
        for m in [0, 15, 30, 45]:
            self.cmb_start_min.addItem(f"{m:02d}")

        self.cmb_start_period = QComboBox()
        self.cmb_start_period.addItems(["مساءً", "صباحاً"])

        # End Time Easy Dropdowns
        self.cmb_end_hour = QComboBox()
        for h in range(1, 13):
            self.cmb_end_hour.addItem(f"{h:02d}")
        self.cmb_end_hour.setCurrentText("06")

        self.cmb_end_min = QComboBox()
        for m in [0, 15, 30, 45]:
            self.cmb_end_min.addItem(f"{m:02d}")

        self.cmb_end_period = QComboBox()
        self.cmb_end_period.addItems(["مساءً", "صباحاً"])

        btn_add_sched = QPushButton("➕ إضافة موعد")
        btn_add_sched.setObjectName("PrimaryBtn")
        btn_add_sched.setCursor(Qt.PointingHandCursor)
        btn_add_sched.clicked.connect(self.add_schedule_custom)

        row_inputs.addWidget(self.txt_sched_name, 2)
        row_inputs.addWidget(QLabel("من:"))
        row_inputs.addWidget(self.cmb_start_hour)
        row_inputs.addWidget(QLabel(":"))
        row_inputs.addWidget(self.cmb_start_min)
        row_inputs.addWidget(self.cmb_start_period)
        
        row_inputs.addWidget(QLabel(" إلى:"))
        row_inputs.addWidget(self.cmb_end_hour)
        row_inputs.addWidget(QLabel(":"))
        row_inputs.addWidget(self.cmb_end_min)
        row_inputs.addWidget(self.cmb_end_period)

        row_inputs.addWidget(btn_add_sched, 1)

        add_vbox.addLayout(row_inputs)
        layout.addWidget(add_box)

        return page

    # Page 3: Blocked Apps
    def create_blocked_apps_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("🚫 البرامج والتطبيقات الممنوعة")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("أثناء جلسة التعلم النشطة، سيمنع التطبيق البرامج المحددة للقضاء على التشتت.")
        desc.setStyleSheet("color: #94A3B8; font-size: 15px;")
        layout.addWidget(desc)

        # 🔍 Search Box for Blocked Apps
        self.txt_search_blocked_apps = QLineEdit()
        self.txt_search_blocked_apps.setPlaceholderText("🔍 ابحث في قائمة التطبيقات الممنوعة...")
        self.txt_search_blocked_apps.textChanged.connect(self.reload_blocked_apps_list)
        layout.addWidget(self.txt_search_blocked_apps)

        self.list_blocked_apps = QListWidget()
        self.list_blocked_apps.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.reload_blocked_apps_list()
        layout.addWidget(self.list_blocked_apps)

        ctrl_box = QHBoxLayout()

        self.txt_app_name = QLineEdit()
        self.txt_app_name.setPlaceholderText("اسم التطبيق التنفيذي (مثل discord.exe)")

        btn_add_app = QPushButton("➕ إضافة يدوي")
        btn_add_app.setObjectName("PrimaryBtn")
        btn_add_app.setCursor(Qt.PointingHandCursor)
        btn_add_app.clicked.connect(self.add_blocked_app)

        btn_pick_app = QPushButton("🔍 اختيار من التطبيقات المفتوحة")
        btn_pick_app.setObjectName("PrimaryBtn")
        btn_pick_app.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10B981); border: 1px solid #10B981;")
        btn_pick_app.setCursor(Qt.PointingHandCursor)
        btn_pick_app.clicked.connect(self.open_running_apps_dialog)

        ctrl_box.addWidget(self.txt_app_name, 1)
        ctrl_box.addWidget(btn_add_app)
        ctrl_box.addWidget(btn_pick_app)

        layout.addLayout(ctrl_box)
        return page

    # Page 6: Blocked Websites Page
    def create_blocked_websites_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("🌐 المواقع المحظورة أثناء التعلم")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("أثناء تفعيل وقت التعلم والتركيز، سيتم حظر الوصول لهذه المواقع لمنع التشتت زيادة الإنتاجية.")
        desc.setStyleSheet("color: #94A3B8; font-size: 15px;")
        layout.addWidget(desc)

        # Quick Preset Buttons Row
        preset_card = QFrame()
        preset_card.setObjectName("Card")
        preset_layout = QVBoxLayout(preset_card)
        preset_layout.setSpacing(10)

        preset_lbl = QLabel("⚡ أزرار حظر سريعة بنقرة واحدة:")
        preset_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        preset_layout.addWidget(preset_lbl)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(10)

        presets = [
            ("🎥 يوتيوب", "youtube.com"),
            ("📘 فيسبوك", "facebook.com"),
            ("🐦 تويتر/X", "twitter.com"),
            ("🎵 تيك توك", "tiktok.com"),
            ("📷 انستغرام", "instagram.com"),
            ("🤖 ريديت", "reddit.com"),
            ("🎬 نتفليكس", "netflix.com")
        ]

        for p_name, domain in presets:
            btn = QPushButton(p_name)
            btn.setObjectName("PresetBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda ch, d=domain: self.add_preset_website(d))
            preset_row.addWidget(btn)

        preset_layout.addLayout(preset_row)
        layout.addWidget(preset_card)

        # Search Box for Blocked Websites
        self.txt_search_blocked_websites = QLineEdit()
        self.txt_search_blocked_websites.setPlaceholderText("🔍 ابحث في قائمة المواقع المحظورة...")
        self.txt_search_blocked_websites.textChanged.connect(self.reload_blocked_websites_list)
        layout.addWidget(self.txt_search_blocked_websites)

        self.list_blocked_websites = QListWidget()
        self.reload_blocked_websites_list()
        layout.addWidget(self.list_blocked_websites)

        ctrl_box = QHBoxLayout()
        self.txt_website_url = QLineEdit()
        self.txt_website_url.setPlaceholderText("رابط الموقع (مثال: youtube.com أو twitch.tv)")

        btn_add_web = QPushButton("➕ إضافة موقع")
        btn_add_web.setObjectName("PrimaryBtn")
        btn_add_web.setCursor(Qt.PointingHandCursor)
        btn_add_web.clicked.connect(self.add_blocked_website)

        ctrl_box.addWidget(self.txt_website_url, 1)
        ctrl_box.addWidget(btn_add_web)

        layout.addLayout(ctrl_box)
        return page

    # Page 7: Settings & Instant Testing
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("⚙️ الإعدادات وتجربة التنبيهات")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        opts_card = QFrame()
        opts_card.setObjectName("Card")
        opts_layout = QVBoxLayout(opts_card)
        opts_layout.setSpacing(15)

        self.chk_startup = QCheckBox("التشغيل التلقائي مع إقلاع الجهاز (Windows Startup)")
        self.chk_startup.setChecked(self.cfg_mgr.is_startup_enabled())
        self.chk_startup.toggled.connect(self.toggle_startup)

        self.chk_sound = QCheckBox("تفعيل الأصوات والتنبيهات الصوتية المتكررة")
        self.chk_sound.setChecked(self.config.get("sound_enabled", True))
        self.chk_sound.toggled.connect(self.toggle_sound)

        opts_layout.addWidget(self.chk_startup)
        opts_layout.addWidget(self.chk_sound)

        layout.addWidget(opts_card)

        # Custom Interval Settings Card
        interval_card = QFrame()
        interval_card.setObjectName("Card")
        interval_layout = QVBoxLayout(interval_card)
        interval_layout.setSpacing(14)

        interval_title = QLabel("⏱️ تحديد مواعيد وتكرار التذكيرات الصحية")
        interval_title.setObjectName("CardTitle")
        interval_layout.addWidget(interval_title)

        interval_row = QHBoxLayout()
        interval_row.setSpacing(20)

        # Water Interval
        water_box = QVBoxLayout()
        water_box.addWidget(QLabel("💧 تذكير شرب الماء:"))
        self.cmb_water_interval = QComboBox()
        for m in [15, 20, 30, 40, 50, 60, 90]:
            self.cmb_water_interval.addItem(f"كل {m} دقيقة", m)

        curr_w = self.config.get("water_interval_min", 40)
        idx_w = self.cmb_water_interval.findData(curr_w)
        if idx_w != -1:
            self.cmb_water_interval.setCurrentIndex(idx_w)
        self.cmb_water_interval.currentIndexChanged.connect(self.change_water_interval)
        water_box.addWidget(self.cmb_water_interval)

        # Pushups Interval
        pushups_box = QVBoxLayout()
        pushups_box.addWidget(QLabel("🏋️ تذكير تمارين الضغط والرياضة:"))
        self.cmb_pushups_interval = QComboBox()
        for m in [30, 45, 60, 90, 120, 180]:
            self.cmb_pushups_interval.addItem(f"كل {m} دقيقة", m)

        curr_p = self.config.get("pushups_interval_min", 120)
        idx_p = self.cmb_pushups_interval.findData(curr_p)
        if idx_p != -1:
            self.cmb_pushups_interval.setCurrentIndex(idx_p)
        self.cmb_pushups_interval.currentIndexChanged.connect(self.change_pushups_interval)
        pushups_box.addWidget(self.cmb_pushups_interval)

        interval_row.addLayout(water_box)
        interval_row.addLayout(pushups_box)
        interval_layout.addLayout(interval_row)

        layout.addWidget(interval_card)

        # Test Center
        test_card = QFrame()
        test_card.setObjectName("Card")
        test_layout = QVBoxLayout(test_card)
        test_layout.setSpacing(15)

        test_title = QLabel("🎯 تجربة شاشات التنبيه فوراً")
        test_title.setObjectName("CardTitle")

        test_desc = QLabel("يمكنك اختبار شكل شاشة شرب الماء وشاشة التمارين المتنوعة فوراً.")
        test_desc.setStyleSheet("color: #94A3B8; font-size: 15px;")

        btn_box = QHBoxLayout()
        btn_box.setSpacing(15)

        btn_test_water = QPushButton("💧 تجربة شاشة شرب الماء الان")
        btn_test_water.setObjectName("PrimaryBtn")
        btn_test_water.setCursor(Qt.PointingHandCursor)
        btn_test_water.clicked.connect(self.test_water_overlay)

        btn_test_pushups = QPushButton("🏋️ تجربة تمرين رياضه الان (متنوع)")
        btn_test_pushups.setObjectName("PrimaryBtn")
        btn_test_pushups.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EA580C, stop:1 #C2410C); border: 1px solid #F97316;")
        btn_test_pushups.setCursor(Qt.PointingHandCursor)
        btn_test_pushups.clicked.connect(self.test_pushups_overlay)

        btn_box.addWidget(btn_test_water)
        btn_box.addWidget(btn_test_pushups)

        test_layout.addWidget(test_title)
        test_layout.addWidget(test_desc)
        test_layout.addLayout(btn_box)

        layout.addWidget(test_card)

        # Reset Progress Section
        reset_card = QFrame()
        reset_card.setObjectName("Card")
        reset_card.setStyleSheet("background-color: #111827; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 20px; padding: 22px;")
        reset_layout = QVBoxLayout(reset_card)
        reset_layout.setSpacing(12)

        reset_title = QLabel("🔄 إعادة تعيين النقاط والتقدم")
        reset_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #EF4444;")
        
        reset_desc = QLabel("تصفير كافة النقاط، الأوسمة، وإحصائيات التقدم والبدء من جديد من رانك 'مبتدئ أول'.")
        reset_desc.setStyleSheet("color: #94A3B8; font-size: 14px;")

        btn_reset_progress = QPushButton("🔄 إعادة تعيين التقدم والنقاط من البداية")
        btn_reset_progress.setObjectName("FinishBtn")
        btn_reset_progress.setCursor(Qt.PointingHandCursor)
        btn_reset_progress.clicked.connect(self.reset_user_progress)

        reset_layout.addWidget(reset_title)
        reset_layout.addWidget(reset_desc)
        reset_layout.addWidget(btn_reset_progress)

        layout.addWidget(reset_card)
        layout.addStretch()
        return page

    # Reload Schedules List
    def reload_schedules_list(self):
        self.list_schedules.clear()
        trash_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(22, 22))
        if trash_pix.isNull():
            trash_pix = get_tinted_pixmap("pauselogo.png", "#EF4444", QSize(22, 22))

        for idx, item in enumerate(self.config.get("learning_schedules", [])):
            list_item = QListWidgetItem(self.list_schedules)
            
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 12, 15, 12)
            row_layout.setSpacing(15)

            start_12 = format_12h(item['start'])
            end_12 = format_12h(item['end'])

            lbl_name = QLabel(item['name'])
            lbl_name.setStyleSheet("font-size: 17px; font-weight: bold; color: #F8FAFC;")
            lbl_name.setWordWrap(True)
            lbl_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            lbl_time = QLabel(f"من {start_12} إلى {end_12}")
            lbl_time.setStyleSheet("font-size: 14px; color: #38BDF8; font-weight: bold;")

            text_vbox = QVBoxLayout()
            text_vbox.setSpacing(4)
            text_vbox.addWidget(lbl_name)
            text_vbox.addWidget(lbl_time)

            btn_del = QPushButton()
            btn_del.setObjectName("IconTrashBtn")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setFixedSize(40, 40)
            if not trash_pix.isNull():
                btn_del.setIcon(QIcon(trash_pix))
                btn_del.setIconSize(QSize(22, 22))
            btn_del.setToolTip("حذف هذا الموعد")
            btn_del.clicked.connect(lambda ch, i=idx: self.delete_schedule(i))

            row_layout.addLayout(text_vbox, 1)
            row_layout.addWidget(btn_del, 0, Qt.AlignRight | Qt.AlignVCenter)

            row_widget.setLayout(row_layout)
            
            hint = row_widget.sizeHint()
            hint.setHeight(max(hint.height(), 68))
            list_item.setSizeHint(hint)

            self.list_schedules.addItem(list_item)
            self.list_schedules.setItemWidget(list_item, row_widget)

    # 1-CLICK INSTANT PRESET ADDER
    def add_quick_preset(self, duration_minutes, preset_name):
        now = QTime.currentTime()
        start_str = now.toString("hh:mm")
        end_time = now.addSecs(duration_minutes * 60)
        end_str = end_time.toString("hh:mm")

        self.config["learning_schedules"].append({
            "name": preset_name, "start": start_str, "end": end_str, "active": True
        })
        self.cfg_mgr.save_config()
        self.reload_schedules_list()

        # Start manual session right away
        self.start_manual_session()

    # EASY DROPDOWN CUSTOM TIME ADDER
    def add_schedule_custom(self):
        name = self.txt_sched_name.text().strip() or "جلسة تعلم خاصة"
        
        # Convert Start Time Dropdowns to 24h string
        h_start = int(self.cmb_start_hour.currentText())
        m_start = int(self.cmb_start_min.currentText())
        if self.cmb_start_period.currentText() == "مساءً" and h_start < 12:
            h_start += 12
        elif self.cmb_start_period.currentText() == "صباحاً" and h_start == 12:
            h_start = 0

        # Convert End Time Dropdowns to 24h string
        h_end = int(self.cmb_end_hour.currentText())
        m_end = int(self.cmb_end_min.currentText())
        if self.cmb_end_period.currentText() == "مساءً" and h_end < 12:
            h_end += 12
        elif self.cmb_end_period.currentText() == "صباحاً" and h_end == 12:
            h_end = 0

        start_str = f"{h_start:02d}:{m_start:02d}"
        end_str = f"{h_end:02d}:{m_end:02d}"

        self.config["learning_schedules"].append({
            "name": name, "start": start_str, "end": end_str, "active": True
        })
        self.cfg_mgr.save_config()
        self.reload_schedules_list()
        self.txt_sched_name.clear()

    def delete_schedule(self, index):
        if 0 <= index < len(self.config["learning_schedules"]):
            self.config["learning_schedules"].pop(index)
            self.cfg_mgr.save_config()
            self.reload_schedules_list()

    # Reload Blocked Apps List
    def reload_blocked_apps_list(self):
        self.list_blocked_apps.clear()

        query = ""
        if hasattr(self, "txt_search_blocked_apps"):
            query = self.txt_search_blocked_apps.text().strip().lower()

        all_apps = self.config.get("blocked_apps", [])
        filtered = [app for app in all_apps if query in app.lower()]

        if not filtered:
            item = QListWidgetItem(self.list_blocked_apps)
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            msg = f"🔍 لا توجد نتائج لـ '{query}'" if query else "🚫 لا توجد تطبيقات ممنوعة في القائمة حالياً"
            lbl = QLabel(msg)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 15px; color: #94A3B8; padding: 15px;")
            row_layout.addWidget(lbl)
            row_widget.setLayout(row_layout)
            item.setSizeHint(QSize(0, 60))
            self.list_blocked_apps.addItem(item)
            self.list_blocked_apps.setItemWidget(item, row_widget)
            return
        
        forb_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(24, 24))
        trash_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(22, 22))

        for app in filtered:
            orig_idx = all_apps.index(app)
            list_item = QListWidgetItem(self.list_blocked_apps)
            
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 12, 15, 12)
            row_layout.setSpacing(15)

            if not forb_pix.isNull():
                ic_lbl = QLabel()
                ic_lbl.setPixmap(forb_pix)
                row_layout.addWidget(ic_lbl, 0, Qt.AlignVCenter)

            lbl = QLabel(app)
            lbl.setStyleSheet("font-size: 17px; font-weight: bold; color: #F8FAFC;")
            lbl.setWordWrap(True)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            btn_del = QPushButton()
            btn_del.setObjectName("IconTrashBtn")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setFixedSize(40, 40)
            if not trash_pix.isNull():
                btn_del.setIcon(QIcon(trash_pix))
                btn_del.setIconSize(QSize(22, 22))
            btn_del.setToolTip("حذف التطبيق الممنوع")
            btn_del.clicked.connect(lambda ch, i=orig_idx: self.delete_blocked_app(i))

            row_layout.addWidget(lbl, 1)
            row_layout.addWidget(btn_del, 0, Qt.AlignRight | Qt.AlignVCenter)

            row_widget.setLayout(row_layout)
            
            hint = row_widget.sizeHint()
            hint.setHeight(max(hint.height(), 60))
            list_item.setSizeHint(hint)

            self.list_blocked_apps.addItem(list_item)
            self.list_blocked_apps.setItemWidget(list_item, row_widget)

    def add_blocked_app(self):
        app = self.txt_app_name.text().strip().lower()
        if not app:
            return
        if not app.endswith(".exe"):
            app += ".exe"
        if app not in self.config["blocked_apps"]:
            self.config["blocked_apps"].append(app)
            self.cfg_mgr.save_config()
            self.app_blocker.set_blocked_apps(self.config["blocked_apps"])
            self.reload_blocked_apps_list()
        self.txt_app_name.clear()

    def delete_blocked_app(self, index):
        if 0 <= index < len(self.config["blocked_apps"]):
            self.config["blocked_apps"].pop(index)
            self.cfg_mgr.save_config()
            self.app_blocker.set_blocked_apps(self.config["blocked_apps"])
            self.reload_blocked_apps_list()

    # ─── Blocked Websites Actions ────────────────────────────────────────────
    def reload_blocked_websites_list(self):
        if not hasattr(self, 'list_blocked_websites'):
            return
        self.list_blocked_websites.clear()

        query = ""
        if hasattr(self, "txt_search_blocked_websites"):
            query = self.txt_search_blocked_websites.text().strip().lower()

        all_sites = self.config.get("blocked_websites", [])
        filtered = [s for s in all_sites if query in s.lower()]

        if not filtered:
            item = QListWidgetItem(self.list_blocked_websites)
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            msg = f"🔍 لا توجد نتائج لـ '{query}'" if query else "🌐 لا توجد مواقع محظورة في القائمة حالياً"
            lbl = QLabel(msg)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 15px; color: #94A3B8; padding: 15px;")
            row_layout.addWidget(lbl)
            row_widget.setLayout(row_layout)
            item.setSizeHint(QSize(0, 60))
            self.list_blocked_websites.addItem(item)
            self.list_blocked_websites.setItemWidget(item, row_widget)
            return

        trash_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(22, 22))

        for site in filtered:
            orig_idx = all_sites.index(site)
            list_item = QListWidgetItem(self.list_blocked_websites)

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(15, 12, 15, 12)
            row_layout.setSpacing(15)

            lbl_ic = QLabel("🌐")
            lbl_ic.setStyleSheet("font-size: 22px;")
            row_layout.addWidget(lbl_ic)

            lbl = QLabel(site)
            lbl.setStyleSheet("font-size: 17px; font-weight: bold; color: #F8FAFC;")
            lbl.setWordWrap(True)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            lbl_badge = QLabel("محظور أثناء التعلم 🛑")
            lbl_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 12px; font-weight: bold; border-radius: 8px; padding: 5px 10px;")

            btn_del = QPushButton()
            btn_del.setObjectName("IconTrashBtn")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setFixedSize(40, 40)
            if not trash_pix.isNull():
                btn_del.setIcon(QIcon(trash_pix))
                btn_del.setIconSize(QSize(22, 22))
            btn_del.setToolTip("حذف الموقع المحظور")
            btn_del.clicked.connect(lambda ch, i=orig_idx: self.delete_blocked_website(i))

            row_layout.addWidget(lbl, 1)
            row_layout.addWidget(lbl_badge, 0, Qt.AlignRight | Qt.AlignVCenter)
            row_layout.addWidget(btn_del, 0, Qt.AlignRight | Qt.AlignVCenter)

            row_widget.setLayout(row_layout)
            hint = row_widget.sizeHint()
            hint.setHeight(max(hint.height(), 60))
            list_item.setSizeHint(hint)

            self.list_blocked_websites.addItem(list_item)
            self.list_blocked_websites.setItemWidget(list_item, row_widget)

    def add_blocked_website(self):
        raw = self.txt_website_url.text().strip().lower()
        if not raw:
            return
        if raw.startswith("http://"): raw = raw[7:]
        if raw.startswith("https://"): raw = raw[8:]
        if raw.startswith("www."): raw = raw[4:]
        site = raw.split('/')[0]
        if site and site not in self.config.get("blocked_websites", []):
            if "blocked_websites" not in self.config:
                self.config["blocked_websites"] = []
            self.config["blocked_websites"].append(site)
            self.cfg_mgr.save_config()
            self.app_blocker.set_blocked_websites(self.config["blocked_websites"])
            self.reload_blocked_websites_list()
        self.txt_website_url.clear()

    def add_preset_website(self, domain):
        if "blocked_websites" not in self.config:
            self.config["blocked_websites"] = []
        if domain not in self.config["blocked_websites"]:
            self.config["blocked_websites"].append(domain)
            self.cfg_mgr.save_config()
            self.app_blocker.set_blocked_websites(self.config["blocked_websites"])
            self.reload_blocked_websites_list()

    def delete_blocked_website(self, index):
        if "blocked_websites" in self.config and 0 <= index < len(self.config["blocked_websites"]):
            self.config["blocked_websites"].pop(index)
            self.cfg_mgr.save_config()
            self.app_blocker.set_blocked_websites(self.config["blocked_websites"])
            self.reload_blocked_websites_list()

    def open_running_apps_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("اختر تطبيقاً حياً لحظره")
        dialog.resize(480, 560)
        dialog.setStyleSheet("background-color: #090D16; color: white;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setSpacing(12)
        d_layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("اختر من التطبيقات المفتوحة حالياً في جهازك:")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        d_layout.addWidget(lbl)

        # 🔍 Search Box inside Dialog
        txt_dlg_search = QLineEdit()
        txt_dlg_search.setPlaceholderText("🔍 ابحث في التطبيقات المفتوحة حالياً...")
        d_layout.addWidget(txt_dlg_search)

        running_list = QListWidget()
        running_apps = AppBlocker.get_running_apps()

        def filter_dlg_apps():
            running_list.clear()
            query = txt_dlg_search.text().strip().lower()
            filtered = [a for a in running_apps if query in a.lower()]
            if not filtered:
                running_list.addItem("🔍 لا توجد تطبيقات حية مطابقة للبحث")
            else:
                for app in filtered:
                    running_list.addItem(app)

        txt_dlg_search.textChanged.connect(filter_dlg_apps)
        filter_dlg_apps()

        d_layout.addWidget(running_list)

        btn_confirm = QPushButton("إضافة للتطبيقات الممنوعة ➕")
        btn_confirm.setObjectName("PrimaryBtn")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.setStyleSheet("background-color: #0284C7; color: white; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 10px;")

        def confirm_selection():
            selected = running_list.currentItem()
            if selected:
                app_name = selected.text()
                if app_name in running_apps and app_name not in self.config["blocked_apps"]:
                    self.config["blocked_apps"].append(app_name)
                    self.cfg_mgr.save_config()
                    self.app_blocker.set_blocked_apps(self.config["blocked_apps"])
                    self.reload_blocked_apps_list()
                dialog.accept()

        btn_confirm.clicked.connect(confirm_selection)
        d_layout.addWidget(btn_confirm)
        dialog.exec()

    # ─── To-Do Tasks Actions ────────────────────────────────────────────────
    def add_task(self):
        text = self.txt_task_input.text().strip()
        if not text:
            return

        if "daily_tasks" not in self.config:
            self.config["daily_tasks"] = []

        self.config["daily_tasks"].append({
            "text": text,
            "completed": False
        })
        self.cfg_mgr.save_config()
        self.txt_task_input.clear()
        self.reload_tasks_list()

    def add_task_from_page(self):
        text = self.txt_task_page_input.text().strip()
        if not text:
            return

        if "daily_tasks" not in self.config:
            self.config["daily_tasks"] = []

        self.config["daily_tasks"].append({
            "text": text,
            "completed": False
        })
        self.cfg_mgr.save_config()
        self.txt_task_page_input.clear()
        self.reload_tasks_list()

    def toggle_task(self, index, is_checked):
        if 0 <= index < len(self.config.get("daily_tasks", [])):
            was_completed = self.config["daily_tasks"][index].get("completed", False)
            self.config["daily_tasks"][index]["completed"] = is_checked
            if is_checked and not was_completed:
                self.award_points(15, "إكمال مهمة يومية")
            self.cfg_mgr.save_config()
            self.reload_tasks_list()

    def delete_task(self, index):
        if 0 <= index < len(self.config.get("daily_tasks", [])):
            self.config["daily_tasks"].pop(index)
            self.cfg_mgr.save_config()
            self.reload_tasks_list()

    def set_task_filter(self, filter_val):
        self.current_task_filter = filter_val
        self.reload_tasks_list()

    def reload_tasks_list(self):
        all_tasks = self.config.get("daily_tasks", [])
        total = len(all_tasks)
        completed_count = sum(1 for t in all_tasks if t.get("completed", False))
        pending_count = total - completed_count
        percent = int((completed_count / total) * 100) if total > 0 else 0

        # Update stats labels on Tasks Page
        if hasattr(self, 'lbl_task_stat_total'):
            self.lbl_task_stat_total.setText(f"{total} مهام")
            self.lbl_task_stat_pending.setText(f"{pending_count} مهام")
            self.lbl_task_stat_done.setText(f"{completed_count} مهام")

        if hasattr(self, 'task_page_progress_bar'):
            self.task_page_progress_bar.setValue(percent)
            self.lbl_task_page_percent.setText(f"{percent}%")

        if hasattr(self, 'task_progress_bar'):
            self.task_progress_bar.setValue(percent)
            self.lbl_task_progress.setText(f"إنجاز المهام: {percent}% ({completed_count} من {total})")

        # Update filter buttons active styling
        for b_name in ['btn_filter_all', 'btn_filter_page_all']:
            if hasattr(self, b_name):
                getattr(self, b_name).setProperty("active", "true" if self.current_task_filter == "all" else "false")
                getattr(self, b_name).setStyle(getattr(self, b_name).style())

        for b_name in ['btn_filter_active', 'btn_filter_page_active']:
            if hasattr(self, b_name):
                getattr(self, b_name).setProperty("active", "true" if self.current_task_filter == "active" else "false")
                getattr(self, b_name).setStyle(getattr(self, b_name).style())

        for b_name in ['btn_filter_completed', 'btn_filter_page_completed']:
            if hasattr(self, b_name):
                getattr(self, b_name).setProperty("active", "true" if self.current_task_filter == "completed" else "false")
                getattr(self, b_name).setStyle(getattr(self, b_name).style())

        # Filter tasks
        filtered_tasks = []
        for idx, t in enumerate(all_tasks):
            is_comp = t.get("completed", False)
            if self.current_task_filter == "all":
                filtered_tasks.append((idx, t))
            elif self.current_task_filter == "active" and not is_comp:
                filtered_tasks.append((idx, t))
            elif self.current_task_filter == "completed" and is_comp:
                filtered_tasks.append((idx, t))

        # Helper to populate any target QListWidget
        def populate_widget(target_list_widget, is_spacious=False):
            if not target_list_widget:
                return
            target_list_widget.clear()

            if not filtered_tasks:
                item = QListWidgetItem(target_list_widget)
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                
                if total == 0:
                    msg = "✨ لا توجد مهام بعد — أضف أول مهمة لبدء يومك بإنتاجية!"
                elif self.current_task_filter == "active":
                    msg = "🎉 رائع جداً! لا توجد مهام معلقة (جميع المهام مكتملة)."
                elif self.current_task_filter == "completed":
                    msg = "📌 لم تكتمل أي مهمة بعد — ابدأ بإكمال أول مهمة اليوم!"
                else:
                    msg = "لا توجد مهام مطابقة."

                lbl = QLabel(msg)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("font-size: 15px; color: #94A3B8; padding: 18px;")
                row_layout.addWidget(lbl)
                row_widget.setLayout(row_layout)
                item.setSizeHint(QSize(0, 60 if is_spacious else 55))
                target_list_widget.addItem(item)
                target_list_widget.setItemWidget(item, row_widget)
                return

            trash_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(22 if is_spacious else 20, 22 if is_spacious else 20))

            for orig_idx, task in filtered_tasks:
                item = QListWidgetItem(target_list_widget)
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(16 if is_spacious else 14, 12 if is_spacious else 10, 16 if is_spacious else 14, 12 if is_spacious else 10)
                row_layout.setSpacing(14 if is_spacious else 12)

                is_done = task.get("completed", False)

                chk = QCheckBox(task.get("text", ""))
                chk.setChecked(is_done)
                if is_done:
                    chk.setStyleSheet(f"color: #64748B; text-decoration: line-through; font-size: {'18px' if is_spacious else '16px'};")
                else:
                    chk.setStyleSheet(f"color: #F8FAFC; font-size: {'18px' if is_spacious else '16px'}; font-weight: 600;")

                chk.stateChanged.connect(lambda state, i=orig_idx: self.toggle_task(i, state == 2))

                # Status Badge Label
                lbl_badge = QLabel("مكتملة ✅" if is_done else "قيد الانتظار ⏳")
                if is_done:
                    lbl_badge.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.4); font-size: {'13px' if is_spacious else '12px'}; font-weight: bold; border-radius: 8px; padding: 5px 10px;")
                else:
                    lbl_badge.setStyleSheet(f"background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); font-size: {'13px' if is_spacious else '12px'}; font-weight: bold; border-radius: 8px; padding: 5px 10px;")

                btn_del = QPushButton()
                btn_del.setObjectName("IconTrashBtn")
                btn_del.setCursor(Qt.PointingHandCursor)
                btn_del.setFixedSize(40 if is_spacious else 36, 40 if is_spacious else 36)
                if not trash_pix.isNull():
                    btn_del.setIcon(QIcon(trash_pix))
                    btn_del.setIconSize(QSize(20 if is_spacious else 18, 20 if is_spacious else 18))
                btn_del.setToolTip("حذف المهمة")
                btn_del.clicked.connect(lambda ch, i=orig_idx: self.delete_task(i))

                row_layout.addWidget(chk, 1)
                row_layout.addWidget(lbl_badge, 0, Qt.AlignRight | Qt.AlignVCenter)
                row_layout.addWidget(btn_del, 0, Qt.AlignRight | Qt.AlignVCenter)

                row_widget.setLayout(row_layout)

                hint = row_widget.sizeHint()
                hint.setHeight(max(hint.height(), 64 if is_spacious else 52))
                item.setSizeHint(hint)

                target_list_widget.addItem(item)
                target_list_widget.setItemWidget(item, row_widget)

        if hasattr(self, 'list_tasks'):
            populate_widget(self.list_tasks, is_spacious=False)

        if hasattr(self, 'list_tasks_page'):
            populate_widget(self.list_tasks_page, is_spacious=True)

    # Manual Start / Finish Session Actions
    def start_manual_session(self):
        self.app_blocker.is_active = True
        self.config["manual_session_active"] = True
        self.cfg_mgr.save_config()
        self.update_status_ui(True)

    def finish_learning_session(self):
        self.app_blocker.is_active = False
        self.config["manual_session_active"] = False
        self.cfg_mgr.save_config()
        self.update_status_ui(False)

    def update_status_ui(self, active: bool):
        if active:
            self.status_card.setStyleSheet("background-color: #111827; border-left: 6px solid #10B981;")
            self.lbl_status_title.setText("حالة جلسة التعلم: نشطة ⚡ (الحظر مفعل)")
            self.lbl_status_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #10B981;")
            self.lbl_status_desc.setText("يتم حظر جميع التطبيقات الممنوعة حالياً لزيادة إنتاجيتك!")
            
            self.btn_start_learning.setVisible(False)
            self.btn_finish_learning.setVisible(True)
        else:
            self.status_card.setStyleSheet("background-color: #111827; border-left: 6px solid #64748B;")
            self.lbl_status_title.setText("حالة جلسة التعلم: غير نشطة")
            self.lbl_status_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #94A3B8;")
            self.lbl_status_desc.setText("يمكنك استخدام الجهاز بحرية. عند بدء التعلم اضغط الزر أدناه.")

            self.btn_start_learning.setVisible(True)
            self.btn_finish_learning.setVisible(False)

    def toggle_startup(self, checked):
        self.cfg_mgr.set_startup(checked)

    def toggle_sound(self, checked):
        self.config["sound_enabled"] = checked
        self.audio_mgr.enabled = checked
        self.cfg_mgr.save_config()

    def test_water_overlay(self):
        """تفتح شاشة الماء — لكن فقط إذا ما كانت مفتوحة بالفعل."""
        if self._water_overlay_open:
            return
        self._water_overlay_open = True
        self.water_overlay = WaterOverlayWindow(
            audio_mgr=self.audio_mgr,
            on_finish_callback=self.handle_overlay_finish
        )

    def test_pushups_overlay(self):
        """تفتح شاشة التمارين بالتدوير بين مختلف التمارين الرياضية."""
        if self._pushups_overlay_open:
            return
        self._pushups_overlay_open = True
        
        ex_idx = self.config.get("exercise_index", 0)
        ex_info = EXERCISES_LIST[ex_idx % len(EXERCISES_LIST)]
        self.config["exercise_index"] = (ex_idx + 1) % len(EXERCISES_LIST)
        self.cfg_mgr.save_config()

        self.pushups_overlay = ExerciseOverlayWindow(
            exercise_info=ex_info,
            audio_mgr=self.audio_mgr,
            on_finish_callback=self.handle_overlay_finish
        )

    def reset_user_progress(self):
        reply = QMessageBox.warning(
            self,
            "إعادة تعيين التقدم والنقاط",
            "هل أنت تأكد من إعادة تعيين كافة النقاط، الأوسمة، وإحصائيات التقدم والبدء من جديد؟\n\nلا يمكن التراجع عن هذا الإجراء بعد تنفيذه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config["user_score"] = 0
            self.config["unlocked_badges"] = []
            today_str = datetime.date.today().isoformat()
            self.config["daily_stats"] = {
                "date": today_str,
                "water_count": 0,
                "pushups_count": 0,
                "learning_minutes": 0
            }
            self.config["weekly_history"] = {}
            self.config["total_water_count"] = 0
            self.config["total_pushups_count"] = 0
            self.config["total_learn_minutes"] = 0
            self.config["total_tasks_done"] = 0
            self.cfg_mgr.save_config()
            self.reload_analytics_ui()
            self.reload_tasks_list()
            QMessageBox.information(self, "تم الإعادة", "تم إعادة تعيين النقاط والتقدم إلى البداية بنجاح! 🚀")

    def change_water_interval(self, index):
        val = self.cmb_water_interval.itemData(index)
        if val:
            self.config["water_interval_min"] = val
            self.cfg_mgr.save_config()

    def change_pushups_interval(self, index):
        val = self.cmb_pushups_interval.itemData(index)
        if val:
            self.config["pushups_interval_min"] = val
            self.cfg_mgr.save_config()

    def set_badge_filter(self, filter_val):
        self.current_badge_filter = filter_val
        self.reload_analytics_ui()

    def award_points(self, amount, reason=""):
        curr = self.config.get("user_score", 0) + amount
        self.config["user_score"] = curr

        unlocked = self.config.get("unlocked_badges", [])
        daily = self.config.get("daily_stats", {})
        w_cnt  = daily.get("water_count", 0)
        p_cnt  = daily.get("pushups_count", 0)
        l_min  = daily.get("learning_minutes", 0)
        t_done = sum(1 for t in self.config.get("daily_tasks", []) if t.get("completed", False))
        t_total = self.config.get("total_tasks_done", t_done)  # lifetime total (approximate)
        w_total = self.config.get("total_water_count", w_cnt)
        p_total = self.config.get("total_pushups_count", p_cnt)
        l_total = self.config.get("total_learn_minutes", l_min)

        # Update lifetime totals
        self.config["total_water_count"]    = max(w_total, w_cnt)
        self.config["total_pushups_count"]  = max(p_total, p_cnt)
        self.config["total_learn_minutes"]  = max(l_total, l_min)
        self.config["total_tasks_done"]     = max(t_total, t_done)

        for badge in ALL_BADGES:
            bid = badge["id"]
            if bid in unlocked:
                continue
            earned = False
            if "water_min"     in badge and w_cnt  >= badge["water_min"]:    earned = True
            if "water_total"   in badge and w_total >= badge["water_total"]:  earned = True
            if "pushups_min"   in badge and p_cnt  >= badge["pushups_min"]:   earned = True
            if "pushups_total" in badge and p_total >= badge["pushups_total"]: earned = True
            if "learn_day"     in badge and l_min  >= badge["learn_day"]:     earned = True
            if "learn_total"   in badge and l_total >= badge["learn_total"]:  earned = True
            if "tasks_done"    in badge and t_done >= badge["tasks_done"]:    earned = True
            if "tasks_total"   in badge and t_total >= badge["tasks_total"]:  earned = True
            if "score_min"     in badge and curr   >= badge["score_min"]:     earned = True
            if earned:
                unlocked.append(bid)
                bonus = badge.get("pts", 0)
                if bonus > 0:
                    curr += bonus

        self.config["user_score"] = curr
        self.config["unlocked_badges"] = unlocked
        self.cfg_mgr.save_config()
        self.reload_analytics_ui()

    def reload_analytics_ui(self):
        if not hasattr(self, 'lbl_user_score_value'):
            return

        score = self.config.get("user_score", 0)
        self.lbl_user_score_value.setText(f"{score}")

        # ── Determine current rank ────────────────────────────────────────────
        current_rank_idx = 0
        for i, (pts_req, name, color, desc) in enumerate(RANKS):
            if score >= pts_req:
                current_rank_idx = i
            else:
                break

        rank_pts, rank_name, rank_color, rank_desc = RANKS[current_rank_idx]
        has_next = current_rank_idx + 1 < len(RANKS)

        if hasattr(self, 'lbl_level_badge'):
            self.lbl_level_badge.setText(rank_name)
            self.lbl_level_badge.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {rank_color}33, stop:1 {rank_color}11);
                color: {rank_color};
                border: 1px solid {rank_color};
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
                padding: 10px 20px;
            """)

        if hasattr(self, 'lbl_rank_desc'):
            self.lbl_rank_desc.setText(rank_desc)

        if hasattr(self, 'rank_progress_bar') and hasattr(self, 'lbl_rank_next_pts'):
            if has_next:
                next_pts = RANKS[current_rank_idx + 1][0]
                next_name = RANKS[current_rank_idx + 1][1]
                prev_pts = rank_pts
                span = max(next_pts - prev_pts, 1)
                prog = min(100, int(((score - prev_pts) / span) * 100))
                self.rank_progress_bar.setValue(prog)
                self.lbl_rank_next_pts.setText(f"{score}/{next_pts} نقطة لـ {next_name}")
                self.lbl_rank_progress_text.setText("التقدم نحو الرانك التالي:")
            else:
                self.rank_progress_bar.setValue(100)
                self.lbl_rank_next_pts.setText("🌟 وصلت لأعلى رانك! أنت أسطورة!")
                self.lbl_rank_progress_text.setText("")

        # ── Ranks Grid ────────────────────────────────────────────────────────
        if hasattr(self, 'ranks_grid_layout'):
            # Clear old widgets
            while self.ranks_grid_layout.count():
                item = self.ranks_grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            cols = 6
            for i, (pts_req, name, color, desc) in enumerate(RANKS):
                is_reached = score >= pts_req
                is_current = (i == current_rank_idx)

                r_frame = QFrame()
                r_frame.setFixedHeight(72)
                if is_current:
                    r_frame.setStyleSheet(f"""
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}44, stop:1 {color}22);
                        border: 2px solid {color};
                        border-radius: 12px;
                    """)
                elif is_reached:
                    r_frame.setStyleSheet(f"""
                        background: {color}15;
                        border: 1px solid {color}66;
                        border-radius: 12px;
                    """)
                else:
                    r_frame.setStyleSheet("""
                        background: #0B0F19;
                        border: 1px solid #1F293D;
                        border-radius: 12px;
                    """)

                r_layout = QVBoxLayout(r_frame)
                r_layout.setContentsMargins(8, 6, 8, 6)
                r_layout.setSpacing(2)

                lbl_name = QLabel(name)
                lbl_name.setAlignment(Qt.AlignCenter)
                lbl_name.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color if (is_reached or is_current) else '#475569'};")
                lbl_name.setWordWrap(True)

                lbl_pts = QLabel(f"{pts_req} نقطة" if not is_current else "◀ رانكك")
                lbl_pts.setAlignment(Qt.AlignCenter)
                lbl_pts.setStyleSheet(f"font-size: 11px; color: {'#F59E0B' if is_current else ('#64748B' if not is_reached else color)};")

                r_layout.addWidget(lbl_name)
                r_layout.addWidget(lbl_pts)

                row = i // cols
                col = i % cols
                self.ranks_grid_layout.addWidget(r_frame, row, col)

        # ── Weekly Bars ───────────────────────────────────────────────────────
        if hasattr(self, 'weekly_bars_layout'):
            while self.weekly_bars_layout.count():
                child = self.weekly_bars_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    # Clear nested layout items
                    while child.layout().count():
                        sub = child.layout().takeAt(0)
                        if sub.widget():
                            sub.widget().deleteLater()

            today = datetime.date.today()
            history = self.config.get("weekly_history", {})
            days_arabic = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]

            max_mins = 1
            daily_data = []
            for i in range(6, -1, -1):
                d = today - datetime.timedelta(days=i)
                d_str = d.isoformat()
                day_name = days_arabic[d.weekday()]
                if d_str == today.isoformat():
                    mins = self.config.get("daily_stats", {}).get("learning_minutes", 0)
                else:
                    mins = history.get(d_str, {}).get("learning_minutes", 0)
                max_mins = max(max_mins, mins)
                daily_data.append((day_name, mins, d_str == today.isoformat()))

            best_day = max(daily_data, key=lambda x: x[1])
            if hasattr(self, 'lbl_best_day'):
                if best_day[1] > 0:
                    self.lbl_best_day.setText(f"🏆 {best_day[0]}: {best_day[1]} دقيقة")
                else:
                    self.lbl_best_day.setText("ابدأ التعلم لتسجل أول إنجاز!")

            for day_name, mins, is_today in daily_data:
                col_w = QWidget()
                col_w.setStyleSheet("background: transparent;")
                col = QVBoxLayout(col_w)
                col.setSpacing(5)
                col.setAlignment(Qt.AlignBottom)

                max_bar_h = 120
                height_factor = max(8, int((mins / max_mins) * max_bar_h)) if max_mins > 0 else 8
                bar_frame = QFrame()
                bar_frame.setFixedWidth(44)
                bar_frame.setFixedHeight(height_factor)

                if is_today:
                    bar_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #059669); border-radius: 8px;")
                elif mins > 0:
                    bar_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38BDF8, stop:1 #0284C7); border-radius: 8px;")
                else:
                    bar_frame.setStyleSheet("background: #1F293D; border-radius: 8px;")

                lbl_val = QLabel(f"{mins}م" if mins > 0 else "-")
                lbl_val.setAlignment(Qt.AlignCenter)
                lbl_val.setStyleSheet("font-size: 11px; font-weight: bold; color: #94A3B8; background: transparent;")

                lbl_day = QLabel(day_name)
                lbl_day.setAlignment(Qt.AlignCenter)
                lbl_day.setStyleSheet("font-size: 11px; font-weight: bold; background: transparent; color: " + ("#10B981;" if is_today else "#94A3B8;"))

                # Spacer to push bar to bottom
                spacer_h = max_bar_h - height_factor
                col.addSpacing(spacer_h)
                col.addWidget(lbl_val, 0, Qt.AlignHCenter)
                col.addWidget(bar_frame, 0, Qt.AlignHCenter)
                col.addWidget(lbl_day, 0, Qt.AlignHCenter)

                self.weekly_bars_layout.addWidget(col_w)

        # ── Badges Gallery ────────────────────────────────────────────────────
        if hasattr(self, 'badges_scroll_grid'):
            while self.badges_scroll_grid.count():
                item = self.badges_scroll_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            unlocked = self.config.get("unlocked_badges", [])
            cat_filter = getattr(self, 'current_badge_filter', 'all')

            # Update filter button active states
            badge_filter_map = {
                "btn_badge_filter_all":     "all",
                "btn_badge_filter_water":   "water",
                "btn_badge_filter_pushups": "pushups",
                "btn_badge_filter_learn":   "learn",
                "btn_badge_filter_tasks":   "tasks",
                "btn_badge_filter_score":   "score",
            }
            for btn_name, val in badge_filter_map.items():
                if hasattr(self, btn_name):
                    b = getattr(self, btn_name)
                    b.setProperty("active", "true" if cat_filter == val else "false")
                    b.setStyle(b.style())

            filtered_badges = [
                b for b in ALL_BADGES
                if cat_filter == "all" or b["cat"] == cat_filter
            ]

            unlocked_count = sum(1 for b in ALL_BADGES if b["id"] in unlocked)
            if hasattr(self, 'lbl_badges_count'):
                self.lbl_badges_count.setText(f"✅ {unlocked_count} / {len(ALL_BADGES)} وسام")

            CAT_COLORS = {
                "water":   ("#38BDF8", "#0C2D3E"),
                "pushups": ("#FB923C", "#2E1A0E"),
                "learn":   ("#A78BFA", "#1D1435"),
                "tasks":   ("#34D399", "#0E2E22"),
                "score":   ("#F59E0B", "#2E2008"),
            }

            COLS = 4
            for idx, badge in enumerate(filtered_badges):
                bid = badge["id"]
                is_unlocked = bid in unlocked
                bcat = badge.get("cat", "score")
                accent, bg_dark = CAT_COLORS.get(bcat, ("#94A3B8", "#111827"))

                b_card = QFrame()
                b_card.setMinimumHeight(110)
                if is_unlocked:
                    b_card.setStyleSheet(f"""
                        QFrame {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {bg_dark}, stop:1 #111827);
                            border: 1px solid {accent};
                            border-radius: 14px;
                        }}
                    """)
                else:
                    b_card.setStyleSheet("""
                        QFrame {
                            background-color: #0B0F19;
                            border: 1px solid #1F293D;
                            border-radius: 14px;
                        }
                    """)

                b_layout = QVBoxLayout(b_card)
                b_layout.setContentsMargins(12, 10, 12, 10)
                b_layout.setSpacing(4)

                lbl_t = QLabel(badge["title"])
                lbl_t.setWordWrap(True)
                lbl_t.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {accent if is_unlocked else '#475569'};")

                lbl_d = QLabel(badge["desc"])
                lbl_d.setWordWrap(True)
                lbl_d.setStyleSheet("font-size: 11px; color: #64748B;")

                pts_text = f"+{badge['pts']} نقطة" if badge.get('pts', 0) > 0 else ""
                lbl_pts = QLabel(pts_text)
                lbl_pts.setStyleSheet(f"font-size: 11px; color: {'#F59E0B' if is_unlocked else '#334155'}; font-weight: bold;")

                lbl_st = QLabel("✅ تم الفتح" if is_unlocked else "🔒 مغلق")
                lbl_st.setAlignment(Qt.AlignRight)
                lbl_st.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {'#10B981' if is_unlocked else '#334155'};")

                b_layout.addWidget(lbl_t)
                b_layout.addWidget(lbl_d)
                b_layout.addWidget(lbl_pts)
                b_layout.addStretch()
                b_layout.addWidget(lbl_st)

                row = idx // COLS
                col_i = idx % COLS
                self.badges_scroll_grid.addWidget(b_card, row, col_i)

    def handle_overlay_finish(self, overlay_type):
        if overlay_type == "water":
            self._water_overlay_open = False
            self.config["daily_stats"]["water_count"] += 1
            self.lbl_stat_water.setText(f"{self.config['daily_stats']['water_count']} أكواب")
            self.award_points(15, "ماء")
        elif overlay_type == "pushups":
            self._pushups_overlay_open = False
            self.config["daily_stats"]["pushups_count"] += 5
            self.lbl_stat_pushups.setText(f"{self.config['daily_stats']['pushups_count']} ضغطات")
            self.award_points(20, "بوش أب")
        elif overlay_type == "schedule":
            self._schedule_overlay_open = False
        self.cfg_mgr.save_config()

    # Background Timers
    def setup_background_timers(self):
        self.proc_timer = QTimer(self)
        self.proc_timer.timeout.connect(self.check_processes_loop)
        self.proc_timer.start(2000)

        self.minute_timer = QTimer(self)
        self.minute_timer.timeout.connect(self.minute_tick_loop)
        self.minute_timer.start(60000)

    def check_processes_loop(self):
        now_str = QTime.currentTime().toString("hh:mm")

        if not self._schedule_overlay_open:
            for sched in self.config.get("learning_schedules", []):
                if sched.get("active", True) and sched["start"] == now_str:
                    sched_key = f"{sched['name']}_{now_str}"
                    if self.last_triggered_schedule_key != sched_key:
                        self.last_triggered_schedule_key = sched_key
                        self._schedule_overlay_open = True
                        self.sched_overlay = StartScheduleOverlayWindow(
                            sched_name=sched["name"],
                            audio_mgr=self.audio_mgr,
                            on_confirm_callback=self._on_schedule_confirmed
                        )
                        break

        if self.config.get("manual_session_active", False) or self.app_blocker.is_active:
            self.app_blocker.check_and_enforce()

    def _on_schedule_confirmed(self):
        """يُستدعى عند الضغط على 'حسناً' في شاشة بدء الجدول."""
        self._schedule_overlay_open = False
        self.start_manual_session()

    def minute_tick_loop(self):
        if self.app_blocker.is_active:
            self.config["daily_stats"]["learning_minutes"] += 1
            self.lbl_stat_time.setText(f"{self.config['daily_stats']['learning_minutes']} دقيقة")
            self.award_points(1, "دقيقة تعلم")

            # 💡 Motivational notifications during active study session
            self.study_motivate_counter = getattr(self, "study_motivate_counter", 0) + 1
            if self.study_motivate_counter >= 10:
                self.study_motivate_counter = 0
                quote = random.choice(MOTIVATIONAL_STUDY_QUOTES)
                if hasattr(self, "tray_icon") and self.tray_icon:
                    self.tray_icon.showMessage("💪 تحفيز الدراسة والتركيز 🚀", quote, QSystemTrayIcon.Information, 7000)

            today_str = datetime.date.today().isoformat()
            if "weekly_history" not in self.config:
                self.config["weekly_history"] = {}
            self.config["weekly_history"][today_str] = {
                "learning_minutes": self.config["daily_stats"]["learning_minutes"],
                "water_count": self.config["daily_stats"]["water_count"],
                "pushups_count": self.config["daily_stats"]["pushups_count"]
            }
            self.cfg_mgr.save_config()

        self.water_timer_counter += 1
        self.pushups_timer_counter += 1

        # ✅ فقط إذا ما كانت شاشة مفتوحة بالفعل
        if self.water_timer_counter >= self.config.get("water_interval_min", 40):
            self.water_timer_counter = 0
            if not self._water_overlay_open:
                self.test_water_overlay()

        if self.pushups_timer_counter >= self.config.get("pushups_interval_min", 120):
            self.pushups_timer_counter = 0
            if not self._pushups_overlay_open:
                self.test_pushups_overlay()

    # System Tray
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("مركز الإنتاجية الذكي")

        tray_menu = QMenu()
        show_action = QAction("فتح النافذة الرئيسية", self)
        show_action.triggered.connect(self.showNormal)

        start_action = QAction("بدء جلسة تعلم", self)
        start_action.triggered.connect(self.start_manual_session)

        stop_action = QAction("لقد أنهيت التعلم", self)
        stop_action.triggered.connect(self.finish_learning_session)

        quit_action = QAction("إغلاق التطبيق نهائياً", self)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(start_action)
        tray_menu.addAction(stop_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "مركز الإنتاجية الذكي",
            "يعمل البرنامج بالخلفية وسينبهك بالمواعيد والتمرين!",
            QSystemTrayIcon.Information,
            3000
        )
