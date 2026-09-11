import sys
import os
import win32com.client
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QFontDatabase, QFont
from PySide6.QtCore import Qt
from asset_helper import get_asset_path
from gui_main import MainWindow

def register_in_windows_search():
    """Automatically registers ProductivityHub shortcut in Windows Start Menu so Windows Search finds it."""
    try:
        start_menu_dir = os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
        shortcut_path = os.path.join(start_menu_dir, "ProductivityHub.lnk")

        if getattr(sys, 'frozen', False):
            target_exe = sys.executable
        else:
            target_exe = os.path.abspath(sys.argv[0])

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_exe
        shortcut.WorkingDirectory = os.path.dirname(target_exe)
        shortcut.IconLocation = target_exe
        shortcut.Description = "مركز الإنتاجية الذكي لتنظيم الوقت وحظر التطبيقات"
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

    register_in_windows_search()
    load_custom_font(app)

    icon = get_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.tray_icon.setIcon(icon)
    window.show()

    sys.exit(app.exec())
