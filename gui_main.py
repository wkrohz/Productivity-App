def open_url_in_default_browser(url):
    u = url.strip()
    if not (u.startswith("http://") or u.startswith("https://")):
        u = "https://" + u
    try:
        webbrowser.open(u, new=2)
    except Exception as e:
        print("webbrowser open error:", e)
    try:
        os.system(f'start "" "{u}"')
    except Exception as e:
        print("os start error:", e)

import sys
import os
import datetime
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox, QCheckBox,
    QStackedWidget, QFrame, QDialog, QMessageBox, QSystemTrayIcon, QMenu, QSizePolicy, QProgressBar,
    QGridLayout, QScrollArea, QGraphicsDropShadowEffect, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QTime, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QAction

from config_manager import ConfigManager
from audio_manager import AudioManager
from app_blocker import AppBlocker
from asset_helper import get_asset_path, get_tinted_pixmap, get_tinted_icon
from overlays import (WaterOverlayWindow, PushupsOverlayWindow, StartScheduleOverlayWindow,
                       ExerciseOverlayWindow, PrayerOverlayWindow, EyeRestOverlayWindow,
                       AppointmentReminderOverlay, EXERCISES_LIST)

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

def clear_layout_recursive(layout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
        elif item.layout() is not None:
            clear_layout_recursive(item.layout())

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

class AddPortfolioFolderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("أضف مجلد إنجاز جديد")
        self.setMinimumWidth(440)
        self.setStyleSheet("background-color: #0F172A; color: #F1F5F9; font-family: 'Segoe UI', sans-serif;")
        self.folder_title = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl_t = QLabel("📂 إنشاء مجلد إنجازات جديد")
        lbl_t.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        lbl_d = QLabel("أدخل عنوان المجلد (مثل: شهادات الدورات، إنجازات الجامعة):")
        lbl_d.setStyleSheet("color: #94A3B8; font-size: 13px;")

        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("عنوان المجلد...")

        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 10px; padding: 8px 18px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("إنشاء المجلد 📁")
        btn_save.setObjectName("PrimaryBtn")
        btn_save.setStyleSheet("background: #0284C7; color: white; font-weight: bold; border-radius: 10px; padding: 8px 18px;")
        btn_save.clicked.connect(self.on_save)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_d)
        layout.addWidget(self.txt_title)
        layout.addLayout(btn_box)

    def on_save(self):
        title = self.txt_title.text().strip()
        if not title:
            QMessageBox.warning(self, "تنبيه", "يرجى كتابة عنوان للمجلد!")
            return
        self.folder_title = title
        self.accept()


