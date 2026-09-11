import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QImage
from PySide6.QtCore import Qt, QSize

def get_asset_path(filename):
    """Resolves asset file path cleanly whether running from source or PyInstaller EXE."""
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Check local assets dir
    local_path = os.path.join(base_dir, "assets", filename)
    if os.path.exists(local_path):
        return local_path

    # Check direct file in base_dir
    local_file = os.path.join(base_dir, filename)
    if os.path.exists(local_file):
        return local_file

    # Fallback to Downloads directory
    downloads_path = os.path.join(r"C:\Users\Wkroh\Downloads\logos sounds", filename)
    if os.path.exists(downloads_path):
        return downloads_path

    return ""

def get_tinted_pixmap(filename, color_hex="#FFFFFF", target_size=None):
    """
    Loads a PNG asset and dynamically tints its opaque pixels to the requested hex color.
    Returns a crisp, anti-aliased QPixmap.
    """
    asset_path = get_asset_path(filename)
    if not asset_path or not os.path.exists(asset_path):
        return QPixmap()

    orig_pix = QPixmap(asset_path)
    if orig_pix.isNull():
        return QPixmap()

    if target_size:
        orig_pix = orig_pix.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    tinted = QPixmap(orig_pix.size())
    tinted.fill(Qt.transparent)

    painter = QPainter(tinted)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    painter.drawPixmap(0, 0, orig_pix)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), QColor(color_hex))
    painter.end()

    return tinted
