import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox, QCheckBox,
    QStackedWidget, QFrame, QDialog, QMessageBox, QSystemTrayIcon, QMenu, QSizePolicy, QProgressBar
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

        # ✅ منع تكرار شاشات التذكير
        self._water_overlay_open = False
        self._pushups_overlay_open = False
        self._schedule_overlay_open = False

        self.current_task_filter = "all"

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
        self.btn_nav_sets = self.create_nav_button(" الإعدادات والاختبار", "settingslogo.png", 5)

        self.btn_nav_dash.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_nav_dash)
        sidebar_layout.addWidget(self.btn_nav_tasks)
        sidebar_layout.addWidget(self.btn_nav_badge)
        sidebar_layout.addWidget(self.btn_nav_sched)
        sidebar_layout.addWidget(self.btn_nav_block)
        sidebar_layout.addWidget(self.btn_nav_sets)
        sidebar_layout.addStretch()

        ver_lbl = QLabel("الإصدار الأسطوري 5.0 ⚡")
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
        nav_btns = [self.btn_nav_dash, self.btn_nav_tasks, self.btn_nav_badge, self.btn_nav_sched, self.btn_nav_block, self.btn_nav_sets]
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
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header Title
        title_box = QHBoxLayout()
        trophy_pix = get_tinted_pixmap("bullseye-arrowlogo.png", "#F59E0B", QSize(36, 36))
        if not trophy_pix.isNull():
            ic_lbl = QLabel()
            ic_lbl.setPixmap(trophy_pix)
            title_box.addWidget(ic_lbl)

        title = QLabel("🏆 إحصائياتك وشارات الإنجاز")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F8FAFC;")
        title_box.addWidget(title)
        title_box.addStretch()

        layout.addLayout(title_box)

        # Gamification Score Card
        score_card = QFrame()
        score_card.setObjectName("Card")
        score_card.setStyleSheet("background-color: #111827; border-left: 6px solid #F59E0B;")
        sc_layout = QHBoxLayout(score_card)

        sc_info = QVBoxLayout()
        self.lbl_user_score_title = QLabel("⚡ نقاط الإنتاجية والتركيز")
        self.lbl_user_score_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F59E0B;")
        
        self.lbl_user_score_value = QLabel(f"{self.config.get('user_score', 0)} نقطة")
        self.lbl_user_score_value.setStyleSheet("font-size: 32px; font-weight: bold; color: #F8FAFC;")

        sc_info.addWidget(self.lbl_user_score_title)
        sc_info.addWidget(self.lbl_user_score_value)

        # Level Badge
        sc_level_box = QVBoxLayout()
        sc_level_box.setAlignment(Qt.AlignCenter)
        self.lbl_level_badge = QLabel("المستوى 1: مبتدئ نشيط 🌱")
        self.lbl_level_badge.setStyleSheet("background-color: rgba(245, 158, 11, 0.18); color: #F59E0B; border: 1px solid #F59E0B; font-size: 16px; font-weight: bold; border-radius: 12px; padding: 10px 20px;")
        sc_level_box.addWidget(self.lbl_level_badge)

        sc_layout.addLayout(sc_info)
        sc_layout.addStretch()
        sc_layout.addLayout(sc_level_box)

        layout.addWidget(score_card)

        # Weekly Progress & Bar Visualization Card
        weekly_card = QFrame()
        weekly_card.setObjectName("Card")
        wk_layout = QVBoxLayout(weekly_card)
        wk_layout.setSpacing(14)

        wk_title = QLabel("📊 الإنجاز والتطور الأسبوعي (أخر 7 أيام)")
        wk_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        wk_layout.addWidget(wk_title)

        self.lbl_best_day = QLabel("🏆 أفضل يوم إنتاجية هذا الأسبوع: اليوم!")
        self.lbl_best_day.setStyleSheet("font-size: 15px; color: #10B981; font-weight: bold;")
        wk_layout.addWidget(self.lbl_best_day)

        # Weekly Bars Container
        self.weekly_bars_layout = QHBoxLayout()
        self.weekly_bars_layout.setSpacing(12)
        wk_layout.addLayout(self.weekly_bars_layout)

        layout.addWidget(weekly_card)

        # Badges Showcase Card
        badges_card = QFrame()
        badges_card.setObjectName("Card")
        bg_layout = QVBoxLayout(badges_card)
        bg_layout.setSpacing(14)

        bg_title = QLabel("🎖️ معرض الأوسمة والتحديات:")
        bg_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F8FAFC;")
        bg_layout.addWidget(bg_title)

        self.badges_grid = QHBoxLayout()
        self.badges_grid.setSpacing(12)
        bg_layout.addLayout(self.badges_grid)

        layout.addWidget(badges_card)

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
        pushups_box.addWidget(QLabel("🏋️ تذكير تمارين الضغط:"))
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
            self.config["daily_tasks"][index]["completed"] = is_checked
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
        """تفتح شاشة البوش-أب — لكن فقط إذا ما كانت مفتوحة بالفعل."""
        if self._pushups_overlay_open:
            return
        self._pushups_overlay_open = True
        self.pushups_overlay = PushupsOverlayWindow(
            audio_mgr=self.audio_mgr,
            on_finish_callback=self.handle_overlay_finish
        )

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

    def award_points(self, amount, reason=""):
        curr = self.config.get("user_score", 0) + amount
        self.config["user_score"] = curr
        
        # Unlocked badges evaluation
        unlocked = self.config.get("unlocked_badges", [])
        w_cnt = self.config.get("daily_stats", {}).get("water_count", 0)
        p_cnt = self.config.get("daily_stats", {}).get("pushups_count", 0)
        l_min = self.config.get("daily_stats", {}).get("learning_minutes", 0)
        t_cnt = sum(1 for t in self.config.get("daily_tasks", []) if t.get("completed", False))

        if w_cnt >= 3 and "b_water_1" not in unlocked:
            unlocked.append("b_water_1")
        if w_cnt >= 10 and "b_water_2" not in unlocked:
            unlocked.append("b_water_2")
        if p_cnt >= 15 and "b_pushups_1" not in unlocked:
            unlocked.append("b_pushups_1")
        if l_min >= 60 and "b_learn_1" not in unlocked:
            unlocked.append("b_learn_1")
        if l_min >= 180 and "b_learn_2" not in unlocked:
            unlocked.append("b_learn_2")
        if t_cnt >= 3 and "b_tasks_1" not in unlocked:
            unlocked.append("b_tasks_1")
        if curr >= 100 and "b_score_100" not in unlocked:
            unlocked.append("b_score_100")

        self.config["unlocked_badges"] = unlocked
        self.cfg_mgr.save_config()
        self.reload_analytics_ui()

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
