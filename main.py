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

from PySide6.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "InproductivityApp_SingleInstance_IPC"

def setup_single_instance(app):
    """
    يتأكد من وجود نسخة واحدة فقط.
    إذا كان التطبيق يعمل بالفعل (حتى لو كان مخفياً في شريط المهام)،
    يرسل له إشارة لإظهار النافذة ثم يغلق النسخة الجديدة فوراً.
    """
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(500):
        # التطبيق يعمل بالفعل! نرسل أمر الإظهار وننهي العملية الجديدة
        socket.write(b"SHOW")
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        sys.exit(0)

    # النسخة الأولى — ننشئ سيرفر استماع محلي
    server = QLocalServer()
    QLocalServer.removeServer(SERVER_NAME)  # تنظيف أي بقايا سابقة
    if not server.listen(SERVER_NAME):
        QLocalServer.removeServer(SERVER_NAME)
        server.listen(SERVER_NAME)
    return server

def restore_existing_window(window):
    """إعادة إظهار النافذة القديمة وإحضارها لمقدمة الشاشة."""
    import win32gui
    import win32con

    window.showNormal()
    window.activateWindow()
    window.raise_()

    try:
        hwnd = int(window.winId())
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass

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
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    server = setup_single_instance(app)

    register_in_windows_search()
    load_custom_font(app)

    icon = get_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.tray_icon.setIcon(icon)
    window.show()

    # الاستماع للنسخ الجديدة التي تفتح من البحث لإعادة إظهار النافذة الحالية
    def on_new_connection():
        client = server.nextPendingConnection()
        if client:
            client.waitForReadyRead(500)
            msg = client.readAll().data().decode("utf-8", errors="ignore")
            if "SHOW" in msg or not msg:
                restore_existing_window(window)
            client.disconnectFromServer()

    server.newConnection.connect(on_new_connection)

    sys.exit(app.exec())
