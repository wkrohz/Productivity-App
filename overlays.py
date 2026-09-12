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


class PushupsOverlayWindow(QWidget):
    """Completely redesigned Push-ups full-screen overlay with tinted logo, simple single action button, and high UX."""
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
        # Ultra Modern Dark Amber / Orange Gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #1C0A00, stop:0.5 #451A03, stop:1 #7C2D12);
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#Card {
                background-color: rgba(28, 10, 0, 0.96);
                border: 2px solid #FB923C;
                border-radius: 28px;
                padding: 45px;
            }
            QLabel#HeaderTitle {
                font-size: 40px;
                font-weight: bold;
                color: #FB923C;
            }
            QLabel#SubTitle {
                font-size: 22px;
                color: #FFEDD5;
                line-height: 1.5;
            }
            QPushButton#ActionBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EA580C, stop:1 #C2410C);
                color: white;
                font-size: 25px;
                font-weight: bold;
                border-radius: 18px;
                padding: 20px 50px;
                border: 1px solid #FB923C;
            }
            QPushButton#ActionBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F97316, stop:1 #EA580C);
            }
            QLabel#EmergencyHint {
                font-size: 15px;
                color: #FDBA74;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(720)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(28)

        # Tinted Gym Logo (Orange/White) scaled with zero cropping
        pix = get_tinted_pixmap("gymlogo.png", "#FB923C", QSize(105, 105))
        if not pix.isNull():
            img_lbl = QLabel()
            img_lbl.setPixmap(pix)
            img_lbl.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(img_lbl)

        title = QLabel("تحدي اللياقة: قم بعمل 5 تمارين ضغط!")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("مرت ساعتان كاملتان!\nقم الآن وأنجز 5 ضغطات لتنشيط الدورة الدموية وتجديد طاقتك الذهنية.")
        subtitle.setObjectName("SubTitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)

        # Simple, clear single action button as requested
        self.btn_finish = QPushButton("أنجزت 5 ضغطات! 🏋️")
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
        """يُستدعى دائماً عند الإغلاق — سواء بالزر أو Alt+F4."""
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