class AddPortfolioItemDialog(QDialog):
    def __init__(self, folder_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"إضافة شهادة إلى: {folder_name}")
        self.setMinimumWidth(480)
        self.setStyleSheet("background-color: #0F172A; color: #F1F5F9; font-family: 'Segoe UI', sans-serif;")
        self.file_path = ""
        self.item_title = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl_t = QLabel(f"🖼️ إضافة شهادة / صورة إنجاز إلى ({folder_name})")
        lbl_t.setStyleSheet("font-size: 18px; font-weight: bold; color: #10B981;")

        self.lbl_img_preview = QLabel("لم يتم اختيار صورة بعد")
        self.lbl_img_preview.setFixedHeight(120)
        self.lbl_img_preview.setStyleSheet("background: #060A12; border: 1px dashed #38BDF8; border-radius: 12px; color: #64748B;")
        self.lbl_img_preview.setAlignment(Qt.AlignCenter)

        btn_pick = QPushButton("🔍 اختيار صورة الشهادة من جهازك")
        btn_pick.setStyleSheet("background: #0284C7; color: white; font-weight: bold; border-radius: 10px; padding: 10px 16px;")
        btn_pick.setCursor(Qt.PointingHandCursor)
        btn_pick.clicked.connect(self.on_pick_image)

        layout.addWidget(lbl_t)
        layout.addWidget(self.lbl_img_preview)
        layout.addWidget(btn_pick)

        lbl_title_tag = QLabel("عنوان الشهادة أو الإنجاز:")
        lbl_title_tag.setStyleSheet("color: #CBD5E1; font-weight: bold;")
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("مثال: شهادة إتمام دورة بايثون...")

        layout.addWidget(lbl_title_tag)
        layout.addWidget(self.txt_title)

        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 10px; padding: 8px 18px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("حفظ الشهادة 💾")
        btn_save.setStyleSheet("background: #10B981; color: white; font-weight: bold; border-radius: 10px; padding: 10px 18px;")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.on_save)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def on_pick_image(self):
        fp, _ = QFileDialog.getOpenFileName(self, "اختر صورة الشهادة", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if fp:
            self.file_path = fp
            pix = QPixmap(fp).scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_img_preview.setPixmap(pix)

    def on_save(self):
        if not self.file_path:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار صورة للشهادة أولاً!")
            return
        t = self.txt_title.text().strip()
        self.item_title = t if t else "شهادة إنجاز"
        self.accept()


class AddEditProfileDialog(QDialog):
    def __init__(self, profile=None, parent=None):
        super().__init__(parent)
        self.profile = profile or {}
        self.setWindowTitle("تعديل زر عمل سريع" if profile else "إضافة زر عمل سريع جديد")
        self.setMinimumSize(540, 520)
        self.setStyleSheet("background-color: #0F172A; color: #F1F5F9; font-family: 'Segoe UI', sans-serif;")

        self.result_profile = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl_t = QLabel("🚀 إعداد زر العمل السريع" if profile else "🚀 إضافة زر عمل سريع جديد")
        lbl_t.setStyleSheet("font-size: 18px; font-weight: bold; color: #C084FC;")
        layout.addWidget(lbl_t)

        # Profile Title
        lbl_title_tag = QLabel("اسم الزر / العنوان (مثال: 💻 بيئة البرمجة والتطوير):")
        lbl_title_tag.setStyleSheet("color: #CBD5E1; font-weight: bold;")
        self.txt_title = QLineEdit()
        self.txt_title.setText(self.profile.get("title", ""))
        self.txt_title.setPlaceholderText("أدخل اسم الزر...")
        layout.addWidget(lbl_title_tag)
        layout.addWidget(self.txt_title)

        # Sections for Apps and URLs
        grid_sections = QHBoxLayout()
        grid_sections.setSpacing(16)

        # ── Apps Box
        apps_box = QVBoxLayout()
        lbl_apps = QLabel("💻 التطبيقات (.exe):")
        lbl_apps.setStyleSheet("font-weight: bold; color: #38BDF8;")
        self.list_apps = QListWidget()
        self.list_apps.setStyleSheet("background: #060A12; border: 1px solid #1E293D; border-radius: 10px; padding: 4px;")
        for app in self.profile.get("apps", []):
            self.list_apps.addItem(app)

        btn_app_row = QHBoxLayout()
        btn_add_app = QPushButton("➕ إضافة تطبيق")
        btn_add_app.setStyleSheet("background: #0284C7; color: white; border-radius: 8px; padding: 6px 12px; font-weight: bold;")
        btn_add_app.setCursor(Qt.PointingHandCursor)
        btn_add_app.clicked.connect(self.add_app)
        btn_del_app = QPushButton("🗑️ حذف")
        btn_del_app.setStyleSheet("background: rgba(239,68,68,0.2); color: #EF4444; border-radius: 8px; padding: 6px 12px;")
        btn_del_app.setCursor(Qt.PointingHandCursor)
        btn_del_app.clicked.connect(self.del_app)
        btn_app_row.addWidget(btn_add_app)
        btn_app_row.addWidget(btn_del_app)

        apps_box.addWidget(lbl_apps)
        apps_box.addWidget(self.list_apps)
        apps_box.addLayout(btn_app_row)

        # ── URLs Box
        urls_box = QVBoxLayout()
        lbl_urls = QLabel("🌐 المواقع (URL):")
        lbl_urls.setStyleSheet("font-weight: bold; color: #A78BFA;")
        self.list_urls = QListWidget()
        self.list_urls.setStyleSheet("background: #060A12; border: 1px solid #1E293D; border-radius: 10px; padding: 4px;")
        for url in self.profile.get("urls", []):
            self.list_urls.addItem(url)

        btn_url_row = QHBoxLayout()
        btn_add_url = QPushButton("➕ إضافة موقع")
        btn_add_url.setStyleSheet("background: #7C3AED; color: white; border-radius: 8px; padding: 6px 12px; font-weight: bold;")
        btn_add_url.setCursor(Qt.PointingHandCursor)
        btn_add_url.clicked.connect(self.add_url)
        btn_del_url = QPushButton("🗑️ حذف")
        btn_del_url.setStyleSheet("background: rgba(239,68,68,0.2); color: #EF4444; border-radius: 8px; padding: 6px 12px;")
        btn_del_url.setCursor(Qt.PointingHandCursor)
        btn_del_url.clicked.connect(self.del_url)
        btn_url_row.addWidget(btn_add_url)
        btn_url_row.addWidget(btn_del_url)

        urls_box.addWidget(lbl_urls)
        urls_box.addWidget(self.list_urls)
        urls_box.addLayout(btn_url_row)

        grid_sections.addLayout(apps_box)
        grid_sections.addLayout(urls_box)
        layout.addLayout(grid_sections)

        # Dialog buttons
        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 10px; padding: 8px 18px;")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("حفظ الزر 💾")
        btn_save.setStyleSheet("background: #10B981; color: white; font-weight: bold; border-radius: 10px; padding: 10px 22px;")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.on_save)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def add_app(self):
        reply = QMessageBox.question(self, "إضافة تطبيق", "هل تريد تصفح الملفات لاختيار برنامج (.exe)؟", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            fp, _ = QFileDialog.getOpenFileName(self, "اختر البرنامج التنفيذي", "", "Executables (*.exe);;All Files (*)")
            if fp:
                self.list_apps.addItem(fp)
        elif reply == QMessageBox.No:
            text, ok = QInputDialog.getText(self, "إضافة تطبيق", "أدخل اسم البرنامج (مثل code.exe أو pycharm.exe):")
            if ok and text.strip():
                self.list_apps.addItem(text.strip())

    def del_app(self):
        row = self.list_apps.currentRow()
        if row >= 0:
            self.list_apps.takeItem(row)

    def add_url(self):
        text, ok = QInputDialog.getText(self, "إضافة موقع", "أدخل رابط الموقع (مثل: https://www.youtube.com):")
        if ok and text.strip():
            self.list_urls.addItem(text.strip())

    def del_url(self):
        row = self.list_urls.currentRow()
        if row >= 0:
            self.list_urls.takeItem(row)

    def on_save(self):
        title = self.txt_title.text().strip()
        if not title:
            QMessageBox.warning(self, "تنبيه", "يرجى أدخال اسم للزر!")
            return
        
        apps = [self.list_apps.item(i).text() for i in range(self.list_apps.count())]
        urls = [self.list_urls.item(i).text() for i in range(self.list_urls.count())]
        
        prof_id = self.profile.get("id") or f"profile_{int(datetime.datetime.now().timestamp())}"
        self.result_profile = {
            "id": prof_id,
            "title": title,
            "apps": apps,
            "urls": urls
        }
        self.accept()


class ManageQuickLaunchProfilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.setWindowTitle("إدارة أزرار العمل السريع")
        self.setMinimumSize(600, 480)
        self.setStyleSheet("background-color: #0F172A; color: #F1F5F9; font-family: 'Segoe UI', sans-serif;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QLabel("⚙️ ضبط وإدارة أزرار العمل السريع")
        hdr.setStyleSheet("font-size: 18px; font-weight: bold; color: #C084FC;")
        desc = QLabel("يمكنك إضافة أزرار عمل جديدة، تعديل اسم كل زر أو تطبيقاته ومواقعه، أو حذف أزرار:")
        desc.setStyleSheet("color: #94A3B8; font-size: 13px;")

        layout.addWidget(hdr)
        layout.addWidget(desc)

        content_h = QHBoxLayout()
        self.list_profiles = QListWidget()
        self.list_profiles.setStyleSheet("background: #060A12; border: 1px solid #1E293D; border-radius: 12px; font-size: 15px; padding: 6px;")

        btn_vbox = QVBoxLayout()
        btn_vbox.setSpacing(10)

        btn_add = QPushButton("➕ إضافة زر جديد")
        btn_add.setStyleSheet("background: #0284C7; color: white; font-weight: bold; border-radius: 10px; padding: 10px 18px;")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_profile)

        btn_edit = QPushButton("✏️ تعديل الزر")
        btn_edit.setStyleSheet("background: rgba(56,189,248,0.15); color: #38BDF8; font-weight: bold; border-radius: 10px; padding: 10px 18px; border: 1px solid rgba(56,189,248,0.4);")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_profile)

        btn_delete = QPushButton("🗑️ حذف الزر")
        btn_delete.setStyleSheet("background: rgba(239,68,68,0.15); color: #EF4444; font-weight: bold; border-radius: 10px; padding: 10px 18px; border: 1px solid rgba(239,68,68,0.4);")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self.delete_profile)

        btn_vbox.addWidget(btn_add)
        btn_vbox.addWidget(btn_edit)
        btn_vbox.addWidget(btn_delete)
        btn_vbox.addStretch()

        content_h.addWidget(self.list_profiles, 1)
        content_h.addLayout(btn_vbox)

        layout.addLayout(content_h)

        btn_close = QPushButton("إغلاق")
        btn_close.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border-radius: 10px; padding: 10px 22px;")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignRight)

        self.reload_list()

    def reload_list(self):
        self.list_profiles.clear()
        profiles = self.main_app.config.get("quick_launch_profiles", [])
        for p in profiles:
            app_cnt = len(p.get("apps", []))
            url_cnt = len(p.get("urls", []))
            item_str = f"{p.get('title', 'زر عمل')}   ({app_cnt} تطبيقات • {url_cnt} مواقع)"
            it = QListWidgetItem(item_str)
            it.setData(Qt.UserRole, p["id"])
            self.list_profiles.addItem(it)

    def add_profile(self):
        dlg = AddEditProfileDialog(parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.result_profile:
            if "quick_launch_profiles" not in self.main_app.config:
                self.main_app.config["quick_launch_profiles"] = []
            self.main_app.config["quick_launch_profiles"].append(dlg.result_profile)
            self.main_app.cfg_mgr.save_config()
            self.reload_list()

    def edit_profile(self):
        curr = self.list_profiles.currentItem()
        if not curr:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار زر لتعديله!")
            return
        p_id = curr.data(Qt.UserRole)
        profiles = self.main_app.config.get("quick_launch_profiles", [])
        p_obj = next((p for p in profiles if p["id"] == p_id), None)
        if p_obj:
            dlg = AddEditProfileDialog(profile=p_obj, parent=self)
            if dlg.exec() == QDialog.Accepted and dlg.result_profile:
                for idx, p in enumerate(profiles):
                    if p["id"] == p_id:
                        profiles[idx] = dlg.result_profile
                        break
                self.main_app.cfg_mgr.save_config()
                self.reload_list()

    def delete_profile(self):
        curr = self.list_profiles.currentItem()
        if not curr:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار زر لحذفه!")
            return
        p_id = curr.data(Qt.UserRole)
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل تريد حذف زر العمل السريع هذا؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_app.config["quick_launch_profiles"] = [p for p in self.main_app.config.get("quick_launch_profiles", []) if p["id"] != p_id]
            self.main_app.cfg_mgr.save_config()
            self.reload_list()


class LaunchProfilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.setWindowTitle("أزرار العمل السريع (Quick Launch)")
        self.setMinimumSize(640, 480)
        self.setStyleSheet("background-color: #0F172A; color: #F1F5F9; font-family: 'Segoe UI', sans-serif;")

        self.setup_ui()

    def setup_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr_row = QHBoxLayout()
        hdr_vb = QVBoxLayout()
        lbl_t = QLabel("🚀 أزرار بيئة العمل السريعة")
        lbl_t.setStyleSheet("font-size: 22px; font-weight: bold; color: #C084FC;")
        lbl_d = QLabel("اختر بيئة العمل التي تريد فتح تطبيقاتها ومواقعها الآن بضغطة واحدة:")
        lbl_d.setStyleSheet("color: #94A3B8; font-size: 13px;")
        hdr_vb.addWidget(lbl_t)
        hdr_vb.addWidget(lbl_d)
        hdr_row.addLayout(hdr_vb, 1)

        btn_manage = QPushButton("⚙️ ضبط وإدارة الأزرار")
        btn_manage.setStyleSheet("background: rgba(168,85,247,0.15); color: #C084FC; font-weight: bold; border-radius: 10px; padding: 8px 16px; border: 1px solid rgba(168,85,247,0.4);")
        btn_manage.setCursor(Qt.PointingHandCursor)
        btn_manage.clicked.connect(self.open_manage_dialog)
        hdr_row.addWidget(btn_manage)

        layout.addLayout(hdr_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_w = QWidget()
        scroll_w.setStyleSheet("background: transparent;")
        cards_vbox = QVBoxLayout(scroll_w)
        cards_vbox.setSpacing(12)
        cards_vbox.setContentsMargins(0, 0, 0, 0)

        profiles = self.main_app.config.get("quick_launch_profiles", [])
        if not profiles:
            empty_lbl = QLabel("لا توجد أزرار عمل سريع بعد.\nاضغط على زر '⚙️ ضبط وإدارة الأزرار' بالأعلى لإضافة أزرار جديدة!")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #64748B; font-size: 15px; padding: 40px;")
            cards_vbox.addWidget(empty_lbl)
        else:
            for prof in profiles:
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E1B4B, stop:1 #111827);
                        border: 1px solid rgba(168, 85, 247, 0.3);
                        border-radius: 16px;
                    }
                    QFrame:hover {
                        border-color: #C084FC;
                    }
                """)
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(20, 16, 20, 16)
                card_layout.setSpacing(16)

                info_vbox = QVBoxLayout()
                info_vbox.setSpacing(4)
                p_title = QLabel(prof.get("title", "بيئة عمل"))
                p_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
                
                app_c = len(prof.get("apps", []))
                url_c = len(prof.get("urls", []))
                p_sub = QLabel(f"💻 {app_c} تطبيقات • 🌐 {url_c} مواقع تعليمية وخاصة")
                p_sub.setStyleSheet("font-size: 13px; color: #94A3B8;")

                info_vbox.addWidget(p_title)
                info_vbox.addWidget(p_sub)

                btn_run = QPushButton("▶ تشغيل هذه البيئة 🚀")
                btn_run.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #7C3AED);
                        color: white; font-weight: bold; font-size: 14px;
                        border-radius: 10px; padding: 10px 22px; border: none;
                    }
                    QPushButton:hover { background: #A855F7; }
                """)
                btn_run.setCursor(Qt.PointingHandCursor)
                p_obj = prof
                btn_run.clicked.connect(lambda ch=False, pr=p_obj: self.run_profile(pr))

                card_layout.addLayout(info_vbox, 1)
                card_layout.addWidget(btn_run)

                cards_vbox.addWidget(card)

        scroll.setWidget(scroll_w)
        layout.addWidget(scroll)

    def open_manage_dialog(self):
        dlg = ManageQuickLaunchProfilesDialog(parent=self.main_app)
        dlg.exec()
        self.setup_ui()

    def run_profile(self, prof):
        self.accept()
        self.main_app.launch_profile_environment(prof)


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
        self.eye_rest_counter = 0
        self.study_motivate_counter = 0
        self.last_triggered_schedule_key = ""
        self.last_sunnah_key = ""

        # ✅ منع تكرار شاشات التذكير
        self._water_overlay_open = False
        self._pushups_overlay_open = False
        self._eye_rest_overlay_open = False
        self._schedule_overlay_open = False

        self.current_task_filter = "all"
        self.current_badge_filter = "all"
        self._prayer_overlay_open = False
        self.current_portfolio_folder_id = None

        self.setWindowTitle("انتاجيتي | مركز الإنتاجية الذكي")
        self.resize(1200, 820)
        self.setMinimumSize(1000, 700)

        self.setup_styles()
        self.setup_ui()
        self.update_streak_logic()
        self.setup_system_tray()
        self.setup_background_timers()

        # Initial button state check
        is_session_active = self.config.get("manual_session_active", False)
        self.app_blocker.is_active = is_session_active
        self.update_status_ui(is_session_active)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #060A12;
            }
            QWidget {
                color: #F1F5F9;
                font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
                font-size: 14px;
            }

            /* ═══ SIDEBAR ═══ */
            QFrame#Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0A1628, stop:0.5 #0D1B35, stop:1 #060A12);
                border-right: 1px solid rgba(56, 189, 248, 0.12);
            }

            /* ═══ NAV BUTTONS ═══ */
            QPushButton#NavBtn {
                background-color: transparent;
                color: #64748B;
                font-size: 15px;
                font-weight: bold;
                text-align: right;
                padding: 13px 16px;
                border-radius: 14px;
                border: none;
                margin: 1px 0;
            }
            QPushButton#NavBtn:hover {
                background: rgba(56, 189, 248, 0.08);
                color: #BAE6FD;
                border: 1px solid rgba(56, 189, 248, 0.2);
            }
            QPushButton#NavBtn[active="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(2, 132, 199, 0.35), stop:1 rgba(14, 165, 233, 0.15));
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                border-right: 3px solid #38BDF8;
            }

            /* ═══ CARDS ═══ */
            QFrame#Card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111C2E, stop:1 #0C1520);
                border: 1px solid rgba(56, 189, 248, 0.1);
                border-radius: 20px;
            }
            QFrame#Card:hover {
                border: 1px solid rgba(56, 189, 248, 0.25);
            }
            QFrame#GlowCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #131E32, stop:0.5 #0F1A2B, stop:1 #0A1220);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 24px;
            }
            QFrame#StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F1E30, stop:1 #091525);
                border: 1px solid rgba(56, 189, 248, 0.15);
                border-radius: 18px;
            }
            QFrame#DangerCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A0E10, stop:1 #0D0A0A);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 20px;
            }

            /* ═══ LABELS ═══ */
            QLabel#CardTitle {
                font-size: 20px;
                font-weight: bold;
                color: #38BDF8;
            }
            QLabel#PageTitle {
                font-size: 26px;
                font-weight: bold;
                color: #F1F5F9;
            }
            QLabel#SectionTitle {
                font-size: 18px;
                font-weight: bold;
                color: #E2E8F0;
            }
            QLabel#StatValue {
                font-size: 38px;
                font-weight: bold;
                color: #38BDF8;
            }
            QLabel#MutedText {
                color: #64748B;
                font-size: 13px;
            }

            /* ═══ PRIMARY BUTTONS ═══ */
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369A1, stop:1 #0284C7);
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 22px;
                border-radius: 14px;
                border: 1px solid rgba(56, 189, 248, 0.5);
            }
            QPushButton#PrimaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284C7, stop:1 #38BDF8);
                border-color: #38BDF8;
            }
            QPushButton#PrimaryBtn:pressed {
                background: #0369A1;
            }

            /* ═══ PRESET BUTTONS ═══ */
            QPushButton#PresetBtn {
                background: rgba(14, 165, 233, 0.08);
                border: 1px solid rgba(56, 189, 248, 0.3);
                color: #7DD3FC;
                font-size: 14px;
                font-weight: bold;
                padding: 11px 16px;
                border-radius: 14px;
            }
            QPushButton#PresetBtn:hover {
                background: rgba(14, 165, 233, 0.2);
                color: #E0F2FE;
                border-color: rgba(56, 189, 248, 0.6);
            }
            QPushButton#PresetBtn:pressed {
                background: rgba(2, 132, 199, 0.3);
            }

            /* ═══ FINISH/DANGER BUTTONS ═══ */
            QPushButton#FinishBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #991B1B, stop:1 #DC2626);
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 22px;
                border-radius: 14px;
                border: 1px solid rgba(239, 68, 68, 0.5);
            }
            QPushButton#FinishBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC2626, stop:1 #EF4444);
                border-color: #EF4444;
            }

            /* ═══ ICON TRASH BUTTON ═══ */
            QPushButton#IconTrashBtn {
                background-color: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 11px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }
            QPushButton#IconTrashBtn:hover {
                background-color: rgba(239, 68, 68, 0.3);
                border-color: #EF4444;
            }
            QPushButton#IconTrashBtn:pressed {
                background-color: #DC2626;
            }

            /* ═══ FILTER BUTTONS ═══ */
            QPushButton#FilterBtn {
                background-color: rgba(30, 41, 59, 0.6);
                color: #64748B;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 10px;
                border: 1px solid rgba(51, 65, 85, 0.6);
            }
            QPushButton#FilterBtn:hover {
                background-color: rgba(51, 65, 85, 0.8);
                color: #CBD5E1;
                border-color: #475569;
            }
            QPushButton#FilterBtn[active="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(2,132,199,0.4), stop:1 rgba(14,165,233,0.2));
                color: #38BDF8;
                border-color: rgba(56, 189, 248, 0.5);
            }

            /* ═══ LIST WIDGET ═══ */
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 4px;
                font-size: 15px;
                outline: none;
            }
            QListWidget::item {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111C2E, stop:1 #0C1520);
                border: 1px solid rgba(56, 189, 248, 0.08);
                border-radius: 14px;
                margin-bottom: 7px;
                padding: 2px;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #172035, stop:1 #101926);
                border: 1px solid rgba(56, 189, 248, 0.2);
            }
            QListWidget::item:selected {
                background: rgba(2, 132, 199, 0.15);
                border: 1px solid rgba(56, 189, 248, 0.35);
            }

            /* ═══ INPUT FIELDS ═══ */
            QLineEdit {
                background: rgba(10, 18, 32, 0.8);
                border: 1px solid rgba(56, 189, 248, 0.15);
                border-radius: 12px;
                padding: 11px 16px;
                color: #F1F5F9;
                font-size: 15px;
                selection-background-color: #0284C7;
            }
            QLineEdit:focus {
                border: 1px solid rgba(56, 189, 248, 0.5);
                background: rgba(14, 26, 46, 0.9);
            }
            QLineEdit:hover {
                border: 1px solid rgba(56, 189, 248, 0.3);
            }

            /* ═══ COMBO BOX ═══ */
            QComboBox {
                background: rgba(10, 18, 32, 0.8);
                border: 1px solid rgba(56, 189, 248, 0.15);
                border-radius: 12px;
                padding: 10px 14px;
                color: #F1F5F9;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: rgba(56, 189, 248, 0.3);
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #0D1B35;
                color: #E2E8F0;
                selection-background-color: #0284C7;
                border: 1px solid rgba(56, 189, 248, 0.2);
                border-radius: 8px;
                padding: 4px;
            }

            /* ═══ CHECKBOXES ═══ */
            QCheckBox {
                font-size: 15px;
                spacing: 10px;
                color: #CBD5E1;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 7px;
                border: 2px solid rgba(56, 189, 248, 0.25);
                background-color: rgba(10, 18, 32, 0.8);
            }
            QCheckBox::indicator:hover {
                border-color: rgba(56, 189, 248, 0.5);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0284C7, stop:1 #38BDF8);
                border-color: #38BDF8;
            }

            /* ═══ PROGRESS BARS ═══ */
            QProgressBar {
                background: rgba(10, 18, 32, 0.6);
                border: 1px solid rgba(56, 189, 248, 0.1);
                border-radius: 10px;
                height: 22px;
                text-align: center;
                color: #94A3B8;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284C7, stop:0.5 #0EA5E9, stop:1 #38BDF8);
                border-radius: 9px;
            }

            /* ═══ SCROLLBAR ═══ */
            QScrollBar:vertical {
                background: rgba(10, 18, 32, 0.4);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(56, 189, 248, 0.25);
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(56, 189, 248, 0.45);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:horizontal {
                background: rgba(10, 18, 32, 0.4);
                height: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(56, 189, 248, 0.25);
                border-radius: 3px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

    def _make_page_bg(self):
        """Creates a consistently styled page background widget."""
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        return w

    def setup_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #060A12;")
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── Sidebar ─────────────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 28, 16, 24)
        sidebar_layout.setSpacing(6)

        # Logo + App Name Header
        header_box = QHBoxLayout()
        header_box.setSpacing(10)

        logo_path = get_asset_path("logo.png")
        if logo_path and os.path.exists(logo_path):
            logo_lbl = QLabel()
            pix = QPixmap(logo_path).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            header_box.addWidget(logo_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(1)
        app_title = QLabel("انتاجيتي")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #38BDF8; letter-spacing: 0px;")
        app_sub = QLabel("Productivity Hub")
        app_sub.setStyleSheet("font-size: 11px; color: #334155; font-weight: 500;")
        title_vbox.addWidget(app_title)
        title_vbox.addWidget(app_sub)
        header_box.addLayout(title_vbox)
        header_box.addStretch()

        sidebar_layout.addLayout(header_box)
        sidebar_layout.addSpacing(20)

        # Divider
        div_line = QFrame()
        div_line.setFixedHeight(1)
        div_line.setStyleSheet("background: rgba(56, 189, 248, 0.1); margin: 0 4px;")
        sidebar_layout.addWidget(div_line)
        sidebar_layout.addSpacing(10)

        # Nav Section Label
        nav_section = QLabel("  القائمة الرئيسية")
        nav_section.setStyleSheet("color: #334155; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        sidebar_layout.addWidget(nav_section)
        sidebar_layout.addSpacing(4)

        self.btn_nav_dash = self.create_nav_button("الرئيسية", "homelogo.png", 0)
        self.btn_nav_tasks = self.create_nav_button("المهام اليومية", "bullseye-arrowlogo.png", 1)
        self.btn_nav_badge = self.create_nav_button("الأوسمة والرتب", "rocketlogo.png", 2)
        self.btn_nav_portfolio = self.create_nav_button("معرض الشهادات والإنجازات", "bullseye-arrowlogo.png", 7)
        self.btn_nav_sched = self.create_nav_button("جدول التعلم والمواعيد", "calendarlogo.png", 3)
        self.btn_nav_prayer = self.create_nav_button("مواعيد الصلاة", "clocklogo.png", 8)
        sidebar_layout.addWidget(self.btn_nav_dash)
        sidebar_layout.addWidget(self.btn_nav_tasks)
        sidebar_layout.addWidget(self.btn_nav_badge)
        sidebar_layout.addWidget(self.btn_nav_portfolio)
        sidebar_layout.addWidget(self.btn_nav_sched)
        sidebar_layout.addWidget(self.btn_nav_prayer)

        sidebar_layout.addSpacing(10)
        block_section = QLabel("  الحماية والتركيز")
        block_section.setStyleSheet("color: #334155; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        sidebar_layout.addWidget(block_section)
        sidebar_layout.addSpacing(4)

        self.btn_nav_block = self.create_nav_button("التطبيقات الممنوعة", "forbiddenapps.png", 4)
        self.btn_nav_web_block = self.create_nav_button("المواقع المحظورة", "forbiddenapps.png", 5)
        self.btn_nav_sets = self.create_nav_button("الإعدادات", "settingslogo.png", 6)
        sidebar_layout.addWidget(self.btn_nav_block)
        sidebar_layout.addWidget(self.btn_nav_web_block)
        sidebar_layout.addWidget(self.btn_nav_sets)

        sidebar_layout.addStretch()

        # Bottom version area
        bottom_div = QFrame()
        bottom_div.setFixedHeight(1)
        bottom_div.setStyleSheet("background: rgba(56, 189, 248, 0.08);")
        sidebar_layout.addWidget(bottom_div)
        sidebar_layout.addSpacing(10)

        ver_lbl = QLabel("⚡ الإصدار الأسطوري 6.0")
        ver_lbl.setStyleSheet("color: #1E3A5F; font-size: 12px; font-weight: bold;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(ver_lbl)

        self.btn_nav_dash.setProperty("active", "true")

        # ─── Content Area ─────────────────────────────────────────────────────
        content_widget = QWidget()
        content_widget.setStyleSheet("background: #060A12;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Stacked Pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")
        self.pages.addWidget(self.create_dashboard_page())
        self.pages.addWidget(self.create_tasks_page())
        self.pages.addWidget(self.create_analytics_page())
        self.pages.addWidget(self.create_schedules_page())
        self.pages.addWidget(self.create_blocked_apps_page())
        self.pages.addWidget(self.create_blocked_websites_page())
        self.pages.addWidget(self.create_settings_page())
        self.pages.addWidget(self.create_portfolio_page())
        self.pages.addWidget(self.create_prayer_times_page())

        content_layout.addWidget(self.pages)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_widget)

    def create_nav_button(self, text, icon_filename, page_index):
        btn = QPushButton(f"  {text}")
        btn.setObjectName("NavBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(46)
        btn._icon_filename = icon_filename
        color = "#38BDF8" if page_index == 0 else "#64748B"
        btn.setIcon(get_tinted_icon(icon_filename, color, QSize(20, 20)))
        btn.setIconSize(QSize(20, 20))
        btn.clicked.connect(lambda: self.switch_page(page_index))
        return btn

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        nav_btns = [self.btn_nav_dash, self.btn_nav_tasks, self.btn_nav_badge, self.btn_nav_sched, self.btn_nav_block, self.btn_nav_web_block, self.btn_nav_sets, self.btn_nav_portfolio, self.btn_nav_prayer]
        for i, btn in enumerate(nav_btns):
            is_active = (i == index)
            btn.setProperty("active", "true" if is_active else "false")
            btn.setStyle(btn.style())
            if hasattr(btn, '_icon_filename') and btn._icon_filename:
                color = "#38BDF8" if is_active else "#64748B"
                btn.setIcon(get_tinted_icon(btn._icon_filename, color, QSize(20, 20)))
            if hasattr(btn, '_icon_filename') and btn._icon_filename:
                color = "#38BDF8" if is_active else "#64748B"
                btn.setIcon(get_tinted_icon(btn._icon_filename, color, QSize(20, 20)))

    # Page 1: Dashboard
    def create_dashboard_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # ── Session Status Card (Hero) ──────────────────────────────────────
        self.status_card = QFrame()
        self.status_card.setMinimumHeight(110)
        self.status_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0B1929, stop:1 #0D1F33);
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-left: 4px solid #475569;
                border-radius: 18px;
            }
        """)

        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(24, 20, 24, 20)
        status_layout.setSpacing(20)

        # Left: indicator dot + text
        indicator_col = QVBoxLayout()
        indicator_col.setAlignment(Qt.AlignVCenter)
        self.lbl_status_dot = QLabel("⬤")
        self.lbl_status_dot.setStyleSheet("font-size: 18px; color: #475569;")
        indicator_col.addWidget(self.lbl_status_dot)
        status_layout.addLayout(indicator_col)

        status_info = QVBoxLayout()
        status_info.setSpacing(5)
        self.lbl_status_title = QLabel("حالة جلسة التعلم: غير نشطة")
        self.lbl_status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #94A3B8;")
        self.lbl_status_desc = QLabel("عند بدء التعلم، يتم حظر التطبيقات والمواقع الممنوعة تلقائياً لحمايتك من التشتت.")
        self.lbl_status_desc.setStyleSheet("font-size: 13px; color: #64748B;")
        self.lbl_status_desc.setWordWrap(True)
        status_info.addWidget(self.lbl_status_title)
        status_info.addWidget(self.lbl_status_desc)

        # Right: Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_start_learning = QPushButton("  بدء جلسة التعلم")
        self.btn_start_learning.setIcon(get_tinted_icon("playlogonotpauselogolikeinyoutube.png", "#FFFFFF", QSize(18, 18)))
        self.btn_start_learning.setIconSize(QSize(18, 18))
        self.btn_start_learning.setObjectName("PrimaryBtn")
        self.btn_start_learning.setCursor(Qt.PointingHandCursor)
        self.btn_start_learning.setMinimumWidth(170)
        self.btn_start_learning.clicked.connect(self.start_manual_session)

        self.btn_finish_learning = QPushButton("  إنهاء الجلسة")
        self.btn_finish_learning.setIcon(get_tinted_icon("pauselogo.png", "#FFFFFF", QSize(18, 18)))
        self.btn_finish_learning.setIconSize(QSize(18, 18))
        self.btn_finish_learning.setObjectName("FinishBtn")
        self.btn_finish_learning.setCursor(Qt.PointingHandCursor)
        self.btn_finish_learning.setMinimumWidth(155)
        self.btn_finish_learning.clicked.connect(self.finish_learning_session)

        btn_box.addWidget(self.btn_start_learning)
        btn_box.addWidget(self.btn_finish_learning)

        # Top Streak Header Badge
        self.card_top_streak = QFrame()
        self.card_top_streak.setCursor(Qt.PointingHandCursor)
        top_strk_l = QHBoxLayout(self.card_top_streak)
        top_strk_l.setContentsMargins(10, 6, 14, 6)
        top_strk_l.setSpacing(8)

        self.lbl_top_streak_icon = QLabel()
        self.lbl_top_streak_text = QLabel("0 يوم 🔥")
        self.lbl_top_streak_text.setStyleSheet("font-size: 14px; font-weight: 800; color: #FFFFFF;")

        top_strk_l.addWidget(self.lbl_top_streak_icon)
        top_strk_l.addWidget(self.lbl_top_streak_text)

        status_layout.addLayout(status_info, 1)
        status_layout.addLayout(btn_box)
        status_layout.addWidget(self.card_top_streak, alignment=Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.status_card)

        # ── Quick Launch Hero Bar ──────────────────────────────────────────
        ql_card = QFrame()
        ql_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E1B4B, stop:0.5 #311042, stop:1 #0F172A);
                border: 1px solid rgba(168, 85, 247, 0.3);
                border-radius: 16px;
                padding: 12px 20px;
            }
        """)
        ql_layout = QHBoxLayout(ql_card)
        ql_layout.setContentsMargins(16, 10, 16, 10)

        ql_info = QVBoxLayout()
        ql_info.setSpacing(2)
        ql_title = QLabel("🚀 تشغيل بيئة العمل السريعة (Quick Launch)")
        ql_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #C084FC;")
        ql_desc = QLabel("يشغّل تطبيقاتك المحددة ومواقعك التعليمية بضغطة زر واحدة ويبدأ التعلم فوراً!")
        ql_desc.setStyleSheet("font-size: 12px; color: #94A3B8;")
        ql_info.addWidget(ql_title)
        ql_info.addWidget(ql_desc)

        ql_btns = QHBoxLayout()
        ql_btns.setSpacing(8)

        btn_launch = QPushButton("🚀 بدء بيئة العمل السريعة")
        btn_launch.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #7C3AED);
                color: white; font-weight: bold; font-size: 13px;
                border-radius: 10px; padding: 10px 18px; border: none;
            }
            QPushButton:hover { background: #A855F7; }
        """)
        btn_launch.setCursor(Qt.PointingHandCursor)
        btn_launch.clicked.connect(self.trigger_quick_launch)

        btn_cfg_ql = QPushButton("⚙️ ضبط")
        btn_cfg_ql.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08); color: #E2E8F0; font-weight: bold;
                border-radius: 10px; padding: 10px 14px; border: 1px solid rgba(255,255,255,0.15);
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
        """)
        btn_cfg_ql.setCursor(Qt.PointingHandCursor)
        btn_cfg_ql.clicked.connect(self.manage_quick_launch_profiles)

        ql_btns.addWidget(btn_launch)
        ql_btns.addWidget(btn_cfg_ql)

        ql_layout.addLayout(ql_info, 1)
        ql_layout.addLayout(ql_btns)

        layout.addWidget(ql_card)

        # ── Stats Row ─────────────────────────────────────────────────────
        stats_header_lbl = QLabel("📊 إحصائيات اليوم")
        stats_header_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #64748B; letter-spacing: 0px;")
        layout.addWidget(stats_header_lbl)

        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(14)

        def make_stat_card(emoji, title, value_lbl_attr, value_text, color, icon_file):
            card = QFrame()
            card.setObjectName("StatCard")
            card.setStyleSheet(f"""
                QFrame#StatCard {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0F1E30, stop:1 #091220);
                    border: 1px solid {color}25;
                    border-top: 3px solid {color};
                    border-radius: 18px;
                }}
            """)
            card_l = QVBoxLayout(card)
            card_l.setContentsMargins(20, 18, 20, 18)
            card_l.setSpacing(8)

            top_row = QHBoxLayout()
            top_row.setSpacing(10)
            ic_lbl = QLabel()
            pix = get_tinted_pixmap(icon_file, color, QSize(26, 26))
            ic_lbl.setPixmap(pix)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"font-size: 13px; color: #64748B; font-weight: 600;")
            top_row.addWidget(ic_lbl)
            top_row.addWidget(title_lbl)
            top_row.addStretch()
            card_l.addLayout(top_row)

            val_lbl = QLabel(value_text)
            val_lbl.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
            setattr(self, value_lbl_attr, val_lbl)
            card_l.addWidget(val_lbl)
            return card

        water_count = self.config['daily_stats']['water_count']
        push_count = self.config['daily_stats']['pushups_count']
        learn_mins = self.config['daily_stats']['learning_minutes']

        card_water = make_stat_card("💧", "شرب الماء اليومي", "lbl_stat_water", f"{water_count} أكواب", "#38BDF8", "waterlogo.png")
        card_pushups = make_stat_card("🏋️", "تمارين اليوم", "lbl_stat_pushups", f"{push_count} ضغطات", "#FB923C", "gymlogo.png")
        card_session = make_stat_card("⏱️", "وقت التعلم اليوم", "lbl_stat_time", f"{learn_mins} دقيقة", "#10B981", "clocklogo.png")

        # Streak Stat Card
        card_streak = QFrame()
        card_streak.setObjectName("StatCard")
        card_streak.setStyleSheet("""
            QFrame#StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1F140E, stop:1 #110B07);
                border: 1px solid rgba(249, 115, 22, 0.25);
                border-top: 3px solid #F97316;
                border-radius: 18px;
            }
        """)
        c_streak_l = QVBoxLayout(card_streak)
        c_streak_l.setContentsMargins(20, 18, 20, 18)
        c_streak_l.setSpacing(8)

        st_top_row = QHBoxLayout()
        st_top_row.setSpacing(10)

        self.lbl_streak_icon = QLabel()
        st_title_lbl = QLabel("الستريك والتتابع")
        st_title_lbl.setStyleSheet("font-size: 13px; color: #94A3B8; font-weight: 600;")
        st_top_row.addWidget(self.lbl_streak_icon)
        st_top_row.addWidget(st_title_lbl)
        st_top_row.addStretch()
        c_streak_l.addLayout(st_top_row)

        self.lbl_streak_val = QLabel("0 أيام")
        self.lbl_streak_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #F8FAFC;")
        c_streak_l.addWidget(self.lbl_streak_val)

        self.lbl_streak_freezes = QLabel("🛡️ 3/3 إنقاذات متبقية")
        self.lbl_streak_freezes.setStyleSheet("font-size: 12px; color: #F59E0B; font-weight: bold;")
        c_streak_l.addWidget(self.lbl_streak_freezes)

        stats_grid.addWidget(card_water)
        stats_grid.addWidget(card_pushups)
        stats_grid.addWidget(card_session)
        stats_grid.addWidget(card_streak)
        layout.addLayout(stats_grid)

        # ── Next Reminders & Timers Card ───────────────────────────────────
        self.card_next_timers = QFrame()
        self.card_next_timers.setObjectName("TimersCard")
        self.card_next_timers.setStyleSheet("""
            QFrame#TimersCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0B192E, stop:1 #0F172A);
                border: 1px solid rgba(56, 189, 248, 0.15);
                border-radius: 20px;
            }
        """)
        timers_card_l = QVBoxLayout(self.card_next_timers)
        timers_card_l.setContentsMargins(20, 16, 20, 16)
        timers_card_l.setSpacing(12)

        timers_head = QHBoxLayout()
        lbl_timers_title = QLabel("⏳ المواعيد والتذكيرات القادمة")
        lbl_timers_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #E2E8F0;")
        timers_head.addWidget(lbl_timers_title)
        timers_head.addStretch()
        timers_card_l.addLayout(timers_head)

        timers_row = QHBoxLayout()
        timers_row.setSpacing(12)

        def make_timer_box(emoji, title, attr_name, accent_color):
            box = QFrame()
            box.setStyleSheet(f"""
                QFrame {{
                    background: rgba(15, 23, 42, 0.6);
                    border: 1px solid {accent_color}30;
                    border-radius: 14px;
                }}
            """)
            bl = QVBoxLayout(box)
            bl.setSpacing(4)
            bl.setContentsMargins(14, 10, 14, 10)
            
            h_lbl = QLabel(f"{emoji} {title}")
            h_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {accent_color};")
            
            val_lbl = QLabel("جاري الحساب...")
            val_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #F8FAFC;")
            setattr(self, attr_name, val_lbl)

            bl.addWidget(h_lbl)
            bl.addWidget(val_lbl)
            return box

        self.box_timer_eye = make_timer_box("👁️", "راحة العينين", "lbl_timer_eye", "#06B6D4")
        self.box_timer_pushups = make_timer_box("🏋️", "التمرين الرياضي", "lbl_timer_pushups", "#FB923C")
        self.box_timer_water = make_timer_box("💧", "شرب الماء", "lbl_timer_water", "#38BDF8")

        timers_row.addWidget(self.box_timer_eye)
        timers_row.addWidget(self.box_timer_pushups)
        timers_row.addWidget(self.box_timer_water)

        timers_card_l.addLayout(timers_row)
        layout.addWidget(self.card_next_timers)
        self.update_dashboard_timers()

        # ── Tasks Compact Card ──────────────────────────────────────────────
        card_tasks = QFrame()
        card_tasks.setObjectName("Card")
        card_tasks.setStyleSheet("""
            QFrame#Card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111C2E, stop:1 #0C1520);
                border: 1px solid rgba(56, 189, 248, 0.1);
                border-radius: 20px;
            }
        """)
        tasks_layout = QVBoxLayout(card_tasks)
        tasks_layout.setContentsMargins(22, 18, 22, 18)
        tasks_layout.setSpacing(12)

        # Header Row
        tasks_header = QHBoxLayout()
        lbl_tasks_title = QLabel("📋 قائمة المهام اليومية")
        lbl_tasks_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #E2E8F0;")

        self.lbl_task_progress = QLabel("إنجاز: 0%")
        self.lbl_task_progress.setStyleSheet("font-size: 14px; font-weight: bold; color: #10B981;")

        # Filter Buttons
        filter_box = QHBoxLayout()
        filter_box.setSpacing(6)
        self.btn_filter_all = QPushButton("الكل")
        self.btn_filter_active = QPushButton("نشطة ⏳")
        self.btn_filter_completed = QPushButton("مكتملة ✅")

        for b, f_val in [(self.btn_filter_all, "all"), (self.btn_filter_active, "active"), (self.btn_filter_completed, "completed")]:
            b.setObjectName("FilterBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda ch, val=f_val: self.set_task_filter(val))

        filter_box.addWidget(self.btn_filter_all)
        filter_box.addWidget(self.btn_filter_active)
        filter_box.addWidget(self.btn_filter_completed)

        tasks_header.addWidget(lbl_tasks_title)
        tasks_header.addSpacing(12)
        tasks_header.addLayout(filter_box)
        tasks_header.addStretch()
        tasks_header.addWidget(self.lbl_task_progress)
        tasks_layout.addLayout(tasks_header)

        # Progress Bar
        self.task_progress_bar = QProgressBar()
        self.task_progress_bar.setRange(0, 100)
        self.task_progress_bar.setValue(0)
        self.task_progress_bar.setFixedHeight(8)
        self.task_progress_bar.setTextVisible(False)
        self.task_progress_bar.setStyleSheet("""
            QProgressBar { background: rgba(30, 41, 59, 0.8); border: none; border-radius: 4px; }
            QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0284C7, stop:1 #10B981); border-radius: 4px; }
        """)
        tasks_layout.addWidget(self.task_progress_bar)

        # Add Task Input Row
        add_task_box = QHBoxLayout()
        add_task_box.setSpacing(10)
        self.txt_task_input = QLineEdit()
        self.txt_task_input.setPlaceholderText("✏️  أضف مهمة جديدة هنا...")
        self.txt_task_input.returnPressed.connect(self.add_task)

        btn_add_task = QPushButton("➕ إضافة")
        btn_add_task.setObjectName("PrimaryBtn")
        btn_add_task.setCursor(Qt.PointingHandCursor)
        btn_add_task.clicked.connect(self.add_task)

        add_task_box.addWidget(self.txt_task_input, 1)
        add_task_box.addWidget(btn_add_task, 0)
        tasks_layout.addLayout(add_task_box)

        # List Widget for Tasks
        self.list_tasks = QListWidget()
        self.list_tasks.setMinimumHeight(160)
        self.list_tasks.setMaximumHeight(240)
        tasks_layout.addWidget(self.list_tasks)

        layout.addWidget(card_tasks)
        self.reload_tasks_list()

        return page

    # Page 1.5: Dedicated Tasks Page
    def create_tasks_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── Page Header ─────────────────────────────────────────────────────
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0A1628, stop:1 #0E1F3A);
                border: 1px solid rgba(56, 189, 248, 0.12);
                border-radius: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(4)
        title = QLabel("✅ المهام اليومية")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #F1F5F9;")
        desc = QLabel("نظّم مهامك، تابع تقدمك، واستمتع بيوم إنتاجي مليء بالإنجاز بدون مشتتات.")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vbox.addWidget(title)
        title_vbox.addWidget(desc)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addWidget(header_card)

        # ── Overview Stats Row ───────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        def make_mini_stat(emoji, lbl_text, attr_name, color):
            c = QFrame()
            c.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0F1E30, stop:1 #091220);
                    border: 1px solid {color}25;
                    border-top: 3px solid {color};
                    border-radius: 16px;
                }}
            """)
            cl = QVBoxLayout(c)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(6)
            top = QLabel(f"{emoji} {lbl_text}")
            top.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600;")
            val = QLabel("0")
            val.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
            setattr(self, attr_name, val)
            cl.addWidget(top)
            cl.addWidget(val)
            return c

        stats_row.addWidget(make_mini_stat("📦", "إجمالي المهام", "lbl_task_stat_total", "#38BDF8"))
        stats_row.addWidget(make_mini_stat("⏳", "قيد الانتظار", "lbl_task_stat_pending", "#FB923C"))
        stats_row.addWidget(make_mini_stat("✅", "مكتملة اليوم", "lbl_task_stat_done", "#10B981"))
        layout.addLayout(stats_row)

        # ── Progress Bar ─────────────────────────────────────────────────────
        prog_card = QFrame()
        prog_card.setObjectName("Card")
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.setContentsMargins(20, 14, 20, 14)
        prog_layout.setSpacing(8)

        pb_header = QHBoxLayout()
        lbl_pb_title = QLabel("🎯 مؤشر إنجاز اليوم")
        lbl_pb_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #E2E8F0;")
        self.lbl_task_page_percent = QLabel("0%")
        self.lbl_task_page_percent.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")
        pb_header.addWidget(lbl_pb_title)
        pb_header.addStretch()
        pb_header.addWidget(self.lbl_task_page_percent)
        prog_layout.addLayout(pb_header)

        self.task_page_progress_bar = QProgressBar()
        self.task_page_progress_bar.setRange(0, 100)
        self.task_page_progress_bar.setValue(0)
        self.task_page_progress_bar.setFixedHeight(12)
        self.task_page_progress_bar.setTextVisible(False)
        self.task_page_progress_bar.setStyleSheet("""
            QProgressBar { background: rgba(30,41,59,0.8); border: none; border-radius: 6px; }
            QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0284C7, stop:1 #10B981); border-radius: 6px; }
        """)
        prog_layout.addWidget(self.task_page_progress_bar)
        layout.addWidget(prog_card)

        # ── Add Task Input ────────────────────────────────────────────────────
        add_card = QFrame()
        add_card.setObjectName("Card")
        add_layout = QHBoxLayout(add_card)
        add_layout.setContentsMargins(18, 14, 18, 14)
        add_layout.setSpacing(12)

        self.txt_task_page_input = QLineEdit()
        self.txt_task_page_input.setPlaceholderText("✏️  أكتب المهمة الجديدة هنا (مثال: مراجعة 30 دقيقة رياضيات)...")
        self.txt_task_page_input.returnPressed.connect(self.add_task_from_page)

        btn_add = QPushButton("➕ إضافة المهمة")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_task_from_page)

        add_layout.addWidget(self.txt_task_page_input, 1)
        add_layout.addWidget(btn_add)
        layout.addWidget(add_card)

        # ── Filter Buttons ────────────────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        lbl_list_title = QLabel("قائمة المهام:")
        lbl_list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #94A3B8;")
        filter_row.addWidget(lbl_list_title)
        filter_row.addSpacing(10)

        self.btn_filter_page_all = QPushButton("الكل")
        self.btn_filter_page_active = QPushButton("نشطة ⏳")
        self.btn_filter_page_completed = QPushButton("مكتملة ✅")

        for b, f_val in [(self.btn_filter_page_all, "all"), (self.btn_filter_page_active, "active"), (self.btn_filter_page_completed, "completed")]:
            b.setObjectName("FilterBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda ch, val=f_val: self.set_task_filter(val))
            filter_row.addWidget(b)

        filter_row.addStretch()
        layout.addLayout(filter_row)

        # ── Large Spacious Task List ──────────────────────────────────────────
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
        hdr_card = QFrame()
        hdr_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D1A30, stop:1 #0A1220);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 18px;
            }
        """)
        hdr_row = QHBoxLayout(hdr_card)
        hdr_row.setContentsMargins(22, 16, 22, 16)
        title_vbox2 = QVBoxLayout()
        title_vbox2.setSpacing(4)
        title = QLabel("🏆 مركز الإنجاز والأوسمة")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #F1F5F9;")
        desc = QLabel("تابع رانكك، نقاطك، وأوسمة إنجازك. كل عمل صغير يصنع فرقاً كبيراً! 🚀")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vbox2.addWidget(title)
        title_vbox2.addWidget(desc)
        hdr_row.addLayout(title_vbox2)
        hdr_row.addStretch()
        layout.addWidget(hdr_card)

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

    # Page 2: Schedules
    def create_schedules_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header card
        hdr = QFrame()
        hdr.setStyleSheet("QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0A1628,stop:1 #0E1F3A); border: 1px solid rgba(56,189,248,0.12); border-radius: 18px; }")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(22, 14, 22, 14)
        title_vb = QVBoxLayout()
        title_vb.setSpacing(3)
        title = QLabel("📅 جدول مواعيد التعلم")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1F5F9;")
        sub = QLabel("ضبط مواعيد جلسات التعلم التلقائية ومتابعة الجداول اليومية")
        sub.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vb.addWidget(title)
        title_vb.addWidget(sub)
        hdr_layout.addLayout(title_vb)
        hdr_layout.addStretch()
        layout.addWidget(hdr)

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

        self.cmb_sched_type = QComboBox()
        self.cmb_sched_type.addItems([
            "تعلم عادي ⏱️",
            "تعلم صارم إجباري 🔒",
            "تذكير بموعد فقط 🔔"
        ])

        btn_add_sched = QPushButton("➕ إضافة موعد")
        btn_add_sched.setObjectName("PrimaryBtn")
        btn_add_sched.setCursor(Qt.PointingHandCursor)
        btn_add_sched.clicked.connect(self.add_schedule_custom)

        row_inputs.addWidget(self.txt_sched_name, 2)
        row_inputs.addWidget(QLabel(" نوع الموعد:"))
        row_inputs.addWidget(self.cmb_sched_type)
        row_inputs.addWidget(QLabel("وقت الموعد / من:"))
        row_inputs.addWidget(self.cmb_start_hour)
        row_inputs.addWidget(QLabel(":"))
        row_inputs.addWidget(self.cmb_start_min)
        row_inputs.addWidget(self.cmb_start_period)
        
        self.lbl_to_text = QLabel(" إلى:")
        row_inputs.addWidget(self.lbl_to_text)
        row_inputs.addWidget(self.cmb_end_hour)
        row_inputs.addWidget(QLabel(":"))
        row_inputs.addWidget(self.cmb_end_min)
        row_inputs.addWidget(self.cmb_end_period)

        def toggle_end_time_visibility(idx):
            is_reminder = (idx == 2)  # "تذكير بموعد فقط 🔔"
            self.lbl_to_text.setVisible(not is_reminder)
            self.cmb_end_hour.setVisible(not is_reminder)
            self.cmb_end_min.setVisible(not is_reminder)
            self.cmb_end_period.setVisible(not is_reminder)

        self.cmb_sched_type.currentIndexChanged.connect(toggle_end_time_visibility)

        row_inputs.addWidget(btn_add_sched, 1)

        add_vbox.addLayout(row_inputs)
        layout.addWidget(add_box)

        return page

    # Page 3: Blocked Apps
    def create_blocked_apps_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        hdr = QFrame()
        hdr.setStyleSheet("QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1A0A12,stop:1 #0D1220); border: 1px solid rgba(239,68,68,0.2); border-radius: 18px; }")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(22, 14, 22, 14)
        title_vb = QVBoxLayout()
        title_vb.setSpacing(3)
        title = QLabel("🚫 التطبيقات الممنوعة")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1F5F9;")
        desc = QLabel("أثناء جلسة التعلم النشطة، سيمنع التطبيق البرامج المحددة للقضاء على التشتت.")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vb.addWidget(title)
        title_vb.addWidget(desc)
        hdr_layout.addLayout(title_vb)
        hdr_layout.addStretch()
        layout.addWidget(hdr)

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
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        hdr = QFrame()
        hdr.setStyleSheet("QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0A1228,stop:1 #0D1A30); border: 1px solid rgba(56,189,248,0.15); border-radius: 18px; }")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(22, 14, 22, 14)
        title_vb = QVBoxLayout()
        title_vb.setSpacing(3)
        title = QLabel("🌐 المواقع المحظورة")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1F5F9;")
        desc = QLabel("أثناء تفعيل وقت التعلم، سيتم حظر الوصول لهذه المواقع لمنع التشتت وزيادة الإنتاجية.")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vb.addWidget(title)
        title_vb.addWidget(desc)
        hdr_layout.addLayout(title_vb)
        hdr_layout.addStretch()
        layout.addWidget(hdr)

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
        page.setStyleSheet("background: transparent;")

        # Make it scrollable
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        scroll.setWidget(scroll_widget)
        page_layout.addWidget(scroll)

        # ── Header Card ────────────────────────────────────────────────────
        hdr = QFrame()
        hdr.setStyleSheet("QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0A1220,stop:1 #0D1A2E); border: 1px solid rgba(56,189,248,0.12); border-radius: 18px; }")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(22, 14, 22, 14)
        title_vb = QVBoxLayout()
        title_vb.setSpacing(3)
        title = QLabel("⚙️ الإعدادات والتجربة")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1F5F9;")
        sub = QLabel("ضبط خيارات التطبيق واختبار شاشات التذكير الصحية")
        sub.setStyleSheet("color: #64748B; font-size: 13px;")
        title_vb.addWidget(title)
        title_vb.addWidget(sub)
        hdr_layout.addLayout(title_vb)
        hdr_layout.addStretch()
        layout.addWidget(hdr)

        # ── General Options Card ────────────────────────────────────────────
        opts_card = QFrame()
        opts_card.setObjectName("Card")
        opts_layout = QVBoxLayout(opts_card)
        opts_layout.setContentsMargins(22, 18, 22, 18)
        opts_layout.setSpacing(14)

        opts_lbl = QLabel("🔧 الخيارات العامة")
        opts_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        opts_layout.addWidget(opts_lbl)

        self.chk_startup = QCheckBox("🚀 التشغيل التلقائي مع إقلاع الجهاز (Windows Startup)")
        self.chk_startup.setChecked(self.cfg_mgr.is_startup_enabled())
        self.chk_startup.toggled.connect(self.toggle_startup)

        self.chk_sound = QCheckBox("🔔 تفعيل الأصوات والتنبيهات الصوتية المتكررة")
        self.chk_sound.setChecked(self.config.get("sound_enabled", True))
        self.chk_sound.toggled.connect(self.toggle_sound)

        self.chk_water_enabled = QCheckBox("💧 تفعيل تذكير شرب الماء الدوري")
        self.chk_water_enabled.setChecked(self.config.get("water_enabled", True))
        self.chk_water_enabled.toggled.connect(self.toggle_water_reminders)

        self.chk_pushups_enabled = QCheckBox("🏋️ تفعيل تذكير تمارين البوش أب والتمارين الرياضية")
        self.chk_pushups_enabled.setChecked(self.config.get("pushups_enabled", True))
        self.chk_pushups_enabled.toggled.connect(self.toggle_pushups_reminders)

        self.chk_eye_rest_enabled = QCheckBox("👀 تفعيل استراحة العينين والبدن (كل 20 دقيقة تنبيه 20 ثانية - قاعدة 20-20-20)")
        self.chk_eye_rest_enabled.setChecked(self.config.get("eye_rest_enabled", True))
        self.chk_eye_rest_enabled.toggled.connect(self.toggle_eye_rest_reminders)

        btn_manage_ql_settings = QPushButton("⚙️ إدارة وتعديل أزرار العمل السريع (Quick Launch Profiles)")
        btn_manage_ql_settings.setStyleSheet("background: rgba(168, 85, 247, 0.15); color: #C084FC; font-weight: bold; border-radius: 10px; padding: 10px 16px; border: 1px solid rgba(168, 85, 247, 0.4);")
        btn_manage_ql_settings.setCursor(Qt.PointingHandCursor)
        btn_manage_ql_settings.clicked.connect(self.manage_quick_launch_profiles)

        opts_layout.addWidget(self.chk_startup)
        opts_layout.addWidget(self.chk_sound)
        opts_layout.addWidget(self.chk_water_enabled)
        opts_layout.addWidget(self.chk_pushups_enabled)
        opts_layout.addWidget(self.chk_eye_rest_enabled)
        opts_layout.addWidget(btn_manage_ql_settings)
        layout.addWidget(opts_card)

        # ── Interval Settings Card ──────────────────────────────────────────
        interval_card = QFrame()
        interval_card.setObjectName("Card")
        interval_layout = QVBoxLayout(interval_card)
        interval_layout.setContentsMargins(22, 18, 22, 18)
        interval_layout.setSpacing(14)

        interval_title = QLabel("⏱️ تكرار التذكيرات الصحية")
        interval_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        interval_layout.addWidget(interval_title)

        interval_row = QHBoxLayout()
        interval_row.setSpacing(20)

        water_box = QVBoxLayout()
        water_box.setSpacing(6)
        wl = QLabel("💧 تذكير شرب الماء:")
        wl.setStyleSheet("font-size: 14px; color: #CBD5E1;")
        water_box.addWidget(wl)
        self.cmb_water_interval = QComboBox()
        for m in [15, 20, 30, 40, 50, 60, 90]:
            self.cmb_water_interval.addItem(f"كل {m} دقيقة", m)
        curr_w = self.config.get("water_interval_min", 40)
        idx_w = self.cmb_water_interval.findData(curr_w)
        if idx_w != -1:
            self.cmb_water_interval.setCurrentIndex(idx_w)
        self.cmb_water_interval.currentIndexChanged.connect(self.change_water_interval)
        water_box.addWidget(self.cmb_water_interval)

        pushups_box = QVBoxLayout()
        pushups_box.setSpacing(6)
        pl = QLabel("🏋️ تذكير تمارين الرياضة:")
        pl.setStyleSheet("font-size: 14px; color: #CBD5E1;")
        pushups_box.addWidget(pl)
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

        # ── Test Center Card ────────────────────────────────────────────────
        test_card = QFrame()
        test_card.setObjectName("Card")
        test_layout = QVBoxLayout(test_card)
        test_layout.setContentsMargins(22, 18, 22, 18)
        test_layout.setSpacing(14)

        test_title = QLabel("🎯 تجربة شاشات التنبيه")
        test_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        test_desc = QLabel("اختبر شاشات التذكير الصحية مباشرةً من هنا.")
        test_desc.setStyleSheet("color: #64748B; font-size: 13px;")

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        btn_test_water = QPushButton("💧 تجربة شاشة شرب الماء")
        btn_test_water.setObjectName("PrimaryBtn")
        btn_test_water.setCursor(Qt.PointingHandCursor)
        btn_test_water.clicked.connect(self.test_water_overlay)

        btn_test_pushups = QPushButton("🏋️ تجربة تمرين رياضي")
        btn_test_pushups.setObjectName("PrimaryBtn")
        btn_test_pushups.setStyleSheet("""
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #C2410C,stop:1 #EA580C);
                border-color: #F97316;
            }
            QPushButton#PrimaryBtn:hover { background: #EA580C; }
        """)
        btn_test_pushups.setCursor(Qt.PointingHandCursor)
        btn_test_pushups.clicked.connect(self.test_pushups_overlay)

        btn_test_eye = QPushButton("👀 تجربة استراحة العينين (20ث)")
        btn_test_eye.setObjectName("PrimaryBtn")
        btn_test_eye.setStyleSheet("""
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0284C7,stop:1 #38BDF8);
                border-color: #38BDF8;
            }
            QPushButton#PrimaryBtn:hover { background: #0284C7; }
        """)
        btn_test_eye.setCursor(Qt.PointingHandCursor)
        btn_test_eye.clicked.connect(self.test_eye_rest_overlay)

        btn_box.addWidget(btn_test_water)
        btn_box.addWidget(btn_test_pushups)
        btn_box.addWidget(btn_test_eye)

        test_layout.addWidget(test_title)
        test_layout.addWidget(test_desc)
        test_layout.addLayout(btn_box)
        layout.addWidget(test_card)

        # ── Reset Progress (Danger Zone) ────────────────────────────────────
        reset_card = QFrame()
        reset_card.setObjectName("DangerCard")
        reset_layout = QVBoxLayout(reset_card)
        reset_layout.setContentsMargins(22, 18, 22, 18)
        reset_layout.setSpacing(10)

        danger_hdr = QHBoxLayout()
        danger_icon = QLabel("⚠️")
        danger_icon.setStyleSheet("font-size: 20px;")
        reset_title = QLabel("منطقة الخطر — إعادة تعيين التقدم")
        reset_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #EF4444;")
        danger_hdr.addWidget(danger_icon)
        danger_hdr.addWidget(reset_title)
        danger_hdr.addStretch()
        reset_layout.addLayout(danger_hdr)

        reset_desc = QLabel("تصفير كافة النقاط، الأوسمة، وإحصائيات التقدم والبدء من جديد من رانك 'مبتدئ أول'. لا يمكن التراجع عن هذا الإجراء.")
        reset_desc.setStyleSheet("color: #64748B; font-size: 13px;")
        reset_desc.setWordWrap(True)
        reset_layout.addWidget(reset_desc)

        btn_reset_progress = QPushButton("🔄 إعادة تعيين كل التقدم والنقاط")
        btn_reset_progress.setObjectName("FinishBtn")
        btn_reset_progress.setCursor(Qt.PointingHandCursor)
        btn_reset_progress.clicked.connect(self.reset_user_progress)
        reset_layout.addWidget(btn_reset_progress)

        layout.addWidget(reset_card)
        layout.addStretch()
        return page

    # Reload Schedules List
    def reload_schedules_list(self):
        self.list_schedules.clear()
        trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(22, 22))
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
            st_type = item.get('type', 'standard')

            lbl_name = QLabel(item['name'])
            lbl_name.setStyleSheet("font-size: 17px; font-weight: bold; color: #F8FAFC;")
            lbl_name.setWordWrap(True)
            lbl_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            if st_type == 'reminder':
                lbl_time = QLabel(f"🔔 التنبيه: {start_12}")
                lbl_time.setStyleSheet("font-size: 14px; color: #F59E0B; font-weight: bold;")
                row_widget.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #261D09, stop:1 #140E04); border-right: 4px solid #F59E0B; border-radius: 12px;")
                badge_text = "🔔 تذكير فقط"
                badge_style = "background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.4); font-size: 12px; font-weight: bold; border-radius: 8px; padding: 4px 10px;"
            elif st_type == 'strict':
                lbl_time = QLabel(f"🔒 من {start_12} إلى {end_12}")
                lbl_time.setStyleSheet("font-size: 14px; color: #EF4444; font-weight: bold;")
                row_widget.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2B0D11, stop:1 #140507); border-right: 4px solid #EF4444; border-radius: 12px;")
                badge_text = "🔒 صارم إجباري"
                badge_style = "background: rgba(239,68,68,0.15); color: #EF4444; border: 1px solid rgba(239,68,68,0.4); font-size: 12px; font-weight: bold; border-radius: 8px; padding: 4px 10px;"
            else:
                lbl_time = QLabel(f"⏱️ من {start_12} إلى {end_12}")
                lbl_time.setStyleSheet("font-size: 14px; color: #38BDF8; font-weight: bold;")
                row_widget.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0A1628, stop:1 #060A12); border-right: 4px solid #38BDF8; border-radius: 12px;")
                badge_text = "⏱️ تعلم عادي"
                badge_style = "background: rgba(56,189,248,0.15); color: #38BDF8; border: 1px solid rgba(56,189,248,0.4); font-size: 12px; font-weight: bold; border-radius: 8px; padding: 4px 10px;"

            lbl_badge = QLabel(badge_text)
            lbl_badge.setStyleSheet(badge_style)

            text_vbox = QVBoxLayout()
            text_vbox.setSpacing(4)
            text_vbox.addWidget(lbl_name)
            text_vbox.addWidget(lbl_time)
            text_vbox.addWidget(lbl_badge)

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

        st_text = self.cmb_sched_type.currentText()
        if "صارم" in st_text:
            st_type = "strict"
        elif "تذكير" in st_text:
            st_type = "reminder"
        else:
            st_type = "standard"

        self.config["learning_schedules"].append({
            "name": name, "start": start_str, "end": end_str, "active": True, "type": st_type
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
        trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(22, 22))

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

        trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(22, 22))

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

            trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(22 if is_spacious else 20, 22 if is_spacious else 20))

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
        if self.config.get("manual_session_is_strict", False):
            QMessageBox.warning(
                self,
                "🔒 وضع التعلم الصارم مفعّل",
                "أنت في وضع التعلم الصارم الإجباري!\nلا يمكنك إنهاء الجلسة يدوياً حتى تنتهي الفترة المحددة."
            )
            return

        self.app_blocker.is_active = False
        self.config["manual_session_active"] = False
        self.config["manual_session_is_strict"] = False
        self.cfg_mgr.save_config()
        self.update_status_ui(False)
        self.record_streak_activity()

    def update_status_ui(self, active: bool):
        is_strict = self.config.get("manual_session_is_strict", False)
        if active:
            self.status_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #071E10, stop:1 #0A2618);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-left: 4px solid #10B981;
                    border-radius: 18px;
                }
            """)
            self.lbl_status_dot.setStyleSheet("font-size: 18px; color: #10B981;")
            if is_strict:
                self.lbl_status_title.setText("🔒 جلسة تعلم صارمة إجبارية — الحظر مفعّل مغلق")
                self.lbl_status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F59E0B;")
                self.lbl_status_desc.setText("أنت الآن في وضع التعلم الصارم! لا يمكنك إيقاف الجلسة حتى ينتهي وقتها لضمان تركيزك التام.")
                self.btn_finish_learning.setEnabled(False)
                self.btn_finish_learning.setToolTip("🔒 وضع التعلم الصارم مفعّل — لا يمكنك إنهاء الجلسة!")
            else:
                self.lbl_status_title.setText("⚡ جلسة التعلم نشطة — الحظر مفعّل")
                self.lbl_status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #34D399;")
                self.lbl_status_desc.setText("يتم حظر جميع التطبيقات والمواقع الممنوعة حالياً لزيادة إنتاجيتك!")
                self.btn_finish_learning.setEnabled(True)
                self.btn_finish_learning.setToolTip("")

            self.lbl_status_desc.setStyleSheet("font-size: 13px; color: #6EE7B7;")
            self.btn_start_learning.setVisible(False)
            self.btn_finish_learning.setVisible(True)
        else:
            self.status_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0B1929, stop:1 #0D1F33);
                    border: 1px solid rgba(100, 116, 139, 0.3);
                    border-left: 4px solid #475569;
                    border-radius: 18px;
                }
            """)
            self.lbl_status_dot.setStyleSheet("font-size: 18px; color: #475569;")
            self.lbl_status_title.setText("حالة جلسة التعلم: غير نشطة")
            self.lbl_status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #94A3B8;")
            self.lbl_status_desc.setText("عند بدء التعلم، يتم حظر التطبيقات والمواقع الممنوعة تلقائياً لحمايتك من التشتت.")
            self.lbl_status_desc.setStyleSheet("font-size: 13px; color: #64748B;")
            self.btn_start_learning.setVisible(True)
            self.btn_finish_learning.setVisible(False)

    def toggle_startup(self, checked):
        self.cfg_mgr.set_startup(checked)

    def toggle_sound(self, checked):
        self.config["sound_enabled"] = checked
        self.audio_mgr.enabled = checked
        self.cfg_mgr.save_config()

    def toggle_water_reminders(self, checked):
        self.config["water_enabled"] = checked
        self.cfg_mgr.save_config()
        self.update_dashboard_timers()

    def toggle_pushups_reminders(self, checked):
        self.config["pushups_enabled"] = checked
        self.cfg_mgr.save_config()
        self.update_dashboard_timers()

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
        elif overlay_type == "eye_rest":
            self._eye_rest_overlay_open = False
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
        now_dt = datetime.datetime.now()
        now_str = QTime.currentTime().toString("hh:mm")

        # 🕌 Prayer 5-minute block timer enforcement
        if hasattr(self, "prayer_block_until") and self.prayer_block_until:
            if now_dt < self.prayer_block_until:
                self.app_blocker.set_active(True)
            else:
                self.prayer_block_until = None
                if not self.config.get("manual_session_active", False) and not getattr(self, "_prayer_overlay_open", False):
                    self.app_blocker.set_active(False)

        # 🕌 Prayer Times Check
        if self.config.get("prayer_times", {}).get("enabled", True) and not getattr(self, "_prayer_overlay_open", False):
            prayers = self.config.get("prayer_times", {}).get("times", {})
            for p_name, p_time in prayers.items():
                if p_time == now_str:
                    p_key = f"prayer_{p_name}_{now_str}"
                    if getattr(self, "last_prayer_key", "") != p_key:
                        self.last_prayer_key = p_key
                        self._prayer_overlay_open = True
                        self.prayer_block_until = now_dt + datetime.timedelta(minutes=5)
                        self.app_blocker.set_active(True)
                        self.prayer_overlay = PrayerOverlayWindow(
                            prayer_name=p_name,
                            audio_mgr=self.audio_mgr,
                            on_finish_callback=self._on_prayer_confirmed
                        )
                        break

        # 📿 Sunnah & Azkar Check
        sunnah_cfg = self.config.get("sunnah_reminders", {})
        if sunnah_cfg.get("enabled", True):
            for s_item in sunnah_cfg.get("items", []):
                if s_item.get("enabled", True) and s_item.get("time") == now_str:
                    s_key = f"sunnah_{s_item['id']}_{now_str}"
                    if getattr(self, "last_sunnah_key", "") != s_key:
                        self.last_sunnah_key = s_key
                        if self.audio_mgr:
                            self.audio_mgr.play_water_alarm()
                        if hasattr(self, "tray_icon") and self.tray_icon:
                            self.tray_icon.showMessage(
                                f"📿 تنبيه سنة/أذكار: {s_item['name']}",
                                f"قد حان موعد {s_item['name']} — تذكير إيماني مبارك 🤲",
                                QSystemTrayIcon.Information,
                                10000
                            )
                        QMessageBox.information(
                            self,
                            f"📿 تنبيه: {s_item['name']}",
                            f"✨ حان الآن موعد {s_item['name']}\n\n« الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ »"
                        )
                        break

        # 📅 Schedules Check
        if not self._schedule_overlay_open:
            for sched in self.config.get("learning_schedules", []):
                if sched.get("active", True) and sched["start"] == now_str:
                    sched_key = f"{sched['name']}_{now_str}"
                    if self.last_triggered_schedule_key != sched_key:
                        self.last_triggered_schedule_key = sched_key
                        
                        s_type = sched.get("type", "standard")
                        if s_type == "reminder":
                            self._appointment_overlay = AppointmentReminderOverlay(
                                appointment_name=sched['name'],
                                appointment_time=sched.get('start', ''),
                                is_strict=False,
                                audio_mgr=self.audio_mgr,
                                on_close_callback=None
                            )
                        else:
                            self._schedule_overlay_open = True
                            if s_type == "strict":
                                self.config["manual_session_is_strict"] = True
                            self.sched_overlay = StartScheduleOverlayWindow(
                                sched_name=sched["name"],
                                audio_mgr=self.audio_mgr,
                                on_confirm_callback=self._on_schedule_confirmed
                            )
                        break

        # 🏁 Auto-end Learning Session when scheduled end time is reached
        if self.config.get("manual_session_active", False) or self.app_blocker.is_active:
            for sched in self.config.get("learning_schedules", []):
                if sched.get("active", True) and sched.get("end") == now_str:
                    sched_end_key = f"end_{sched['name']}_{now_str}"
                    if getattr(self, "last_ended_schedule_key", "") != sched_end_key:
                        self.last_ended_schedule_key = sched_end_key
                        self.config["manual_session_is_strict"] = False
                        self.finish_learning_session()
                        if hasattr(self, "tray_icon") and self.tray_icon:
                            self.tray_icon.showMessage(
                                "🎉 انتهت جلسة التعلم",
                                f"وصلنا إلى موعد نهاية {sched['name']} ({sched.get('end')}). تم إلغاء حظر التطبيقات بنجاح!",
                                QSystemTrayIcon.Information,
                                7000
                            )
                        break

            m_end = self.config.get("manual_session_end_time", "")
            if m_end and m_end == now_str:
                if getattr(self, "last_ended_schedule_key", "") != f"m_end_{now_str}":
                    self.last_ended_schedule_key = f"m_end_{now_str}"
                    self.config["manual_session_is_strict"] = False
                    self.finish_learning_session()
                    if hasattr(self, "tray_icon") and self.tray_icon:
                        self.tray_icon.showMessage(
                            "🎉 انتهت جلسة التعلم",
                            "وصلنا لانتهاء فترة التعلم المحددة! تم فك الحظر.",
                            QSystemTrayIcon.Information,
                            7000
                        )

        if self.config.get("manual_session_active", False) or self.app_blocker.is_active:
            self.app_blocker.check_and_enforce()

    def _on_schedule_confirmed(self):
        """يُستدعى عند الضغط على 'حسناً' في شاشة بدء الجدول."""
        self._schedule_overlay_open = False
        self.start_manual_session()

    def _on_prayer_confirmed(self, arg=None):
        """يُستدعى عند انتهاء أو التفاعل مع شاشة الصلاة."""
        self._prayer_overlay_open = False

    def minute_tick_loop(self):
        if self.app_blocker.is_active:
            self.config["daily_stats"]["learning_minutes"] += 1
            self.lbl_stat_time.setText(f"{self.config['daily_stats']['learning_minutes']} دقيقة")
            self.award_points(1, "دقيقة تعلم")
            if self.config["daily_stats"]["learning_minutes"] >= 15:
                self.record_streak_activity()

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

        if self.config.get("water_enabled", True):
            self.water_timer_counter += 1
            if self.water_timer_counter >= self.config.get("water_interval_min", 40):
                self.water_timer_counter = 0
                if not self._water_overlay_open:
                    self.test_water_overlay()

        if self.config.get("pushups_enabled", True):
            self.pushups_timer_counter += 1
            if self.pushups_timer_counter >= self.config.get("pushups_interval_min", 120):
                self.pushups_timer_counter = 0
                if not self._pushups_overlay_open:
                    self.test_pushups_overlay()

        if self.config.get("eye_rest_enabled", True):
            self.eye_rest_counter += 1
            if self.eye_rest_counter >= self.config.get("eye_rest_interval_min", 20):
                self.eye_rest_counter = 0
                if not getattr(self, "_eye_rest_overlay_open", False):
                    self.test_eye_rest_overlay()

        self.update_dashboard_timers()

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


    def toggle_eye_rest_reminders(self, enabled: bool):
        self.config["eye_rest_enabled"] = enabled
        self.cfg_mgr.save_config()
        self.update_dashboard_timers()

    def update_dashboard_timers(self):
        if not hasattr(self, "card_next_timers"):
            return

        water_enabled = self.config.get("water_enabled", True)
        pushups_enabled = self.config.get("pushups_enabled", True)
        eye_rest_enabled = self.config.get("eye_rest_enabled", True)

        visible_count = 0

        # Eye Rest Timer
        if eye_rest_enabled:
            self.box_timer_eye.setVisible(True)
            visible_count += 1
            interval = self.config.get("eye_rest_interval_min", 20)
            rem = max(0, interval - getattr(self, "eye_rest_counter", 0))
            if rem == 0:
                self.lbl_timer_eye.setText("الآن 🔔")
            else:
                self.lbl_timer_eye.setText(f"بعد {rem} دقيقة")
        else:
            self.box_timer_eye.setVisible(False)

        # Pushups/Exercise Timer
        if pushups_enabled:
            self.box_timer_pushups.setVisible(True)
            visible_count += 1
            interval = self.config.get("pushups_interval_min", 120)
            rem = max(0, interval - getattr(self, "pushups_timer_counter", 0))
            if rem == 0:
                self.lbl_timer_pushups.setText("الآن 🏋️")
            else:
                self.lbl_timer_pushups.setText(f"بعد {rem} دقيقة")
        else:
            self.box_timer_pushups.setVisible(False)

        # Water Timer
        if water_enabled:
            self.box_timer_water.setVisible(True)
            visible_count += 1
            interval = self.config.get("water_interval_min", 40)
            rem = max(0, interval - getattr(self, "water_timer_counter", 0))
            if rem == 0:
                self.lbl_timer_water.setText("الآن 💧")
            else:
                self.lbl_timer_water.setText(f"بعد {rem} دقيقة")
        else:
            self.box_timer_water.setVisible(False)

        # Hide entire card if all 3 are disabled
        self.card_next_timers.setVisible(visible_count > 0)

    # ─── STREAK MANAGEMENT ──────────────────────────────────────────────────
    def update_streak_logic(self):
        s_data = self.config.get("streak_data", {})
        today = datetime.date.today()
        today_str = today.isoformat()
        current_month_str = today.strftime("%Y-%m")

        # 1. Reset monthly freezes if month changed
        if s_data.get("current_month") != current_month_str:
            s_data["current_month"] = current_month_str
            s_data["freezes_remaining"] = 3

        last_active_str = s_data.get("last_active_date", "")

        if last_active_str:
            try:
                last_date = datetime.date.fromisoformat(last_active_str)
                diff = (today - last_date).days

                # User missed 1 or more days
                if diff > 1:
                    missed_days = diff - 1
                    rescues_used = 0
                    for _ in range(missed_days):
                        if s_data.get("freezes_remaining", 0) > 0:
                            s_data["freezes_remaining"] -= 1
                            s_data["total_rescues_used"] = s_data.get("total_rescues_used", 0) + 1
                            rescues_used += 1
                        else:
                            s_data["is_alive"] = False
                            s_data["current_streak"] = 0
                            break

                    if rescues_used > 0 and s_data.get("is_alive", True):
                        if hasattr(self, "tray_icon") and self.tray_icon:
                            self.tray_icon.showMessage(
                                "🛡️ تم إنقاذ الستريك الخاص بك!",
                                f"تم استخدام {rescues_used} من إنقاذات الشهر وحماية الستريك من الموت! متبقي {s_data['freezes_remaining']} إنقاذات.",
                                QSystemTrayIcon.Information,
                                7000
                            )
            except Exception as e:
                print(f"Error checking streak logic: {e}")

        self.config["streak_data"] = s_data
        self.cfg_mgr.save_config()
        self.update_streak_ui()

    def record_streak_activity(self):
        s_data = self.config.get("streak_data", {})
        today_str = datetime.date.today().isoformat()
        current_month_str = datetime.date.today().strftime("%Y-%m")

        if s_data.get("current_month") != current_month_str:
            s_data["current_month"] = current_month_str
            s_data["freezes_remaining"] = 3

        if s_data.get("last_active_date") != today_str:
            if s_data.get("is_alive", True) and s_data.get("current_streak", 0) > 0:
                s_data["current_streak"] += 1
            else:
                s_data["current_streak"] = 1
                s_data["is_alive"] = True

            s_data["last_active_date"] = today_str
            self.config["streak_data"] = s_data
            self.cfg_mgr.save_config()
            self.update_streak_ui()

            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.showMessage(
                    "🔥 الستريك مشتعل!",
                    f"أحسنت! وصل الستريك الخاص بك إلى {s_data['current_streak']} أيام متتالية 🚀",
                    QSystemTrayIcon.Information,
                    5000
                )

    def update_streak_ui(self):
        if not hasattr(self, "lbl_streak_val"):
            return

        s_data = self.config.get("streak_data", {})
        is_alive = s_data.get("is_alive", True)
        count = s_data.get("current_streak", 0)
        freezes = s_data.get("freezes_remaining", 3)

        if is_alive and count > 0:
            icon_file = "streakfirethefireisfiringthestreakisstillgoinglogo.png"
            title_text = f"{count} يوم متتالي 🔥"
            border_color = "#F97316"
            bg_color = "rgba(249, 115, 22, 0.12)"
            tooltip_msg = f"🔥 الستريك مشتعل! ({count} يوم متتالي)\n🛡️ متبقي {freezes} إنقاذات شهرية"
        else:
            icon_file = "deadstreakfirelogo.png"
            title_text = "0 يوم (منتهي 💀)"
            border_color = "#64748B"
            bg_color = "rgba(100, 116, 139, 0.10)"
            tooltip_msg = f"💀 الستريك منتهي!\nأنجز 15 دقيقة تعلم اليوم لإعادة إشعال النار 🔥\n🛡️ متبقي {freezes} إنقاذات شهرية"

        asset_p = get_asset_path(icon_file)
        if asset_p and os.path.exists(asset_p):
            pix = QPixmap(asset_p).scaled(QSize(34, 34), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_streak_icon.setPixmap(pix)
            if hasattr(self, "lbl_top_streak_icon"):
                pix_top = QPixmap(asset_p).scaled(QSize(22, 22), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_top_streak_icon.setPixmap(pix_top)

        self.lbl_streak_val.setText(f"{count} أيام")
        self.lbl_streak_freezes.setText(f"🛡️ {freezes}/3 إنقاذات متبقية")

        if hasattr(self, "lbl_top_streak_text"):
            self.lbl_top_streak_text.setText(title_text)
            self.card_top_streak.setToolTip(tooltip_msg)
            self.card_top_streak.setStyleSheet(f"""
                QFrame {{
                    background: {bg_color};
                    border: 1.5px solid {border_color};
                    border-radius: 12px;
                    padding: 4px 12px;
                }}
            """)

    def test_eye_rest_overlay(self):
        if not getattr(self, "_eye_rest_overlay_open", False):
            self._eye_rest_overlay_open = True
            self.eye_rest_overlay = EyeRestOverlayWindow(
                audio_mgr=self.audio_mgr,
                on_finish_callback=self.handle_overlay_finish
            )

    # ─── QUICK LAUNCH FEATURES ───────────────────────────────────────────────
    def trigger_quick_launch(self):
        dlg = LaunchProfilesDialog(self)
        dlg.exec()

    def manage_quick_launch_profiles(self):
        dlg = ManageQuickLaunchProfilesDialog(self)
        dlg.exec()

    def launch_profile_environment(self, profile):
        if not self.config.get("manual_session_active", False):
            self.start_manual_session()

        launched_apps = 0
        launched_urls = 0

        for app in profile.get("apps", []):
            try:
                if os.path.isabs(app) and os.path.exists(app):
                    subprocess.Popen([app])
                else:
                    os.startfile(app)
                launched_apps += 1
            except Exception as e:
                print(f"Error launching app {app}: {e}")

        for url in profile.get("urls", []):
            try:
                open_url_in_default_browser(url)
                launched_urls += 1
            except Exception as e:
                print(f"Error opening url {url}: {e}")

        p_title = profile.get("title", "بيئة العمل")
        QMessageBox.information(
            self,
            "العمل السريع 🚀",
            f"تم بدء جلسة التعلم وتشغيل '{p_title}' بنجاح!\n\n💻 تم فتح {launched_apps} تطبيقات\n🌐 تم فتح {launched_urls} مواقع"
        )


    # ─── PORTFOLIO & ACHIEVEMENTS VAULT ────────────────────────────────────────
    def create_portfolio_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background: #0B0F19; width: 8px; border-radius: 4px; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        self.portfolio_layout = QVBoxLayout(scroll_widget)
        self.portfolio_layout.setContentsMargins(32, 28, 32, 28)
        self.portfolio_layout.setSpacing(20)

        scroll.setWidget(scroll_widget)
        page_layout.addWidget(scroll)

        self.reload_portfolio_ui()
        return page

    def reload_portfolio_ui(self):
        clear_layout_recursive(self.portfolio_layout)

        folders = self.config.get("portfolio_folders", [])
        current_fid = getattr(self, "current_portfolio_folder_id", None)
        active_folder = next((f for f in folders if f.get("id") == current_fid), None) if current_fid else None

        # ── Header Card
        hdr_card = QFrame()
        if active_folder:
            hdr_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #064E3B, stop:0.5 #065F46, stop:1 #047857);
                    border: 2px solid #34D399;
                    border-radius: 20px;
                }
            """)
        else:
            hdr_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1E1B4B, stop:0.5 #0F172A, stop:1 #0284C7);
                    border: 1px solid rgba(56, 189, 248, 0.25);
                    border-radius: 20px;
                }
            """)

        hdr_row = QHBoxLayout(hdr_card)
        hdr_row.setContentsMargins(24, 20, 24, 20)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        if active_folder:
            crumb_lbl = QLabel(f"📂 المعرض الرئيسي  ⬅️  📁 {active_folder.get('title')}")
            crumb_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #A7F3D0; letter-spacing: 0.5px;")
            t_lbl = QLabel(f"📁 مجلد: {active_folder.get('title')}")
            t_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFFFFF;")
            d_lbl = QLabel(f"تستعرض الآن المحتويات والشهادات المحفوظة داخل مجلد ({active_folder.get('title')})")
            d_lbl.setStyleSheet("color: #D1FAE5; font-size: 13px;")
            title_box.addWidget(crumb_lbl)
            title_box.addWidget(t_lbl)
            title_box.addWidget(d_lbl)
        else:
            t_lbl = QLabel("🏆 معرض الشهادات والإنجازات الشخصية")
            t_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #F1F5F9;")
            d_lbl = QLabel("احفظ شهاداتك، إنجازاتك، ووثائق نجاحك في مجلدات منظمة لتبقى دائمًا فخورًا برحلتك!")
            d_lbl.setStyleSheet("color: #94A3B8; font-size: 13px;")
            title_box.addWidget(t_lbl)
            title_box.addWidget(d_lbl)

        hdr_row.addLayout(title_box, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        if active_folder:
            btn_back = QPushButton("⬅️ العودة إلى جميع المجلدات")
            btn_back.setStyleSheet("background: rgba(0,0,0,0.3); color: #FFFFFF; font-weight: bold; border-radius: 12px; padding: 12px 20px; border: 1px solid #34D399;")
            btn_back.setCursor(Qt.PointingHandCursor)
            btn_back.clicked.connect(lambda: self._set_portfolio_folder(None))
            btn_row.addWidget(btn_back)

            btn_add_item = QPushButton("🖼️ إضافة شهادة / صورة للمجلد")
            btn_add_item.setStyleSheet("background: #10B981; color: white; font-weight: bold; border-radius: 12px; padding: 12px 20px; border: none;")
            btn_add_item.setCursor(Qt.PointingHandCursor)
            af_id = active_folder['id']
            btn_add_item.clicked.connect(lambda ch=False, fid=af_id: self.add_portfolio_item(fid))
            btn_row.addWidget(btn_add_item)
        else:
            btn_add_folder = QPushButton("📁 أضف مجلد إنجاز جديد")
            btn_add_folder.setObjectName("PrimaryBtn")
            btn_add_folder.setCursor(Qt.PointingHandCursor)
            btn_add_folder.clicked.connect(self.add_portfolio_folder)
            btn_row.addWidget(btn_add_folder)

        hdr_row.addLayout(btn_row)
        self.portfolio_layout.addWidget(hdr_card)

        if not active_folder:
            sec_title = QLabel("📂 المجلدات الرئيسية للإنجازات:")
            sec_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
            self.portfolio_layout.addWidget(sec_title)

            grid = QGridLayout()
            grid.setSpacing(16)

            row, col = 0, 0
            for folder in folders:
                f_card = QFrame()
                f_card.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111C2E, stop:1 #0C1520);
                        border: 1px solid rgba(56, 189, 248, 0.15);
                        border-radius: 18px;
                    }
                    QFrame:hover { border-color: #38BDF8; }
                """)
                f_layout = QVBoxLayout(f_card)
                f_layout.setContentsMargins(20, 20, 20, 20)
                f_layout.setSpacing(10)

                top_h = QHBoxLayout()
                ic_l = QLabel()
                pix = get_tinted_pixmap(folder.get("icon", "rocketlogo.png"), "#38BDF8", QSize(36, 36))
                ic_l.setPixmap(pix)

                title_l = QLabel(folder.get("title", "مجلد بدون عنوان"))
                title_l.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")

                top_h.addWidget(ic_l)
                top_h.addWidget(title_l, 1)
                f_layout.addLayout(top_h)

                items_count = len(folder.get("items", []))
                cnt_l = QLabel(f"تحتوي على {items_count} شهادة / عنصر")
                cnt_l.setStyleSheet("color: #64748B; font-size: 13px;")
                f_layout.addWidget(cnt_l)

                action_row = QHBoxLayout()
                btn_open = QPushButton("فتح المجلد 📂")
                btn_open.setStyleSheet("background: rgba(2, 132, 199, 0.2); color: #38BDF8; font-weight: bold; border-radius: 10px; padding: 8px 16px; border: 1px solid rgba(56,189,248,0.3);")
                btn_open.setCursor(Qt.PointingHandCursor)
                f_id = folder["id"]
                btn_open.clicked.connect(lambda ch=False, fid=f_id: self._set_portfolio_folder(fid))

                btn_del_f = QPushButton()
                btn_del_f.setObjectName("IconTrashBtn")
                btn_del_f.setCursor(Qt.PointingHandCursor)
                btn_del_f.setFixedSize(36, 36)
                trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(18, 18))
                if not trash_pix.isNull():
                    btn_del_f.setIcon(QIcon(trash_pix))
                btn_del_f.clicked.connect(lambda ch=False, fid=f_id: self.delete_portfolio_folder(fid))

                action_row.addWidget(btn_open, 1)
                action_row.addWidget(btn_del_f)
                f_layout.addLayout(action_row)

                grid.addWidget(f_card, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            self.portfolio_layout.addLayout(grid)
            self.portfolio_layout.addStretch()

        else:
            folder = active_folder
            sec_title = QLabel(f"🖼️ الشهادات والإنجازات داخل: ({folder.get('title')})")
            sec_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
            self.portfolio_layout.addWidget(sec_title)

            items = folder.get("items", [])
            if not items:
                empty_card = QFrame()
                empty_card.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1626, stop:1 #080D18);
                        border: 2px dashed rgba(56, 189, 248, 0.25);
                        border-radius: 20px;
                    }
                """)
                empty_layout = QVBoxLayout(empty_card)
                empty_layout.setContentsMargins(40, 50, 40, 50)
                empty_layout.setSpacing(14)

                ic_l = QLabel("📜")
                ic_l.setStyleSheet("font-size: 48px;")
                ic_l.setAlignment(Qt.AlignCenter)

                empty_lbl = QLabel("لا توجد شهادات أو إنجازات مرفوعة في هذا المجلد بعد.\nاضغط على زر '🖼️ إضافة شهادة / صورة للمجلد' بالأعلى لإضافة إنجازاتك!")
                empty_lbl.setStyleSheet("color: #94A3B8; font-size: 16px; font-weight: 500; line-height: 1.6;")
                empty_lbl.setAlignment(Qt.AlignCenter)

                empty_layout.addWidget(ic_l)
                empty_layout.addWidget(empty_lbl)
                self.portfolio_layout.addWidget(empty_card)
            else:
                grid = QGridLayout()
                grid.setSpacing(16)

                row, col = 0, 0
                for item in items:
                    it_card = QFrame()
                    it_card.setStyleSheet("""
                        QFrame {
                            background: #0D1626;
                            border: 1px solid rgba(56, 189, 248, 0.2);
                            border-radius: 16px;
                        }
                        QFrame:hover {
                            border-color: #38BDF8;
                        }
                    """)
                    it_layout = QVBoxLayout(it_card)
                    it_layout.setContentsMargins(14, 14, 14, 14)
                    it_layout.setSpacing(8)

                    img_path = item.get("image_path", "")
                    img_lbl = QLabel()
                    img_lbl.setFixedHeight(140)
                    img_lbl.setAlignment(Qt.AlignCenter)
                    img_lbl.setStyleSheet("background: #060A12; border-radius: 10px;")

                    if img_path and os.path.exists(img_path):
                        pix = QPixmap(img_path).scaled(240, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img_lbl.setPixmap(pix)
                    else:
                        img_lbl.setText("🖼️ صورة غير متوفرة")

                    it_layout.addWidget(img_lbl)

                    item_title = QLabel(item.get("title", "إنجاز بدون اسم"))
                    item_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9;")
                    item_title.setWordWrap(True)
                    it_layout.addWidget(item_title)

                    if item.get("date"):
                        date_l = QLabel(f"📅 {item.get('date')}")
                        date_l.setStyleSheet("font-size: 11px; color: #64748B;")
                        it_layout.addWidget(date_l)

                    act_h = QHBoxLayout()
                    act_h.setSpacing(8)

                    btn_view = QPushButton("🔍 تكبير الصورة")
                    btn_view.setStyleSheet("background: rgba(56, 189, 248, 0.15); color: #38BDF8; font-weight: bold; font-size: 12px; border-radius: 8px; padding: 6px 12px; border: 1px solid rgba(56,189,248,0.3);")
                    btn_view.setCursor(Qt.PointingHandCursor)
                    ipath = img_path
                    ititle = item.get("title", "")
                    btn_view.clicked.connect(lambda ch=False, p=ipath, t=ititle: self.show_image_viewer(p, t))

                    btn_del_item = QPushButton()
                    btn_del_item.setObjectName("IconTrashBtn")
                    btn_del_item.setCursor(Qt.PointingHandCursor)
                    btn_del_item.setFixedSize(32, 32)
                    trash_pix = get_tinted_pixmap("trash.png", "#EF4444", QSize(16, 16))
                    if not trash_pix.isNull():
                        btn_del_item.setIcon(QIcon(trash_pix))
                    iid = item["id"]
                    fid = folder["id"]
                    btn_del_item.clicked.connect(lambda ch=False, f_id=fid, i_id=iid: self.delete_portfolio_item(f_id, i_id))

                    act_h.addWidget(btn_view, 1)
                    act_h.addWidget(btn_del_item)
                    it_layout.addLayout(act_h)

                    grid.addWidget(it_card, row, col)
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1

                self.portfolio_layout.addLayout(grid)

            self.portfolio_layout.addStretch()

    def _set_portfolio_folder(self, folder_id):
        self.current_portfolio_folder_id = folder_id
        self.reload_portfolio_ui()

    def add_portfolio_folder(self):
        dlg = AddPortfolioFolderDialog(self)
        if dlg.exec() == QDialog.Accepted and dlg.folder_title:
            folder_id = f"folder_{int(datetime.datetime.now().timestamp())}"
            new_folder = {
                "id": folder_id,
                "title": dlg.folder_title,
                "icon": "rocketlogo.png",
                "items": []
            }
            if "portfolio_folders" not in self.config:
                self.config["portfolio_folders"] = []
            self.config["portfolio_folders"].append(new_folder)
            self.cfg_mgr.save_config()
            self.reload_portfolio_ui()

    def delete_portfolio_folder(self, folder_id):
        reply = QMessageBox.question(
            self,
            "حذف المجلد",
            "هل أنت تأكد من حذف هذا المجلد وجميع الشهادات والإنجازات بداخله؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config["portfolio_folders"] = [f for f in self.config.get("portfolio_folders", []) if f.get("id") != folder_id]
            self.cfg_mgr.save_config()
            if getattr(self, "current_portfolio_folder_id", None) == folder_id:
                self.current_portfolio_folder_id = None
            self.reload_portfolio_ui()

    def add_portfolio_item(self, folder_id):
        folder = next((f for f in self.config.get("portfolio_folders", []) if f.get("id") == folder_id), None)
        folder_name = folder.get("title", "") if folder else ""
        dlg = AddPortfolioItemDialog(folder_name=folder_name, parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.file_path:
            item_id = f"item_{int(datetime.datetime.now().timestamp())}"
            new_item = {
                "id": item_id,
                "title": dlg.item_title,
                "image_path": dlg.file_path,
                "date": datetime.date.today().strftime("%Y-%m-%d")
            }
            if folder:
                if "items" not in folder:
                    folder["items"] = []
                folder["items"].append(new_item)
                self.cfg_mgr.save_config()
                self.reload_portfolio_ui()

    def delete_portfolio_item(self, folder_id, item_id):
        reply = QMessageBox.question(
            self,
            "حذف الشهادة",
            "هل تريد حذف هذه الشهادة من المجلد؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for folder in self.config.get("portfolio_folders", []):
                if folder.get("id") == folder_id:
                    folder["items"] = [it for it in folder.get("items", []) if it.get("id") != item_id]
                    break
            self.cfg_mgr.save_config()
            self.reload_portfolio_ui()

    def show_image_viewer(self, image_path, title_text):
        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, "خطأ", "الصورة المحددة غير موجودة!")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"عرض الشهادة: {title_text}")
        dlg.resize(900, 650)
        dlg.setStyleSheet("background-color: #060A12; color: white;")

        vbox = QVBoxLayout(dlg)
        lbl_t = QLabel(title_text)
        lbl_t.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8; padding: 10px;")
        lbl_t.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl_t)

        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        pix = QPixmap(image_path).scaled(860, 560, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl_img.setPixmap(pix)
        vbox.addWidget(lbl_img, 1)

        dlg.exec()

    # ─── PRAYER TIMES PAGE ──────────────────────────────────────────────────
    def create_prayer_times_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        hdr = QFrame()
        hdr.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #064E3B, stop:0.5 #065F46, stop:1 #047857);
                border: 1px solid #34D399;
                border-radius: 20px;
            }
        """)
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(24, 20, 24, 20)

        title_vb = QVBoxLayout()
        title_vb.setSpacing(4)
        title = QLabel("🕌 مواعيد وتنبيهات الصلوات الخمس")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFFFFF;")
        desc = QLabel("أدخل وقت كل صلاة يدوياً بالـ (الساعة والدقيقة). عند حلول الوقت سيتم تنبيهك وإيقاف جميع الألعاب والمشتتات لمدة 5 دقائق لأداء الصلاة.")
        desc.setStyleSheet("color: #D1FAE5; font-size: 13px;")
        title_vb.addWidget(title)
        title_vb.addWidget(desc)
        hdr_layout.addLayout(title_vb, 1)

        btn_save_top = QPushButton("💾 حفظ مواعيد الصلاة")
        btn_save_top.setStyleSheet("background: #10B981; color: white; font-weight: bold; font-size: 15px; border-radius: 12px; padding: 12px 24px; border: none;")
        btn_save_top.setCursor(Qt.PointingHandCursor)
        hdr_layout.addWidget(btn_save_top)

        layout.addWidget(hdr)

        enable_card = QFrame()
        enable_card.setObjectName("Card")
        enable_layout = QHBoxLayout(enable_card)
        enable_layout.setContentsMargins(20, 14, 20, 14)

        chk_enable_prayer = QCheckBox("تفعيل تنبيهات الصلاة والتوقف الإجباري لمدة 5 دقائق")
        chk_enable_prayer.setStyleSheet("font-size: 16px; font-weight: bold; color: #34D399;")
        p_cfg = self.config.get("prayer_times", {"enabled": True, "times": {}})
        chk_enable_prayer.setChecked(p_cfg.get("enabled", True))

        enable_layout.addWidget(chk_enable_prayer)
        layout.addWidget(enable_card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background: #0B0F19; width: 8px; border-radius: 4px; }")

        scroll_w = QWidget()
        scroll_w.setStyleSheet("background: transparent;")
        prayers_vbox = QVBoxLayout(scroll_w)
        prayers_vbox.setSpacing(14)
        prayers_vbox.setContentsMargins(0, 0, 0, 0)

        prayers_def = [
            ("الفجر",  "🌅 صلاة الفجر",  "04:45"),
            ("الظهر",  "☀️ صلاة الظهر",  "12:15"),
            ("العصر",  "🌤️ صلاة العصر",  "15:35"),
            ("المغرب", "🌅 صلاة المغرب", "18:10"),
            ("العشاء", "🌙 صلاة العشاء", "19:40")
        ]

        saved_times = p_cfg.get("times", {})
        self.prayer_inputs = {}

        for key_name, display_name, default_time in prayers_def:
            current_24h = saved_times.get(key_name, default_time)
            
            try:
                h_24, m_24 = map(int, current_24h.split(":"))
            except:
                h_24, m_24 = 12, 0

            if h_24 == 0:
                h_12 = 12
                period_str = "صباحاً AM"
            elif h_24 == 12:
                h_12 = 12
                period_str = "مساءً PM"
            elif h_24 > 12:
                h_12 = h_24 - 12
                period_str = "مساءً PM"
            else:
                h_12 = h_24
                period_str = "صباحاً AM"

            p_card = QFrame()
            p_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F1E19, stop:1 #0A1411);
                    border: 1px solid rgba(52, 211, 153, 0.2);
                    border-radius: 16px;
                }
                QFrame:hover {
                    border-color: #34D399;
                }
            """)
            p_layout = QHBoxLayout(p_card)
            p_layout.setContentsMargins(20, 16, 20, 16)
            p_layout.setSpacing(16)

            lbl_pname = QLabel(display_name)
            lbl_pname.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
            lbl_pname.setMinimumWidth(160)

            in_layout = QHBoxLayout()
            in_layout.setSpacing(8)

            lbl_h = QLabel("الساعة:")
            lbl_h.setStyleSheet("color: #94A3B8; font-weight: bold;")
            
            txt_hour = QLineEdit()
            txt_hour.setText(str(h_12))
            txt_hour.setFixedWidth(70)
            txt_hour.setAlignment(Qt.AlignCenter)
            txt_hour.setPlaceholderText("9")
            txt_hour.setStyleSheet("font-size: 16px; font-weight: bold; color: #34D399; background: #060A12; border: 1px solid #10B981;")

            lbl_colon = QLabel(":")
            lbl_colon.setStyleSheet("font-size: 20px; font-weight: bold; color: #34D399;")

            lbl_m = QLabel("الدقيقة:")
            lbl_m.setStyleSheet("color: #94A3B8; font-weight: bold;")

            txt_min = QLineEdit()
            txt_min.setText(f"{m_24:02d}")
            txt_min.setFixedWidth(70)
            txt_min.setAlignment(Qt.AlignCenter)
            txt_min.setPlaceholderText("45")
            txt_min.setStyleSheet("font-size: 16px; font-weight: bold; color: #34D399; background: #060A12; border: 1px solid #10B981;")

            cmb_period = QComboBox()
            cmb_period.addItems(["صباحاً AM", "مساءً PM"])
            cmb_period.setCurrentText(period_str)
            cmb_period.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9; background: #060A12;")

            lbl_preview = QLabel(f"التوقيت الفعلي: {current_24h}")
            lbl_preview.setStyleSheet("color: #64748B; font-size: 13px; font-weight: bold;")

            def update_preview_label(h_txt=None, m_txt=None, per_txt=None, key=key_name, l_prev=lbl_preview, t_h=txt_hour, t_m=txt_min, c_p=cmb_period):
                try:
                    h_val = int(t_h.text().strip())
                    m_val = int(t_m.text().strip())
                    period = c_p.currentText()

                    if h_val < 1: h_val = 1
                    if h_val > 12: h_val = 12
                    if m_val < 0: m_val = 0
                    if m_val > 59: m_val = 59

                    if "مساءً" in period:
                        h24 = 12 if h_val == 12 else h_val + 12
                    else:
                        h24 = 0 if h_val == 12 else h_val

                    res_str = f"{h24:02d}:{m_val:02d}"
                    l_prev.setText(f"التوقيت الفعلي: {res_str}")
                except:
                    pass

            txt_hour.textChanged.connect(update_preview_label)
            txt_min.textChanged.connect(update_preview_label)
            cmb_period.currentIndexChanged.connect(update_preview_label)

            in_layout.addWidget(lbl_h)
            in_layout.addWidget(txt_hour)
            in_layout.addWidget(lbl_colon)
            in_layout.addWidget(lbl_m)
            in_layout.addWidget(txt_min)
            in_layout.addWidget(cmb_period)

            p_layout.addWidget(lbl_pname)
            p_layout.addLayout(in_layout)
            p_layout.addStretch()
            p_layout.addWidget(lbl_preview)

            prayers_vbox.addWidget(p_card)

            self.prayer_inputs[key_name] = (txt_hour, txt_min, cmb_period, lbl_preview)

        # ── SUNNAH & AZKAR SECTION ──────────────────────────────────────────────
        sunnah_hdr = QFrame()
        sunnah_hdr.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E1B4B, stop:0.5 #311042, stop:1 #0F172A);
                border: 1px solid #A855F7;
                border-radius: 18px;
                margin-top: 15px;
            }
        """)
        sunnah_hdr_layout = QHBoxLayout(sunnah_hdr)
        sunnah_hdr_layout.setContentsMargins(20, 16, 20, 16)

        s_title_vb = QVBoxLayout()
        s_title_vb.setSpacing(4)
        s_title = QLabel("📿 تنبيهات السنن والأذكار والنوافل")
        s_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
        s_desc = QLabel("حدد السنن والأذكار التي تود التذكير بها واضبط ووقتها المحدد:")
        s_desc.setStyleSheet("color: #E9D5FF; font-size: 13px;")
        s_title_vb.addWidget(s_title)
        s_title_vb.addWidget(s_desc)
        sunnah_hdr_layout.addLayout(s_title_vb, 1)

        prayers_vbox.addWidget(sunnah_hdr)

        sunnah_cfg = self.config.get("sunnah_reminders", {"enabled": True, "items": []})
        chk_enable_sunnah_master = QCheckBox("تفعيل تنبيهات السنن والأذكار النفلية")
        chk_enable_sunnah_master.setStyleSheet("font-size: 16px; font-weight: bold; color: #C084FC;")
        chk_enable_sunnah_master.setChecked(sunnah_cfg.get("enabled", True))
        prayers_vbox.addWidget(chk_enable_sunnah_master)

        sunnah_items_def = sunnah_cfg.get("items", [
            {"id": "sunnah_duha", "name": "☀️ صلاة الضحى", "time": "09:30", "enabled": True},
            {"id": "sunnah_azkar_m", "name": "🌅 أذكار الصباح", "time": "06:30", "enabled": True},
            {"id": "sunnah_azkar_e", "name": "<ctrl42> أذكار المساء", "time": "17:00", "enabled": True},
            {"id": "sunnah_qiyam", "name": "🌙 صلاة قيام الليل والوتر", "time": "02:00", "enabled": True},
            {"id": "sunnah_fajr", "name": "🌅 سنة الفجر (الركعتين)", "time": "04:30", "enabled": True}
        ])

        self.sunnah_inputs = {}

        for item in sunnah_items_def:
            s_id = item["id"]
            s_name = item["name"]
            s_time = item.get("time", "09:00")
            s_enabled = item.get("enabled", True)

            try:
                h_24, m_24 = map(int, s_time.split(":"))
            except:
                h_24, m_24 = 9, 0

            if h_24 == 0:
                h_12, period_str = 12, "صباحاً AM"
            elif h_24 == 12:
                h_12, period_str = 12, "مساءً PM"
            elif h_24 > 12:
                h_12, period_str = h_24 - 12, "مساءً PM"
            else:
                h_12, period_str = h_24, "صباحاً AM"

            s_card = QFrame()
            s_card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A102F, stop:1 #0F0A1C);
                    border: 1px solid rgba(168, 85, 247, 0.2);
                    border-radius: 16px;
                }
                QFrame:hover {
                    border-color: #A855F7;
                }
            """)
            s_layout = QHBoxLayout(s_card)
            s_layout.setContentsMargins(18, 14, 18, 14)
            s_layout.setSpacing(14)

            chk_item = QCheckBox(s_name)
            chk_item.setChecked(s_enabled)
            chk_item.setStyleSheet("font-size: 16px; font-weight: bold; color: #F1F5F9;")
            chk_item.setMinimumWidth(180)

            in_layout = QHBoxLayout()
            in_layout.setSpacing(8)

            txt_hour = QLineEdit(str(h_12))
            txt_hour.setFixedWidth(65)
            txt_hour.setAlignment(Qt.AlignCenter)
            txt_hour.setStyleSheet("font-size: 15px; font-weight: bold; color: #C084FC; background: #060A12; border: 1px solid #8B5CF6;")

            lbl_colon = QLabel(":")
            lbl_colon.setStyleSheet("font-size: 18px; font-weight: bold; color: #C084FC;")

            txt_min = QLineEdit(f"{m_24:02d}")
            txt_min.setFixedWidth(65)
            txt_min.setAlignment(Qt.AlignCenter)
            txt_min.setStyleSheet("font-size: 15px; font-weight: bold; color: #C084FC; background: #060A12; border: 1px solid #8B5CF6;")

            cmb_period = QComboBox()
            cmb_period.addItems(["صباحاً AM", "مساءً PM"])
            cmb_period.setCurrentText(period_str)
            cmb_period.setStyleSheet("font-size: 13px; font-weight: bold; color: #F1F5F9; background: #060A12;")

            lbl_preview = QLabel(f"التوقيت: {s_time}")
            lbl_preview.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: bold;")

            def update_sunnah_preview(t_h=txt_hour, t_m=txt_min, c_p=cmb_period, l_p=lbl_preview):
                try:
                    hv = int(t_h.text().strip() or "12")
                    mv = int(t_m.text().strip() or "0")
                    p = c_p.currentText()
                    if hv < 1: hv = 1
                    if hv > 12: hv = 12
                    if mv < 0: mv = 0
                    if mv > 59: mv = 59
                    if "مساءً" in p:
                        h24 = 12 if hv == 12 else hv + 12
                    else:
                        h24 = 0 if hv == 12 else hv
                    l_p.setText(f"التوقيت: {h24:02d}:{mv:02d}")
                except:
                    pass

            txt_hour.textChanged.connect(update_sunnah_preview)
            txt_min.textChanged.connect(update_sunnah_preview)
            cmb_period.currentIndexChanged.connect(update_sunnah_preview)

            in_layout.addWidget(txt_hour)
            in_layout.addWidget(lbl_colon)
            in_layout.addWidget(txt_min)
            in_layout.addWidget(cmb_period)

            s_layout.addWidget(chk_item)
            s_layout.addLayout(in_layout)
            s_layout.addStretch()
            s_layout.addWidget(lbl_preview)

            prayers_vbox.addWidget(s_card)
            self.sunnah_inputs[s_id] = (chk_item, txt_hour, txt_min, cmb_period, s_name)

        scroll.setWidget(scroll_w)
        layout.addWidget(scroll)

        def save_prayers():
            new_times = {}
            for k, (t_h, t_m, c_p, _) in self.prayer_inputs.items():
                try:
                    h_val = int(t_h.text().strip() or "12")
                    m_val = int(t_m.text().strip() or "0")
                    period = c_p.currentText()

                    if h_val < 1: h_val = 1
                    if h_val > 12: h_val = 12
                    if m_val < 0: m_val = 0
                    if m_val > 59: m_val = 59

                    if "مساءً" in period:
                        h24 = 12 if h_val == 12 else h_val + 12
                    else:
                        h24 = 0 if h_val == 12 else h_val

                    new_times[k] = f"{h24:02d}:{m_val:02d}"
                except Exception as e:
                    print(f"Error parsing prayer time for {k}: {e}")

            self.config["prayer_times"] = {
                "enabled": chk_enable_prayer.isChecked(),
                "times": new_times
            }

            new_sunnah_items = []
            for s_id, (chk_item, t_h, t_m, c_p, s_name) in self.sunnah_inputs.items():
                try:
                    hv = int(t_h.text().strip() or "12")
                    mv = int(t_m.text().strip() or "0")
                    p = c_p.currentText()
                    if hv < 1: hv = 1
                    if hv > 12: hv = 12
                    if mv < 0: mv = 0
                    if mv > 59: mv = 59
                    if "مساءً" in p:
                        h24 = 12 if hv == 12 else hv + 12
                    else:
                        h24 = 0 if hv == 12 else hv
                    t_str = f"{h24:02d}:{mv:02d}"
                except:
                    t_str = "09:00"

                new_sunnah_items.append({
                    "id": s_id,
                    "name": s_name,
                    "time": t_str,
                    "enabled": chk_item.isChecked()
                })

            self.config["sunnah_reminders"] = {
                "enabled": chk_enable_sunnah_master.isChecked(),
                "items": new_sunnah_items
            }

            self.cfg_mgr.save_config()
            QMessageBox.information(page, "تم الحفظ 🕌", "تم حفظ مواعيد الصلوات الخمس والسنن والأذكار بنجاح!")

        btn_save_top.clicked.connect(save_prayers)
        return page
