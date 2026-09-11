import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox, QCheckBox,
    QStackedWidget, QFrame, QDialog, QMessageBox, QSystemTrayIcon, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QTime, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QAction

from config_manager import ConfigManager
from audio_manager import AudioManager
from app_blocker import AppBlocker
from asset_helper import get_asset_path, get_tinted_pixmap
from overlays import WaterOverlayWindow, PushupsOverlayWindow, StartScheduleOverlayWindow

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cfg_mgr = ConfigManager()
        self.config = self.cfg_mgr.config
        self.audio_mgr = AudioManager(enabled=self.config.get("sound_enabled", True))
        self.app_blocker = AppBlocker(audio_mgr=self.audio_mgr)
        self.app_blocker.set_blocked_apps(self.config.get("blocked_apps", []))

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
        self.last_triggered_schedule_key = ""

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
        self.btn_nav_sched = self.create_nav_button(" جدول التعلم", "calendarlogo.png", 1)
        self.btn_nav_block = self.create_nav_button(" التطبيقات الممنوعة", "forbiddenapps.png", 2)
        self.btn_nav_sets = self.create_nav_button(" الإعدادات والاختبار", "settingslogo.png", 3)

        self.btn_nav_dash.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_nav_dash)
        sidebar_layout.addWidget(self.btn_nav_sched)
        sidebar_layout.addWidget(self.btn_nav_block)
        sidebar_layout.addWidget(self.btn_nav_sets)
        sidebar_layout.addStretch()

        ver_lbl = QLabel("الإصدار الأسهل 4.0 ⚡")
        ver_lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(ver_lbl)

        # Stacked Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_dashboard_page())
        self.pages.addWidget(self.create_schedules_page())
        self.pages.addWidget(self.create_blocked_apps_page())
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
        nav_btns = [self.btn_nav_dash, self.btn_nav_sched, self.btn_nav_block, self.btn_nav_sets]
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
        layout.addStretch()

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

    # Page 4: Settings & Instant Testing
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

        # Test Center
        test_card = QFrame()
        test_card.setObjectName("Card")
        test_layout = QVBoxLayout(test_card)
        test_layout.setSpacing(15)

        test_title = QLabel("🎯 تجربة شاشات التنبيه فوراً")
        test_title.setObjectName("CardTitle")

        test_desc = QLabel("يمكنك اختبار شكل شاشة شرب الماء وشاشة التمارين والصوت المتكرر فوراً.")
        test_desc.setStyleSheet("color: #94A3B8; font-size: 15px;")

        btn_box = QHBoxLayout()
        btn_box.setSpacing(15)

        btn_test_water = QPushButton("💧 تجربة شاشة شرب الماء الان")
        btn_test_water.setObjectName("PrimaryBtn")
        btn_test_water.setCursor(Qt.PointingHandCursor)
        btn_test_water.clicked.connect(self.test_water_overlay)

        btn_test_pushups = QPushButton("🏋️ تجربة شاشة البوش اب الان")
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
        
        forb_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(24, 24))
        trash_pix = get_tinted_pixmap("forbiddenapps.png", "#EF4444", QSize(22, 22))

        for idx, app in enumerate(self.config.get("blocked_apps", [])):
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
            btn_del.clicked.connect(lambda ch, i=idx: self.delete_blocked_app(i))

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

    def open_running_apps_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("اختر تطبيقاً حياً لحظره")
        dialog.resize(440, 500)
        dialog.setStyleSheet("background-color: #090D16; color: white;")

        d_layout = QVBoxLayout(dialog)
        d_layout.addWidget(QLabel("اختر من التطبيقات المفتوحة حالياً:"))

        running_list = QListWidget()
        running_apps = AppBlocker.get_running_apps()
        for app in running_apps:
            running_list.addItem(app)
        d_layout.addWidget(running_list)

        btn_confirm = QPushButton("إضافة للتطبيقات الممنوعة")
        btn_confirm.setObjectName("PrimaryBtn")
        btn_confirm.setStyleSheet("background-color: #0284C7; color: white; padding: 12px; font-weight: bold;")

        def confirm_selection():
            selected = running_list.currentItem()
            if selected:
                app_name = selected.text()
                if app_name not in self.config["blocked_apps"]:
                    self.config["blocked_apps"].append(app_name)
                    self.cfg_mgr.save_config()
                    self.app_blocker.set_blocked_apps(self.config["blocked_apps"])
                    self.reload_blocked_apps_list()
                dialog.accept()

        btn_confirm.clicked.connect(confirm_selection)
        d_layout.addWidget(btn_confirm)
        dialog.exec()

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
        self.water_overlay = WaterOverlayWindow(audio_mgr=self.audio_mgr, on_finish_callback=self.handle_overlay_finish)

    def test_pushups_overlay(self):
        self.pushups_overlay = PushupsOverlayWindow(audio_mgr=self.audio_mgr, on_finish_callback=self.handle_overlay_finish)

    def handle_overlay_finish(self, overlay_type):
        if overlay_type == "water":
            self.config["daily_stats"]["water_count"] += 1
            self.lbl_stat_water.setText(f"{self.config['daily_stats']['water_count']} أكواب")
        elif overlay_type == "pushups":
            self.config["daily_stats"]["pushups_count"] += 5
            self.lbl_stat_pushups.setText(f"{self.config['daily_stats']['pushups_count']} ضغطات")
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

        for sched in self.config.get("learning_schedules", []):
            if sched.get("active", True) and sched["start"] == now_str:
                sched_key = f"{sched['name']}_{now_str}"
                if self.last_triggered_schedule_key != sched_key:
                    self.last_triggered_schedule_key = sched_key
                    self.sched_overlay = StartScheduleOverlayWindow(
                        sched_name=sched["name"],
                        audio_mgr=self.audio_mgr,
                        on_confirm_callback=self.start_manual_session
                    )
                    break

        if self.config.get("manual_session_active", False) or self.app_blocker.is_active:
            self.app_blocker.check_and_enforce()

    def minute_tick_loop(self):
        if self.app_blocker.is_active:
            self.config["daily_stats"]["learning_minutes"] += 1
            self.lbl_stat_time.setText(f"{self.config['daily_stats']['learning_minutes']} دقيقة")
            self.cfg_mgr.save_config()

        self.water_timer_counter += 1
        self.pushups_timer_counter += 1

        if self.water_timer_counter >= self.config.get("water_interval_min", 40):
            self.water_timer_counter = 0
            self.test_water_overlay()

        if self.pushups_timer_counter >= self.config.get("pushups_interval_min", 120):
            self.pushups_timer_counter = 0
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
