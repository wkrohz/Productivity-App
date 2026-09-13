import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QLinearGradient, QPen, QBrush, QRadialGradient
from asset_helper import get_tinted_pixmap


# ─────────────────────────────────────────────────────────────────────────────
#  Helper: glowing drop shadow
# ─────────────────────────────────────────────────────────────────────────────
def _glow(widget, color="#8B5CF6", radius=40, offset=0):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(radius)
    eff.setColor(QColor(color))
    eff.setOffset(offset, offset)
    widget.setGraphicsEffect(eff)
    return eff


# ─────────────────────────────────────────────────────────────────────────────
#  Animated pulsing ring widget
# ─────────────────────────────────────────────────────────────────────────────
class PulsingRing(QWidget):
    """Draws an animated pulsing circle behind the icon."""
    def __init__(self, color="#8B5CF6", size=160, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.ring_size = size
        self.setFixedSize(size, size)
        self._scale = 0.7
        self._alpha = 220

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(40)
        self._growing = True

    def _tick(self):
        step = 0.008
        if self._growing:
            self._scale += step
            self._alpha = max(80, self._alpha - 3)
            if self._scale >= 1.0:
                self._growing = False
        else:
            self._scale -= step
            self._alpha = min(220, self._alpha + 3)
            if self._scale <= 0.7:
                self._growing = True
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self.ring_size
        margin = int(s * (1 - self._scale) / 2)
        rect = QRect(margin, margin, s - 2 * margin, s - 2 * margin)

        # outer glow ring
        glow_col = QColor(self.color)
        glow_col.setAlpha(30)
        p.setPen(QPen(glow_col, 14))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(rect)

        # inner fill circle
        fill = QColor(self.color)
        fill.setAlpha(self._alpha)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(fill))
        inner = rect.adjusted(18, 18, -18, -18)
        p.drawEllipse(inner)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  Base overlay — shared dark glassmorphism card layout
