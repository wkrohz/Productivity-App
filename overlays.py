import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon
from asset_helper import get_tinted_pixmap

class StartScheduleOverlayWindow(QWidget):
    """Full-screen alarm overlay when a scheduled learning session begins."""
    def __init__(self, sched_name, audio_mgr=None, on_confirm_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_confirm_callback = on_confirm_callback
        self.sched_name = sched_name

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self.setup_ui()

        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #0B0A12, stop:0.5 #1E1B3A, stop:1 #311042);
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#Card {
                background-color: rgba(26, 24, 48, 0.96);
                border: 2px solid #8B5CF6;
                border-radius: 28px;
                padding: 45px;
            }
            QLabel#HeaderTitle {
                font-size: 42px;
                font-weight: bold;
                color: #C084FC;
            }
            QLabel#SubTitle {
                font-size: 22px;
                color: #E2E8F0;
                line-height: 1.5;
            }
            QPushButton#ActionBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #6D28D9);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 16px;
                padding: 18px 45px;
                border: none;
            }
            QPushButton#ActionBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A855F7, stop:1 #7C3AED);
            }
            QLabel#EmergencyHint {
                font-size: 15px;
                color: #94A3B8;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(720)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(25)

        # Tinted Clock Logo (Purple/White)
        pix = get_tinted_pixmap("clocklogo.png", "#C084FC", QSize(100, 100))
        if pix.isNull():
            pix = get_tinted_pixmap("bullseye-arrowlogo.png", "#C084FC", QSize(100, 100))
        
        if not pix.isNull():
            img_lbl = QLabel()
            img_lbl.setPixmap(pix)
            img_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(img_lbl)

        title = QLabel("⏰ بدأ وقت التعلم الآن!")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(f"حسب جدولك المحدد: ({self.sched_name})\nتم تفعيل حظر التطبيقات الممنوعة لمساعدتك على التركيز.")
        subtitle.setObjectName("SubTitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        # Confirm Button
        self.btn_confirm = QPushButton("حسناً، ابدأ التعلم الآن 🚀")
        self.btn_confirm.setObjectName("ActionBtn")
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.clicked.connect(self.confirm_action)

        hint = QLabel("💡 يمكنك الإغلاق باختصار Alt + F4 للحالات الضرورية")
        hint.setObjectName("EmergencyHint")
        hint.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.btn_confirm)
        card_layout.addWidget(hint)

        main_layout.addWidget(card)

    def confirm_action(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        self.close()

    def closeEvent(self, event):
        """يُستدعى دائماً عند الإغلاق."""
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        if self.on_confirm_callback:
            self.on_confirm_callback()
        self.on_confirm_callback = None
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


class WaterOverlayWindow(QWidget):
    """Full-screen water reminder overlay with tinted water logo & looping sound."""
    def __init__(self, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self.setup_ui()

        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #061A24, stop:0.5 #0369A1, stop:1 #0284C7);
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#Card {
                background-color: rgba(6, 26, 36, 0.96);
                border: 2px solid #38BDF8;
                border-radius: 28px;
                padding: 45px;
            }
            QLabel#HeaderTitle {
                font-size: 40px;
                font-weight: bold;
                color: #38BDF8;
            }
            QLabel#SubTitle {
                font-size: 22px;
                color: #E0F2FE;
            }
            QPushButton#ActionBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 16px;
                padding: 18px 45px;
                border: 1px solid #38BDF8;
            }
            QPushButton#ActionBtn:hover {
                background: #0284C7;
            }
            QLabel#EmergencyHint {
                font-size: 15px;
                color: #93C5FD;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(700)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(25)

        # Tinted Water Logo (Cyan/White) scaled with zero cropping
        pix = get_tinted_pixmap("waterlogo.png", "#38BDF8", QSize(100, 100))
        if not pix.isNull():
            img_lbl = QLabel()
            img_lbl.setPixmap(pix)
            img_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(img_lbl)

        title = QLabel("تذكير صحي: اشرب ماء الآن!")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("مرت 40 دقيقة! شرب الماء يعيد نشاط دماغك ويزيد تركيزك في التعلم.")
        subtitle.setObjectName("SubTitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        self.btn_finish = QPushButton("شربت كوب ماء (+1) 💧")
        self.btn_finish.setObjectName("ActionBtn")
        self.btn_finish.setCursor(Qt.PointingHandCursor)
        self.btn_finish.clicked.connect(self.finish_action)

        hint = QLabel("💡 إغلاق الشاشة: اضغط الزر أعلاه أو Alt + F4 للحالات الضرورية")
        hint.setObjectName("EmergencyHint")
        hint.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.btn_finish)
        card_layout.addWidget(hint)

        main_layout.addWidget(card)

    def finish_action(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        self.close()

    def closeEvent(self, event):
        """يُستدعى دائماً عند الإغلاق — سواء بالزر أو Alt+F4 — لإعادة تعيين الـ flag."""
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        if self.on_finish_callback:
            self.on_finish_callback("water")
        self.on_finish_callback = None  # منع الاستدعاء المزدوج
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


EXERCISES_LIST = [
    {
        "id": "pushups",
        "name": "تمارين الضغط",
        "title": "تحدي اللياقة: 5 تمارين ضغط 🏋️",
        "subtitle": "مرت ساعتان كاملتان!\nقم الآن وأنجز 5 ضغطات لتنشيط الدورة الدموية والجزء العلوي من جسمك.",
        "btn_text": "أنجزت 5 ضغطات! 🏋️",
        "color": "#FB923C",
        "bg_grad": "stop:0 #1C0A00, stop:0.5 #451A03, stop:1 #7C2D12"
    },
    {
        "id": "squats",
        "name": "تمارين السكوات (القرفصاء)",
        "title": "تحدي اللياقة: 8 تمارين سكوات 🦵",
        "subtitle": "حانت لحظة الحركة!\nقف وأنجز 8 تكرارات قرفصاء (Squats) لتجديد نشاط الساقين والجسم.",
        "btn_text": "أنجزت 8 سكوات! 🦵",
        "color": "#60A5FA",
        "bg_grad": "stop:0 #0F172A, stop:0.5 #1E3A8A, stop:1 #1D4ED8"
    },
    {
        "id": "jumping_jacks",
        "name": "تمارين قفز الجاك",
        "title": "تحدي اللياقة: 10 قفزات جاك 🤸",
        "subtitle": "ارفع مستوى اليقظة والتركيز!\nقم بـ 10 قفزات (Jumping Jacks) لزيادة تدفق الأكسجين والدورة الدموية.",
        "btn_text": "أنجزت 10 قفزات! 🤸",
        "color": "#A78BFA",
        "bg_grad": "stop:0 #1E1B4B, stop:0.5 #4C1D95, stop:1 #6D28D9"
    },
    {
        "id": "plank",
        "name": "تمرين البلانك",
        "title": "تحدي اللياقة: 20 ثانية بلانك 🧘",
        "subtitle": "تحدى إرادتك وقوتك الجسدية!\nاثبت في وضعية البلانك (Plank) لمدة 20 ثانية لتقوية عضلات الجذع والظهر.",
        "btn_text": "أنجزت 20 ثانية بلانك! 🧘",
        "color": "#34D399",
        "bg_grad": "stop:0 #064E3B, stop:0.5 #047857, stop:1 #059669"
    },
    {
        "id": "lunges",
        "name": "تمارين الطعن (Lunges)",
        "title": "تحدي اللياقة: 6 تكرارات طعن 🚶",
        "subtitle": "جدد حيوية جسمك وساقيك!\nقم بعمل 6 تكرارات طعن (Lunges) لكل رجل لإعادة الحيوية والتوازن.",
        "btn_text": "أنجزت تكرارات الطعن! 🚶",
        "color": "#F0ABFC",
        "bg_grad": "stop:0 #701A75, stop:0.5 #86198F, stop:1 #A21CAF"
    },
    {
        "id": "stretch",
        "name": "تمارين الإطالة والمد",
        "title": "تحدي اللياقة: 30 ثانية إطالة 🙆",
        "subtitle": "تخلص من الإجهاد العضلي والتعب!\nقم بتمارين إطالة سريعة للرقبة والكتفين لمدة 30 ثانية لتنعم بالاسترخاء.",
        "btn_text": "أنجزت الإطالة! 🙆",
        "color": "#FDBA74",
        "bg_grad": "stop:0 #7C2D12, stop:0.5 #9A3412, stop:1 #C2410C"
    }
]

class ExerciseOverlayWindow(QWidget):
    """Dynamic full-screen exercise reminder overlay rotating through pushups, squats, jacks, plank, lunges & stretching."""
    def __init__(self, exercise_info=None, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback
        if exercise_info is None:
            self.ex_data = EXERCISES_LIST[0]
        else:
            self.ex_data = exercise_info

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self.setup_ui()

        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def setup_ui(self):
        bg_grad = self.ex_data.get("bg_grad", "stop:0 #1C0A00, stop:0.5 #451A03, stop:1 #7C2D12")
        border_col = self.ex_data.get("color", "#FB923C")

        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {bg_grad});
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QFrame#Card {{
                background-color: rgba(15, 10, 25, 0.96);
                border: 2px solid {border_col};
                border-radius: 28px;
                padding: 45px;
            }}
            QLabel#HeaderTitle {{
                font-size: 38px;
                font-weight: bold;
                color: {border_col};
            }}
            QLabel#SubTitle {{
                font-size: 22px;
                color: #F8FAFC;
                line-height: 1.5;
            }}
            QPushButton#ActionBtn {{
                background: {border_col};
                color: #000000;
                font-size: 24px;
                font-weight: bold;
                border-radius: 18px;
                padding: 20px 50px;
                border: none;
            }}
            QPushButton#ActionBtn:hover {{
                opacity: 0.9;
            }}
            QLabel#EmergencyHint {{
                font-size: 15px;
                color: #94A3B8;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(720)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(28)

        pix = get_tinted_pixmap("gymlogo.png", border_col, QSize(105, 105))
        if not pix.isNull():
            img_lbl = QLabel()
            img_lbl.setPixmap(pix)
            img_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(img_lbl)

        title = QLabel(self.ex_data.get("title", "تحدي اللياقة"))
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(self.ex_data.get("subtitle", ""))
        subtitle.setObjectName("SubTitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        self.btn_finish = QPushButton(self.ex_data.get("btn_text", "أنجزت التمرين! 🏋️"))
        self.btn_finish.setObjectName("ActionBtn")
        self.btn_finish.setCursor(Qt.PointingHandCursor)
        self.btn_finish.clicked.connect(self.finish_action)

        hint = QLabel("💡 إغلاق الشاشة: اضغط الزر أعلاه أو Alt + F4 للحالات الضرورية")
        hint.setObjectName("EmergencyHint")
        hint.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.btn_finish)
        card_layout.addWidget(hint)

        main_layout.addWidget(card)

    def finish_action(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        self.close()

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        if self.on_finish_callback:
            self.on_finish_callback("pushups")
        self.on_finish_callback = None
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


class PushupsOverlayWindow(ExerciseOverlayWindow):
    """Backwards compatibility alias for ExerciseOverlayWindow."""
    def __init__(self, audio_mgr=None, on_finish_callback=None):
        super().__init__(exercise_info=EXERCISES_LIST[0], audio_mgr=audio_mgr, on_finish_callback=on_finish_callback)


class PrayerOverlayWindow(QWidget):
    """Full-screen prayer break reminder overlay (5-minute spiritual break)."""
    def __init__(self, prayer_name, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.prayer_name = prayer_name
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback
        self.seconds_left = 300  # 5 minutes

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self.setup_ui()

        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

        from PySide6.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #062016, stop:0.5 #064E3B, stop:1 #047857);
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#Card {
                background-color: rgba(6, 32, 22, 0.96);
                border: 2px solid #10B981;
                border-radius: 28px;
                padding: 45px;
            }
            QLabel#HeaderTitle {
                font-size: 38px;
                font-weight: bold;
                color: #34D399;
            }
            QLabel#SubTitle {
                font-size: 22px;
                color: #D1FAE5;
                line-height: 1.5;
            }
            QPushButton#ActionBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
                color: white;
                font-size: 22px;
                font-weight: bold;
                border-radius: 18px;
                padding: 18px 45px;
                border: none;
            }
            QPushButton#ActionBtn:hover {
                background: #059669;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(720)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(24)

        pix = get_tinted_pixmap("clocklogo.png", "#34D399", QSize(100, 100))
        if not pix.isNull():
            img_lbl = QLabel()
            img_lbl.setPixmap(pix)
            img_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(img_lbl)

        title = QLabel(f"🕌 حانت الآن صلاة {self.prayer_name}")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("تم حظر جميع الألعاب والمشتتات لمدة 5 دقائق لأداء الصلاة خشوعاً وحضوراً.")
        subtitle.setObjectName("SubTitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        self.lbl_countdown = QLabel("المتبقي لاستئناف العمل: 05:00")
        self.lbl_countdown.setStyleSheet("font-size: 20px; font-weight: bold; color: #F59E0B;")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)

        self.btn_finish = QPushButton("تقبّل الله (إغلاق التنبيه) 🕌")
        self.btn_finish.setObjectName("ActionBtn")
        self.btn_finish.setCursor(Qt.PointingHandCursor)
        self.btn_finish.clicked.connect(self.finish_action)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.lbl_countdown)
        card_layout.addWidget(self.btn_finish)

        main_layout.addWidget(card)

    def update_countdown(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            m = self.seconds_left // 60
            s = self.seconds_left % 60
            self.lbl_countdown.setText(f"المتبقي لاستئناف العمل: {m:02d}:{s:02d}")
        else:
            self.lbl_countdown.setText("انتهت استراحة الصلاة! تقبل الله طاعتكم 🤲")

    def finish_action(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        self.close()

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        if self.on_finish_callback:
            self.on_finish_callback("prayer")
        self.on_finish_callback = None
        super().closeEvent(event)

