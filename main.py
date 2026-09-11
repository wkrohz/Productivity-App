import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QFontDatabase, QFont
from PySide6.QtCore import Qt
from asset_helper import get_asset_path
from gui_main import MainWindow

def load_custom_font(app):
    font_path = get_asset_path("MadikaArabicTRIAL-Light.otf")
    if font_path:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                custom_font = QFont(families[0], 11)
                app.setFont(custom_font)
                print(f"Loaded custom font: {families[0]}")

def get_app_icon():
    logo_path = get_asset_path("logo.png")
    if logo_path:
        return QIcon(logo_path)

    # Fallback created pixmap
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(124, 58, 237))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    painter.end()
    return QIcon(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    load_custom_font(app)

    icon = get_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.tray_icon.setIcon(icon)
    window.show()

    sys.exit(app.exec())