# ─────────────────────────────────────────────────────────────────────────────
class BaseOverlay(QWidget):
    ACCENT      = "#8B5CF6"
    BG_STOPS    = "stop:0 #0B0A12, stop:0.5 #1E1B3A, stop:1 #311042"
    CARD_BG     = "rgba(18, 16, 38, 0.97)"
    EMOJI       = "🔔"
    LOGO_FILE   = "clocklogo.png"

    def __init__(self, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self._build_base_style()
        self._build_ui()
        self._post_init()

    # Override in subclasses ──────────────────────────────────────────────────
    def _post_init(self): pass
    def _card_content(self, card_layout): pass

    def _build_base_style(self):
        self.setStyleSheet(f"""
            QWidget#BaseRoot {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {self.BG_STOPS});
            }}
            QFrame#Card {{
                background-color: {self.CARD_BG};
                border: 1.5px solid rgba(255,255,255,0.08);
                border-radius: 32px;
            }}
            QLabel#Title {{
                font-size: 36px;
                font-weight: 900;
                color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#SubTitle {{
                font-size: 19px;
                color: rgba(226, 232, 240, 0.88);
                line-height: 1.7;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Hint {{
                font-size: 13px;
                color: rgba(148, 163, 184, 0.70);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#PrimaryBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT}, stop:1 {self._darken(self.ACCENT)});
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
                border-radius: 18px;
                padding: 16px 52px;
                border: none;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#PrimaryBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self._lighten(self.ACCENT)}, stop:1 {self.ACCENT});
            }}
            QPushButton#PrimaryBtn:pressed {{
                padding: 14px 52px 18px;
            }}
        """)

    @staticmethod
    def _darken(hex_col):
        c = QColor(hex_col)
        h, s, v, a = c.getHsvF()
        c.setHsvF(h, s, max(0, v - 0.15), a)
        return c.name()

    @staticmethod
    def _lighten(hex_col):
        c = QColor(hex_col)
        h, s, v, a = c.getHsvF()
        c.setHsvF(h, max(0, s - 0.1), min(1, v + 0.12), a)
        return c.name()

    def _build_ui(self):
        root_frame = QWidget(self)
        root_frame.setObjectName("BaseRoot")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(root_frame)

        outer = QVBoxLayout(root_frame)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(760)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Card shadow / glow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(self.ACCENT + "80"))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(52, 48, 52, 48)

        # Icon area (pulsing ring + logo)
        icon_row = QHBoxLayout()
        icon_row.setAlignment(Qt.AlignCenter)

        ring_container = QWidget()
        ring_container.setFixedSize(140, 140)
        ring_layout = QVBoxLayout(ring_container)
        ring_layout.setContentsMargins(0, 0, 0, 0)

        self.ring = PulsingRing(self.ACCENT, 140)
        ring_layout.addWidget(self.ring)

        # Logo on top of ring
        pix = get_tinted_pixmap(self.LOGO_FILE, "#FFFFFF", QSize(70, 70))
        if pix.isNull():
            pix = get_tinted_pixmap("clocklogo.png", "#FFFFFF", QSize(70, 70))

        if not pix.isNull():
            logo_lbl = QLabel(ring_container)
            logo_lbl.setPixmap(pix)
            logo_lbl.setAlignment(Qt.AlignCenter)
            logo_lbl.setGeometry(35, 35, 70, 70)

        icon_row.addWidget(ring_container)
        card_layout.addLayout(icon_row)

        # Accent top bar
        accent_bar = QFrame()
        accent_bar.setFixedHeight(3)
        accent_bar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.3 {self.ACCENT},
                stop:0.7 {self.ACCENT}, stop:1 transparent);
            border-radius: 2px;
        """)
        card_layout.addWidget(accent_bar)

        self._card_content(card_layout)

        # Emergency hint
        hint = QLabel("Alt + F4 للحالات الضرورية فقط")
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(hint)

        outer.addWidget(card)

    def _make_info_box(self, text, bg="rgba(255,255,255,0.05)", border_color=None):
        """Creates a styled info/dhikr box."""
        if border_color is None:
            border_color = self.ACCENT
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border_color}55;
                border-radius: 16px;
                padding: 12px 20px;
            }}
        """)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 16px;
            color: rgba(224, 242, 254, 0.92);
            font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            line-height: 1.7;
        """)
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        lay = QVBoxLayout(box)
        lay.addWidget(lbl)
        return box

    def _make_primary_btn(self, text):
        btn = QPushButton(text)
        btn.setObjectName("PrimaryBtn")
        btn.setCursor(Qt.PointingHandCursor)
        _glow(btn, self.ACCENT, 35)
        return btn

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        if cb:
            cb("closed")
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  1. Schedule / Study Session Overlay
# ─────────────────────────────────────────────────────────────────────────────
class StartScheduleOverlayWindow(BaseOverlay):
    ACCENT   = "#8B5CF6"
    BG_STOPS = "stop:0 #060410, stop:0.45 #120E30, stop:1 #1E0B35"
    CARD_BG  = "rgba(14, 10, 32, 0.98)"
    LOGO_FILE = "clocklogo.png"

    def __init__(self, sched_name, audio_mgr=None, on_confirm_callback=None):
        self.sched_name = sched_name
        self._confirm_cb = on_confirm_callback
        super().__init__(audio_mgr=audio_mgr, on_finish_callback=None)

    def _post_init(self):
        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def _card_content(self, lay):
        # Badge
        badge = QLabel("⏰  جلسة التعلم المجدولة")
        badge.setStyleSheet(f"""
            background: {self.ACCENT}22; color: {self.ACCENT};
            border: 1px solid {self.ACCENT}55; border-radius: 20px;
            padding: 6px 20px; font-size: 14px; font-weight: bold;
            font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
        """)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        lay.addWidget(badge)

        title = QLabel(f"بدأ وقت التعلم الآن!")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        sub = QLabel(f"جدولك المحدد:  «  {self.sched_name}  »\nتم تفعيل حظر التطبيقات الممنوعة لمساعدتك على التركيز الكامل.")
        sub.setObjectName("SubTitle")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        # Tips row
        tips_row = QHBoxLayout()
        for icon, tip in [("🚫", "الألعاب محظورة"), ("📵", "المشتتات مغلقة"), ("🚀", "وقت الإنجاز")]:
            tip_w = QFrame()
            tip_w.setStyleSheet(f"""
                QFrame {{
                    background: rgba(139, 92, 246, 0.10);
                    border: 1px solid rgba(139, 92, 246, 0.25);
                    border-radius: 12px;
                    padding: 10px;
                }}
            """)
            tip_lay = QVBoxLayout(tip_w)
            tip_lay.setSpacing(4)
            e_lbl = QLabel(icon)
            e_lbl.setAlignment(Qt.AlignCenter)
            e_lbl.setStyleSheet("font-size: 26px;")
            t_lbl = QLabel(tip)
            t_lbl.setAlignment(Qt.AlignCenter)
            t_lbl.setStyleSheet("font-size: 13px; color: rgba(200,200,220,0.85); font-family: 'Segoe UI', Tahoma;")
            tip_lay.addWidget(e_lbl)
            tip_lay.addWidget(t_lbl)
            tips_row.addWidget(tip_w)
        lay.addLayout(tips_row)

        self.btn = self._make_primary_btn("حسناً، ابدأ التعلم الآن  🚀")
        self.btn.clicked.connect(self._confirm)
        lay.addWidget(self.btn, alignment=Qt.AlignCenter)

    def _confirm(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self._confirm_cb
        self._confirm_cb = None
        self.on_finish_callback = None
        self.close()
        if cb:
            cb()

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        super(BaseOverlay, self).closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  2. Water Reminder Overlay
# ─────────────────────────────────────────────────────────────────────────────
class WaterOverlayWindow(BaseOverlay):
    ACCENT   = "#0EA5E9"
    BG_STOPS = "stop:0 #030D14, stop:0.5 #052940, stop:1 #0369A1"
    CARD_BG  = "rgba(3, 13, 25, 0.98)"
    LOGO_FILE = "waterlogo.png"

    def _post_init(self):
        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def _card_content(self, lay):
        badge = QLabel("💧  تذكير صحي")
        badge.setStyleSheet(f"""
            background: {self.ACCENT}22; color: {self.ACCENT};
            border: 1px solid {self.ACCENT}55; border-radius: 20px;
            padding: 6px 20px; font-size: 14px; font-weight: bold;
            font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
        """)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        lay.addWidget(badge)

        title = QLabel("اشرب ماءً الآن!")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("مرّت 40 دقيقة على آخر شرب للماء 💦\nشرب الماء يُعيد نشاط دماغك ويرفع مستوى تركيزك.")
        sub.setObjectName("SubTitle")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        # Benefits row
        benefits = [("🧠", "دماغ أنشط"), ("⚡", "طاقة أعلى"), ("👁️", "عيون مرتاحة")]
        row = QHBoxLayout()
        for icon, label in benefits:
            w = QFrame()
            w.setStyleSheet(f"""
                QFrame {{
                    background: rgba(14, 165, 233, 0.10);
                    border: 1px solid rgba(14, 165, 233, 0.28);
                    border-radius: 14px;
                    padding: 12px 8px;
                }}
            """)
            wl = QVBoxLayout(w)
            wl.setSpacing(5)
            il = QLabel(icon)
            il.setAlignment(Qt.AlignCenter)
            il.setStyleSheet("font-size: 28px;")
            tl = QLabel(label)
            tl.setAlignment(Qt.AlignCenter)
            tl.setStyleSheet("font-size: 13px; color: rgba(186, 230, 253, 0.85); font-family: 'Segoe UI', Tahoma;")
            wl.addWidget(il)
            wl.addWidget(tl)
            row.addWidget(w)
        lay.addLayout(row)

        # Water count context
        info = self._make_info_box(
            "«  وَجَعَلْنَا مِنَ الْمَاءِ كُلَّ شَيْءٍ حَيٍّ  »  —  سورة الأنبياء",
            bg="rgba(14,165,233,0.07)",
            border_color=self.ACCENT
        )
        lay.addWidget(info)

        self.btn = self._make_primary_btn("شربت كوب ماء  (+1)  💧")
        self.btn.clicked.connect(self._done)
        lay.addWidget(self.btn, alignment=Qt.AlignCenter)

    def _done(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        self.close()
        if cb:
            cb("water")

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        if cb:
            cb("water")
        super(BaseOverlay, self).closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  3. Exercise Overlays
# ─────────────────────────────────────────────────────────────────────────────
EXERCISES_LIST = [
    {
        "id": "pushups",
        "name": "تمارين الضغط",
        "emoji": "🏋️",
        "title": "5 تمارين ضغط",
        "subtitle": "مرت ساعتان كاملتان!\nقم الآن وأنجز 5 ضغطات لتنشيط الدورة الدموية والجزء العلوي من جسمك.",
        "btn_text": "أنجزت 5 ضغطات!  🏋️",
        "color": "#FB923C",
        "bg_stops": "stop:0 #0D0500, stop:0.5 #2D1000, stop:1 #4A1808",
        "card_bg": "rgba(13, 5, 0, 0.98)"
    },
    {
        "id": "squats",
        "name": "القرفصاء",
        "emoji": "🦵",
        "title": "8 تمارين سكوات",
        "subtitle": "حانت لحظة الحركة!\nقف وأنجز 8 تكرارات قرفصاء لتجديد نشاط الساقين والجسم.",
        "btn_text": "أنجزت 8 سكوات!  🦵",
        "color": "#60A5FA",
        "bg_stops": "stop:0 #030810, stop:0.5 #0B1A3A, stop:1 #0F2060",
        "card_bg": "rgba(3, 8, 16, 0.98)"
    },
    {
        "id": "jumping_jacks",
        "name": "قفز الجاك",
        "emoji": "🤸",
        "title": "10 قفزات جاك",
        "subtitle": "ارفع مستوى اليقظة والتركيز!\nقم بـ 10 قفزات لزيادة تدفق الأكسجين وإعادة النشاط.",
        "btn_text": "أنجزت 10 قفزات!  🤸",
        "color": "#A78BFA",
        "bg_stops": "stop:0 #080612, stop:0.5 #1A1040, stop:1 #2D1680",
        "card_bg": "rgba(8, 6, 18, 0.98)"
    },
    {
        "id": "plank",
        "name": "البلانك",
        "emoji": "🧘",
        "title": "20 ثانية بلانك",
        "subtitle": "تحدى إرادتك وقوتك الجسدية!\nاثبت في وضعية البلانك لمدة 20 ثانية لتقوية عضلات الجذع.",
        "btn_text": "أنجزت 20 ثانية بلانك!  🧘",
        "color": "#34D399",
        "bg_stops": "stop:0 #020E08, stop:0.5 #052D1A, stop:1 #065E30",
        "card_bg": "rgba(2, 14, 8, 0.98)"
    },
    {
        "id": "lunges",
        "name": "تمارين الطعن",
        "emoji": "🚶",
        "title": "6 تكرارات طعن",
        "subtitle": "جدد حيوية جسمك وساقيك!\nقم بعمل 6 تكرارات طعن لكل رجل لإعادة الحيوية والتوازن.",
        "btn_text": "أنجزت تكرارات الطعن!  🚶",
        "color": "#F0ABFC",
        "bg_stops": "stop:0 #120318, stop:0.5 #320845, stop:1 #6B1280",
        "card_bg": "rgba(18, 3, 24, 0.98)"
    },
    {
        "id": "stretch",
        "name": "الإطالة والمد",
        "emoji": "🙆",
        "title": "30 ثانية إطالة",
        "subtitle": "تخلص من الإجهاد العضلي والتعب!\nقم بتمارين إطالة سريعة للرقبة والكتفين لتنعم بالاسترخاء.",
        "btn_text": "أنجزت الإطالة!  🙆",
        "color": "#FDBA74",
        "bg_stops": "stop:0 #0D0500, stop:0.5 #2C0E00, stop:1 #5C2000",
        "card_bg": "rgba(13, 5, 0, 0.98)"
    }
]


class ExerciseOverlayWindow(QWidget):
    """Dynamic full-screen exercise overlay — premium redesign."""

    def __init__(self, exercise_info=None, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback
        self.ex = exercise_info or EXERCISES_LIST[0]

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self._setup()

        if self.audio_mgr:
            self.audio_mgr.play_loop_alarm()

    def _setup(self):
        accent = self.ex["color"]
        bg_stops = self.ex.get("bg_stops", "stop:0 #0D0500, stop:0.5 #2D1000, stop:1 #4A1808")
        card_bg = self.ex.get("card_bg", "rgba(13,5,0,0.98)")

        self.setStyleSheet(f"""
            QWidget#ExRoot {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, {bg_stops});
            }}
            QFrame#Card {{
                background-color: {card_bg};
                border: 1.5px solid rgba(255,255,255,0.07);
                border-radius: 32px;
            }}
            QLabel#Badge {{
                background: {accent}22; color: {accent};
                border: 1px solid {accent}55; border-radius: 20px;
                padding: 6px 20px; font-size: 14px; font-weight: bold;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Title {{
                font-size: 36px; font-weight: 900; color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Sub {{
                font-size: 19px; color: rgba(226,232,240,0.88);
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {accent}, stop:1 {accent}BB);
                color: #0A0A0A; font-size: 20px; font-weight: bold;
                border-radius: 18px; padding: 16px 52px; border: none;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn:hover {{ background: {accent}EE; }}
            QLabel#Hint {{
                font-size: 13px; color: rgba(148,163,184,0.65);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
        """)

        root = QWidget(self)
        root.setObjectName("ExRoot")
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.addWidget(root)

        outer = QVBoxLayout(root)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(780)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(accent + "80"))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setAlignment(Qt.AlignCenter)
        cl.setSpacing(18)
        cl.setContentsMargins(52, 46, 52, 46)

        # Pulsing ring + emoji
        ring_container = QWidget()
        ring_container.setFixedSize(140, 140)
        self.ring = PulsingRing(accent, 140)
        rl = QVBoxLayout(ring_container)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.ring)
        emoji_lbl = QLabel(self.ex.get("emoji", "🏋️"), ring_container)
        emoji_lbl.setAlignment(Qt.AlignCenter)
        emoji_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        emoji_lbl.setGeometry(20, 30, 100, 80)

        cl.addWidget(ring_container, alignment=Qt.AlignCenter)

        # Accent bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {accent},
                stop:0.7 {accent}, stop:1 transparent);
            border-radius: 2px;
        """)
        cl.addWidget(bar)

        # Badge
        badge = QLabel(f"🏃  تحدي اللياقة")
        badge.setObjectName("Badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        cl.addWidget(badge)

        title = QLabel(self.ex.get("title", ""))
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel(self.ex.get("subtitle", ""))
        sub.setObjectName("Sub")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Steps row
        steps = self._steps_row(accent)
        cl.addLayout(steps)

        btn = QPushButton(self.ex.get("btn_text", "أنجزت التمرين!"))
        btn.setObjectName("Btn")
        btn.setCursor(Qt.PointingHandCursor)
        glow = QGraphicsDropShadowEffect(btn)
        glow.setBlurRadius(35)
        glow.setColor(QColor(accent + "90"))
        glow.setOffset(0, 0)
        btn.setGraphicsEffect(glow)
        btn.clicked.connect(self._done)
        cl.addWidget(btn, alignment=Qt.AlignCenter)

        hint = QLabel("Alt + F4 للحالات الضرورية فقط")
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        cl.addWidget(hint)

        outer.addWidget(card)

    def _steps_row(self, accent):
        row = QHBoxLayout()
        steps = [
            ("1️⃣", "قف واستعد"),
            ("2️⃣", "نفّذ التمرين"),
            ("3️⃣", "استرح وعد للعمل"),
        ]
        for num, step in steps:
            w = QFrame()
            w.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255,255,255,0.04);
                    border: 1px solid {accent}33;
                    border-radius: 14px;
                    padding: 10px 6px;
                }}
            """)
            wl = QVBoxLayout(w)
            wl.setSpacing(4)
            nl = QLabel(num)
            nl.setAlignment(Qt.AlignCenter)
            nl.setStyleSheet("font-size: 22px;")
            sl = QLabel(step)
            sl.setAlignment(Qt.AlignCenter)
            sl.setStyleSheet(f"font-size: 13px; color: rgba(200,210,220,0.80); font-family: 'Segoe UI', Tahoma;")
            wl.addWidget(nl)
            wl.addWidget(sl)
            row.addWidget(w)
        return row

    def _done(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        self.close()
        if cb:
            cb("pushups")

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        if cb:
            cb("pushups")
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


class PushupsOverlayWindow(ExerciseOverlayWindow):
    def __init__(self, audio_mgr=None, on_finish_callback=None):
        super().__init__(exercise_info=EXERCISES_LIST[0], audio_mgr=audio_mgr, on_finish_callback=on_finish_callback)


# ─────────────────────────────────────────────────────────────────────────────
#  4. Prayer Reminder Overlay
# ─────────────────────────────────────────────────────────────────────────────
class PrayerOverlayWindow(QWidget):
    ACCENT   = "#10B981"
    BG_STOPS = "stop:0 #020E08, stop:0.45 #042418, stop:1 #053D28"
    CARD_BG  = "rgba(2, 14, 8, 0.98)"

    PRAYER_DHIKR = {
        "الفجر":   ("إِنَّ قُرْآنَ الْفَجْرِ كَانَ مَشْهُودًا", "أفضل أوقات تلاوة القرآن — قم وصلّ ركعتَي الفجر قبل الفريضة 🌙"),
        "الظهر":   ("أَقِمِ الصَّلَاةَ لِذِكْرِي", "انقطع لله لحظات في وسط يومك — صلّ وسبّح واذكر الله 🤲"),
        "العصر":   ("حَافِظُوا عَلَى الصَّلَوَاتِ وَالصَّلَاةِ الْوُسْطَىٰ", "صلاة العصر خير من الدنيا وما فيها — لا تفوّتها ☀️"),
        "المغرب":  ("فَسُبْحَانَ اللَّهِ حِينَ تُمْسُونَ وَحِينَ تُصْبِحُونَ", "أدِّ صلاة المغرب وسبّح الله عند مساء يومك 🌅"),
        "العشاء":  ("وَمِنَ اللَّيْلِ فَتَهَجَّدْ بِهِ نَافِلَةً لَّكَ", "اختم يومك بذكر الله — صلّ العشاء واقرأ آية الكرسي 🌙"),
    }

    def __init__(self, prayer_name, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.prayer_name = prayer_name
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback
        self.seconds_left = 300

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self._setup()

        if self.audio_mgr:
            if hasattr(self.audio_mgr, "play_prayer_alarm"):
                self.audio_mgr.play_prayer_alarm()
            else:
                self.audio_mgr.play_loop_alarm()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _setup(self):
        accent = self.ACCENT
        self.setStyleSheet(f"""
            QWidget#PRoot {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,{self.BG_STOPS});
            }}
            QFrame#Card {{
                background-color: {self.CARD_BG};
                border: 1.5px solid rgba(255,255,255,0.07);
                border-radius: 32px;
            }}
            QLabel#Badge {{
                background: {accent}22; color: {accent};
                border: 1px solid {accent}55; border-radius: 20px;
                padding: 6px 20px; font-size: 14px; font-weight: bold;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Title {{
                font-size: 38px; font-weight: 900; color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Sub {{
                font-size: 19px; color: rgba(209,250,229,0.88);
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Verse {{
                font-size: 22px; font-weight: bold; color: #6EE7B7;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#DhikrText {{
                font-size: 15px; color: rgba(209,250,229,0.80);
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#CountdownLbl {{
                font-size: 44px; font-weight: 900; color: #FBBF24;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#CountdownSub {{
                font-size: 14px; color: rgba(251,191,36,0.70);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {accent}, stop:1 #059669);
                color: #FFFFFF; font-size: 20px; font-weight: bold;
                border-radius: 18px; padding: 16px 52px; border: none;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn:hover {{ background: #059669; }}
            QLabel#Hint {{
                font-size: 13px; color: rgba(148,163,184,0.65);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
        """)

        root = QWidget(self)
        root.setObjectName("PRoot")
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(root)

        outer = QVBoxLayout(root)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(780)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(90)
        shadow.setColor(QColor(accent + "70"))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setAlignment(Qt.AlignCenter)
        cl.setSpacing(18)
        cl.setContentsMargins(52, 46, 52, 46)

        # Ring + crescent emoji
        ring_c = QWidget()
        ring_c.setFixedSize(140, 140)
        self.ring = PulsingRing(accent, 140)
        rl = QVBoxLayout(ring_c)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.ring)
        moon = QLabel("🕌", ring_c)
        moon.setAlignment(Qt.AlignCenter)
        moon.setStyleSheet("font-size: 50px; background: transparent;")
        moon.setGeometry(20, 28, 100, 84)
        cl.addWidget(ring_c, alignment=Qt.AlignCenter)

        # Accent bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {accent},
                stop:0.7 {accent}, stop:1 transparent);
            border-radius: 2px;
        """)
        cl.addWidget(bar)

        badge = QLabel(f"🕌  وقت الصلاة")
        badge.setObjectName("Badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        cl.addWidget(badge)

        title = QLabel(f"حانت الآن صلاة {self.prayer_name}")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("تم حظر جميع الألعاب والمشتتات\nاستعدّ لأداء الصلاة بخشوع وحضور قلب 🤲")
        sub.setObjectName("Sub")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Dhikr box
        verse_text, dhikr_text = self.PRAYER_DHIKR.get(
            self.prayer_name,
            ("أَقِمِ الصَّلَاةَ لِذِكْرِي", "« أستغفر الله (3) — سبحان الله (33) — الحمد لله (33) — الله أكبر (33) »")
        )
        dhikr_box = QFrame()
        dhikr_box.setStyleSheet(f"""
            QFrame {{
                background: rgba(16,185,129,0.07);
                border: 1px solid rgba(52,211,153,0.28);
                border-radius: 18px;
                padding: 16px 20px;
            }}
        """)
        dl = QVBoxLayout(dhikr_box)
        dl.setSpacing(8)
        verse_lbl = QLabel(f"﴿  {verse_text}  ﴾")
        verse_lbl.setObjectName("Verse")
        verse_lbl.setAlignment(Qt.AlignCenter)
        verse_lbl.setWordWrap(True)
        dhikr_lbl = QLabel(dhikr_text)
        dhikr_lbl.setObjectName("DhikrText")
        dhikr_lbl.setAlignment(Qt.AlignCenter)
        dhikr_lbl.setWordWrap(True)
        dl.addWidget(verse_lbl)
        dl.addWidget(dhikr_lbl)
        cl.addWidget(dhikr_box)

        # Countdown
        cd_frame = QFrame()
        cd_frame.setStyleSheet("""
            QFrame {
                background: rgba(251,191,36,0.06);
                border: 1px solid rgba(251,191,36,0.22);
                border-radius: 16px;
                padding: 14px;
            }
        """)
        cd_lay = QVBoxLayout(cd_frame)
        cd_lay.setSpacing(4)
        self.lbl_countdown = QLabel("05:00")
        self.lbl_countdown.setObjectName("CountdownLbl")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        cd_sub = QLabel("المتبقي قبل استئناف النشاط")
        cd_sub.setObjectName("CountdownSub")
        cd_sub.setAlignment(Qt.AlignCenter)
        cd_lay.addWidget(self.lbl_countdown)
        cd_lay.addWidget(cd_sub)
        cl.addWidget(cd_frame)

        self.btn = QPushButton("تقبّل الله  ·  إغلاق التنبيه  🤲")
        self.btn.setObjectName("Btn")
        self.btn.setCursor(Qt.PointingHandCursor)
        glow = QGraphicsDropShadowEffect(self.btn)
        glow.setBlurRadius(35)
        glow.setColor(QColor(accent + "90"))
        glow.setOffset(0, 0)
        self.btn.setGraphicsEffect(glow)
        self.btn.clicked.connect(self._done)
        cl.addWidget(self.btn, alignment=Qt.AlignCenter)

        hint = QLabel("Alt + F4 للحالات الضرورية فقط")
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        cl.addWidget(hint)

        outer.addWidget(card)

    def _tick(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            m = self.seconds_left // 60
            s = self.seconds_left % 60
            self.lbl_countdown.setText(f"{m:02d}:{s:02d}")
        else:
            self._timer.stop()
            self.lbl_countdown.setText("✓  تقبّل الله طاعتكم 🤲")
            self.lbl_countdown.setStyleSheet("font-size: 36px; font-weight: 900; color: #34D399; font-family: 'Madika Arabic TRIAL', 'Segoe UI', sans-serif;")
            self.btn.setText("✓ اكتمل وقت الصلاة (5 دقائق)  ·  إغلاق وتوقف الانذار  🤲")
            self.btn.setStyleSheet("""
                QPushButton#Btn {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #10B981, stop:1 #059669);
                    color: #FFFFFF; font-size: 20px; font-weight: bold;
                    border-radius: 18px; padding: 16px 52px; border: 2px solid #6EE7B7;
                }
                QPushButton#Btn:hover { background: #059669; }
            """)

    def _done(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        self.close()
        if cb:
            cb("prayer")

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        if cb:
            cb("prayer")
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  5. Eye Rest Overlay (20-20-20)
# ─────────────────────────────────────────────────────────────────────────────
class EyeRestOverlayWindow(QWidget):
    ACCENT   = "#06B6D4"
    BG_STOPS = "stop:0 #020C10, stop:0.5 #042035, stop:1 #053048"
    CARD_BG  = "rgba(2, 12, 16, 0.98)"

    def __init__(self, audio_mgr=None, on_finish_callback=None):
        super().__init__()
        self.audio_mgr = audio_mgr
        self.on_finish_callback = on_finish_callback
        self.seconds_left = 20

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self._setup()

        if self.audio_mgr:
            if hasattr(self.audio_mgr, "play_eye_rest_alarm"):
                self.audio_mgr.play_eye_rest_alarm()
            elif hasattr(self.audio_mgr, "play_water_alarm"):
                self.audio_mgr.play_water_alarm()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _setup(self):
        accent = self.ACCENT
        self.setStyleSheet(f"""
            QWidget#ERoot {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,{self.BG_STOPS});
            }}
            QFrame#Card {{
                background-color: {self.CARD_BG};
                border: 1.5px solid rgba(255,255,255,0.07);
                border-radius: 32px;
            }}
            QLabel#Badge {{
                background: {accent}22; color: {accent};
                border: 1px solid {accent}55; border-radius: 20px;
                padding: 6px 20px; font-size: 14px; font-weight: bold;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Title {{
                font-size: 34px; font-weight: 900; color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Sub {{
                font-size: 18px; color: rgba(207,250,254,0.85);
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#BigCount {{
                font-size: 86px; font-weight: 900; color: #FBBF24;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#CountSub {{
                font-size: 16px; color: rgba(251,191,36,0.65);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {accent}, stop:1 #0284C7);
                color: #FFFFFF; font-size: 18px; font-weight: bold;
                border-radius: 16px; padding: 14px 48px; border: none;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn:hover {{ background: #0891B2; }}
            QPushButton#Btn:disabled {{
                background: rgba(51, 65, 85, 0.6);
                color: rgba(148, 163, 184, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QLabel#Hint {{
                font-size: 13px; color: rgba(148,163,184,0.60);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
        """)

        root = QWidget(self)
        root.setObjectName("ERoot")
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(root)

        outer = QVBoxLayout(root)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(700)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(accent + "70"))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setAlignment(Qt.AlignCenter)
        cl.setSpacing(18)
        cl.setContentsMargins(50, 44, 50, 44)

        # Ring + emoji
        ring_c = QWidget()
        ring_c.setFixedSize(130, 130)
        self.ring = PulsingRing(accent, 130)
        rl = QVBoxLayout(ring_c)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.ring)
        eye_lbl = QLabel("👀", ring_c)
        eye_lbl.setAlignment(Qt.AlignCenter)
        eye_lbl.setStyleSheet("font-size: 46px; background: transparent;")
        eye_lbl.setGeometry(18, 28, 94, 74)
        cl.addWidget(ring_c, alignment=Qt.AlignCenter)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {accent},
                stop:0.7 {accent}, stop:1 transparent);
            border-radius: 2px;
        """)
        cl.addWidget(bar)

        badge = QLabel("👁️  قاعدة 20-20-20")
        badge.setObjectName("Badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        cl.addWidget(badge)

        title = QLabel("استراحة العينين والجسم")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("انظر إلى مكان بعيد وأرِح عينيك\nافرد ظهرك واسترخِ — جسمك يشكرك 🌿")
        sub.setObjectName("Sub")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Big countdown
        cd_frame = QFrame()
        cd_frame.setStyleSheet("""
            QFrame {
                background: rgba(251,191,36,0.05);
                border: 1px solid rgba(251,191,36,0.20);
                border-radius: 20px;
                padding: 10px;
            }
        """)
        cd_l = QVBoxLayout(cd_frame)
        cd_l.setSpacing(2)
        self.lbl_countdown = QLabel("20")
        self.lbl_countdown.setObjectName("BigCount")
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        cd_sub_lbl = QLabel("ثانية متبقية")
        cd_sub_lbl.setObjectName("CountSub")
        cd_sub_lbl.setAlignment(Qt.AlignCenter)
        cd_l.addWidget(self.lbl_countdown)
        cd_l.addWidget(cd_sub_lbl)
        cl.addWidget(cd_frame)

        # Tips
        tips_row = QHBoxLayout()
        for icon, tip in [("👁️", "انظر بعيداً 6م+"), ("🪑", "استقم في كرسيك"), ("🌬️", "خذ نفساً عميقاً")]:
            w = QFrame()
            w.setStyleSheet(f"""
                QFrame {{
                    background: rgba(6,182,212,0.07);
                    border: 1px solid rgba(6,182,212,0.22);
                    border-radius: 12px;
                    padding: 10px 6px;
                }}
            """)
            wl = QVBoxLayout(w)
            wl.setSpacing(4)
            il = QLabel(icon)
            il.setAlignment(Qt.AlignCenter)
            il.setStyleSheet("font-size: 22px;")
            tl = QLabel(tip)
            tl.setAlignment(Qt.AlignCenter)
            tl.setStyleSheet(f"font-size: 12px; color: rgba(165,243,252,0.80); font-family: 'Segoe UI', Tahoma;")
            wl.addWidget(il)
            wl.addWidget(tl)
            tips_row.addWidget(w)
        cl.addLayout(tips_row)

        self.btn = QPushButton("⏳ يرجى إراحة عينيك (20ث)...")
        self.btn.setObjectName("Btn")
        self.btn.setEnabled(False)
        self.btn.setCursor(Qt.ForbiddenCursor)
        glow = QGraphicsDropShadowEffect(self.btn)
        glow.setBlurRadius(30)
        glow.setColor(QColor(accent + "80"))
        glow.setOffset(0, 0)
        self.btn.setGraphicsEffect(glow)
        self.btn.clicked.connect(self._done)
        cl.addWidget(self.btn, alignment=Qt.AlignCenter)

        hint = QLabel("Alt + F4 للحالات الضرورية فقط")
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        cl.addWidget(hint)

        outer.addWidget(card)

    def _tick(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.lbl_countdown.setText(str(self.seconds_left))
            self.btn.setText(f"⏳ يرجى إراحة عينيك ({self.seconds_left}ث)...")
        else:
            self.lbl_countdown.setText("✓")
            self.lbl_countdown.setStyleSheet(
                "font-size: 86px; font-weight: 900; color: #34D399; font-family: 'Segoe UI', Tahoma, sans-serif;"
            )
            self.btn.setText("انتهت الاستراحة  ·  عد للعمل  🚀")
            self.btn.setEnabled(True)
            self.btn.setCursor(Qt.PointingHandCursor)
            self._timer.stop()

    def _done(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        self.close()
        if cb:
            cb("eye_rest")

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_finish_callback
        self.on_finish_callback = None
        if cb:
            cb("eye_rest")
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
#  6. Appointment / Schedule REMINDER Overlay (replaces tray notification)
# ─────────────────────────────────────────────────────────────────────────────
class AppointmentReminderOverlay(QWidget):
    """Attractive full-screen popup for reminder-type schedule events."""
    ACCENT   = "#F59E0B"
    BG_STOPS = "stop:0 #0A0700, stop:0.5 #1F1500, stop:1 #2D1C00"
    CARD_BG  = "rgba(10, 7, 0, 0.98)"

    def __init__(self, appointment_name, appointment_time="", is_strict=False,
                 audio_mgr=None, on_close_callback=None):
        super().__init__()
        self.appointment_name = appointment_name
        self.appointment_time = appointment_time
        self.is_strict = is_strict
        self.audio_mgr = audio_mgr
        self.on_close_callback = on_close_callback

        if is_strict:
            self.ACCENT = "#EF4444"
            self.BG_STOPS = "stop:0 #0A0000, stop:0.5 #1F0000, stop:1 #350000"
            self.CARD_BG = "rgba(10, 0, 0, 0.98)"

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        self._setup()

        if self.audio_mgr:
            self.audio_mgr.play_water_alarm()

    def _setup(self):
        accent = self.ACCENT
        self.setStyleSheet(f"""
            QWidget#ARRoot {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,{self.BG_STOPS});
            }}
            QFrame#Card {{
                background-color: {self.CARD_BG};
                border: 1.5px solid rgba(255,255,255,0.07);
                border-radius: 32px;
            }}
            QLabel#TypeBadge {{
                background: {accent}22; color: {accent};
                border: 1px solid {accent}55; border-radius: 20px;
                padding: 6px 20px; font-size: 14px; font-weight: bold;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Name {{
                font-size: 40px; font-weight: 900; color: #FFFFFF;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#TimeLbl {{
                font-size: 56px; font-weight: 900; color: {accent};
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
            QLabel#Sub {{
                font-size: 18px; color: rgba(226,232,240,0.80);
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {accent}, stop:1 {accent}BB);
                color: #0A0A0A; font-size: 20px; font-weight: bold;
                border-radius: 18px; padding: 16px 52px; border: none;
                font-family: 'Madika Arabic TRIAL', 'Segoe UI', Tahoma, sans-serif;
            }}
            QPushButton#Btn:hover {{ background: {accent}DD; }}
            QLabel#Hint {{
                font-size: 13px; color: rgba(148,163,184,0.60);
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }}
        """)

        root = QWidget(self)
        root.setObjectName("ARRoot")
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(root)

        outer = QVBoxLayout(root)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(760)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(90)
        shadow.setColor(QColor(accent + "80"))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setAlignment(Qt.AlignCenter)
        cl.setSpacing(20)
        cl.setContentsMargins(52, 46, 52, 46)

        # Ring + emoji
        ring_c = QWidget()
        ring_c.setFixedSize(140, 140)
        self.ring = PulsingRing(accent, 140)
        rl = QVBoxLayout(ring_c)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.ring)
        bell_lbl = QLabel("🔔" if not self.is_strict else "🚨", ring_c)
        bell_lbl.setAlignment(Qt.AlignCenter)
        bell_lbl.setStyleSheet("font-size: 52px; background: transparent;")
        bell_lbl.setGeometry(20, 26, 100, 88)
        cl.addWidget(ring_c, alignment=Qt.AlignCenter)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {accent},
                stop:0.7 {accent}, stop:1 transparent);
            border-radius: 2px;
        """)
        cl.addWidget(bar)

        badge_text = "🔴  تذكير صارم" if self.is_strict else "🔔  تذكير بموعد"
        badge = QLabel(badge_text)
        badge.setObjectName("TypeBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(38)
        cl.addWidget(badge)

        name_lbl = QLabel(self.appointment_name)
        name_lbl.setObjectName("Name")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        cl.addWidget(name_lbl)

        if self.appointment_time:
            time_lbl = QLabel(self.appointment_time)
            time_lbl.setObjectName("TimeLbl")
            time_lbl.setAlignment(Qt.AlignCenter)
            cl.addWidget(time_lbl)

        msg = "حان الوقت المحدد لهذا الموعد الهام.\nاضغط للإغلاق والتوجه لموعدك. 📌" \
              if not self.is_strict else \
              "⚠️  هذا موعد صارم — لا يمكن تجاهله.\nيجب الالتزام الآن دون تأخير."
        sub = QLabel(msg)
        sub.setObjectName("Sub")
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        btn = QPushButton("فهمت  ·  توجهت للموعد  ✅")
        btn.setObjectName("Btn")
        btn.setCursor(Qt.PointingHandCursor)
        glow = QGraphicsDropShadowEffect(btn)
        glow.setBlurRadius(35)
        glow.setColor(QColor(accent + "90"))
        glow.setOffset(0, 0)
        btn.setGraphicsEffect(glow)
        btn.clicked.connect(self._done)
        cl.addWidget(btn, alignment=Qt.AlignCenter)

        hint = QLabel("Alt + F4 للحالات الضرورية فقط")
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        cl.addWidget(hint)

        outer.addWidget(card)

    def _done(self):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
            if hasattr(self.audio_mgr, "play_success_sound"):
                self.audio_mgr.play_success_sound()
        cb = self.on_close_callback
        self.on_close_callback = None
        self.close()
        if cb:
            cb()

    def closeEvent(self, event):
        if self.audio_mgr:
            self.audio_mgr.stop_alarm()
        cb = self.on_close_callback
        self.on_close_callback = None
        if cb:
            cb()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4 and (event.modifiers() & Qt.AltModifier):
            self.close()
        else:
            super().keyPressEvent(event)
