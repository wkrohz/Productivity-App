import sys
import os
import win32com.client
import win32event
import win32api
import winerror
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QFontDatabase, QFont
from PySide6.QtCore import Qt
from asset_helper import get_asset_path
from gui_main import MainWindow

# ─── Single Instance Lock ───────────────────────────────────────────────────
MUTEX_NAME = "انتاجيتي_SingleInstance_Mutex"
_mutex_handle = None

def activate_existing_window():
    """البحث عن نافذة التطبيق المشغّلة مسبقاً وإحضارها للمقدمة."""
    import win32gui
    import win32con

    target_hwnd = None

    def enum_windows_callback(hwnd, extra):
        nonlocal target_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "مركز الإنتاجية الذكي" in title or "انتاجيتي" in title:
                target_hwnd = hwnd
                return False
        return True

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception:
        pass

    if target_hwnd:
        # إظهار النافذة وإحضارها إلى الشاشة واستعادتها إذا كانت مصغرة
        win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(target_hwnd)
        return True
    return False

def ensure_single_instance():
    """
    يمنع تشغيل أكثر من نسخة واحدة من التطبيق في نفس الوقت.
    إذا كانت نسخة مشغّلة، تُرفع نافذتها وتغلق النسخة الجديدة فوراً بدون رسائل خطأ مزعجة.
    """
    global _mutex_handle
    _mutex_handle = win32event.CreateMutex(None, True, MUTEX_NAME)
    last_error = win32api.GetLastError()

    if last_error == winerror.ERROR_ALREADY_EXISTS:
        # نسخة ثانية → نرفع النافذة القديمة للمقدمة وننهي النسخة الثانية
        activate_existing_window()
        sys.exit(0)

    return _mutex_handle

# ────────────────────────────────────────────────────────────────────────────

def register_in_windows_search():
    """Automatically registers shortcut in Windows Start Menu so Windows Search finds it."""
    try:
        start_menu_dir = os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
        shortcut_path = os.path.join(start_menu_dir, "انتاجيتي.lnk")

        if getattr(sys, 'frozen', False):
            target_exe = sys.executable
        else:
            target_exe = os.path.abspath(sys.argv[0])

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_exe
        shortcut.WorkingDirectory = os.path.dirname(target_exe)
        shortcut.IconLocation = target_exe
        shortcut.Description = "انتاجيتي - مركز الإنتاجية الذكي لتنظيم الوقت وحظر التطبيقات"
        shortcut.save()
    except Exception as e:
        print("Shortcut creation notice:", e)

def load_custom_font(app):
    font_path = get_asset_path("MadikaArabicTRIAL-Light.otf")
    if font_path:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                custom_font = QFont(families[0], 11)
                app.setFont(custom_font)

def get_app_icon():
    logo_path = get_asset_path("logo.png")
    if logo_path and os.path.exists(logo_path):
        return QIcon(logo_path)

    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(2, 132, 199))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    painter.end()
    return QIcon(pixmap)

if __name__ == "__main__":
    # ✅ منع تعدد النسخ — يجب أن يكون قبل أي شيء آخر
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    ensure_single_instance()

    register_in_windows_search()
    load_custom_font(app)

    icon = get_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.tray_icon.setIcon(icon)
    window.show()

    sys.exit(app.exec())
