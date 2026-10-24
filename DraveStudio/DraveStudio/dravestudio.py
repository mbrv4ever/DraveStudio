#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DraveStudio - a lightweight Photoshop-style image editor  (a Dravenlock product)

Portable PyQt6 app: a canvas with layers, painting tools (brush, eraser, fill,
eyedropper, move), colour picker, undo/redo, its own project format and
PNG/JPG export. Dutch base language with automatic OS-language detection.
"""

import sys
import os
import json
import base64
import locale

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect, QTimer
from PyQt6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QFont, QPen, QIcon,
    QShortcut, QKeySequence,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSlider, QSpinBox, QToolButton, QFrame,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QDialog, QColorDialog,
    QScrollArea, QPlainTextEdit, QButtonGroup, QCheckBox, QSizePolicy, QFontComboBox,
)

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

APP_NAME = "DraveStudio"
APP_VERSION = "0.5"
AUTHOR_NAME = "Dravenlock"
WEBSITE_URL = "https://dravenlock.nl/"
DONATE_URL = "https://paypal.me/roger076"
CONTACT_EMAIL = "service@dravenlock.nl"
VERSION_URL = "https://dravenlock.nl/downloads/DraveStudio/version.txt"
PROJECT_EXT = ".dravestudio"


# ----------------------------------------------------------------------------- paths
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = app_dir()
CONFIG_PATH = os.path.join(APP_DIR, "dravestudio_config.json")


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", APP_DIR)
    return os.path.join(base, rel)


# ----------------------------------------------------------------------------- config
def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=2)
        return True
    except Exception:
        return False


# ----------------------------------------------------------------------------- language
SUPPORTED_LANGS = ["nl", "en"]

TRANSLATIONS = {
    "en": {
        "Een lichte fotobewerker met lagen.": "A lightweight image editor with layers.",
        "Bestand": "File", "Nieuw": "New", "Openen…": "Open…", "Opslaan": "Save",
        "Opslaan als…": "Save as…", "Exporteren…": "Export…",
        "Gereedschap": "Tools", "Penseel": "Brush", "Gum": "Eraser", "Vullen": "Fill",
        "Pipet": "Pick colour", "Verplaatsen": "Move",
        "Selectie": "Selection", "Deselecteren": "Deselect",
        "Rechthoek": "Rectangle", "Ovaal": "Ellipse", "Lijn": "Line", "Vorm vullen": "Fill shape",
        "Tekst": "Text", "Tekst toevoegen": "Add text", "Lettertype": "Font",
        "Tekengrootte": "Font size", "Ongedaan": "Undo", "Opnieuw": "Redo", "Passend": "Fit",
        "Kleur": "Colour", "Grootte": "Size", "Lagen": "Layers",
        "Nieuwe laag": "New layer", "Verwijderen": "Delete", "Omhoog": "Up", "Omlaag": "Down",
        "Dupliceren": "Duplicate", "Dekking": "Opacity", "Overvloeimodus": "Blend mode",
        "Achtergrond": "Background", "Laag": "Layer",
        "Normaal": "Normal", "Vermenigvuldigen": "Multiply", "Scherm": "Screen",
        "Bedekken": "Overlay", "Donkerder": "Darken", "Lichter": "Lighten", "Verschil": "Difference",
        "Snelgids": "Quick guide", "📖 Snelgids": "📖 Quick guide",
        "Contact": "Contact", "✉️ Contact": "✉️ Contact",
        "Updates": "Updates", "🔄 Updates": "🔄 Updates", "Info": "Info", "ℹ️ Info": "ℹ️ Info",
        "♥ Donatie": "♥ Donate", "Instellingen…": "Settings…", "Instellingen": "Settings",
        "Taal": "Language", "Automatisch (computertaal)": "Automatic (system language)",
        "Nederlands": "Dutch", "English": "English",
        "Sluiten": "Close", "Annuleren": "Cancel", "OK": "OK",
        "Breedte": "Width", "Hoogte": "Height", "Nieuw project": "New project",
        "Niet-opgeslagen wijzigingen gaan verloren. Doorgaan?":
            "Unsaved changes will be lost. Continue?",
        "Opgeslagen.": "Saved.", "Geëxporteerd.": "Exported.",
        "Je gebruikt de nieuwste versie.": "You are using the latest version.",
        "Er is een nieuwe versie beschikbaar": "A new version is available",
    }
}


def system_lang():
    try:
        code = (locale.getlocale()[0] or "")
        if not code:
            code = (locale.getdefaultlocale()[0] or "")
    except Exception:
        code = ""
    code = code.lower()
    if code.startswith("nl"):
        return "nl"
    return "en"


def current_lang():
    cfg = load_config()
    choice = cfg.get("lang", "auto")
    if choice in SUPPORTED_LANGS:
        return choice
    return system_lang()


def t(s):
    lang = current_lang()
    if lang == "nl":
        return s
    return TRANSLATIONS.get(lang, {}).get(s, s)


# ----------------------------------------------------------------------------- style
DRAVENLOCK_QSS = """
* { font-family: 'Segoe UI', Arial, sans-serif; }
QWidget { background-color: #0e0e11; color: #d4d4d4; font-size: 14px; }
QMainWindow, QDialog { background-color: #0e0e11; }
#header { background-color: #08080a; border-bottom: 1px solid #2a2a31; }
#title { color: #ffffff; font-size: 22px; font-weight: bold; }
#subtitle { color: #6fa3d6; font-size: 12px; }
#version { color: #6b6b76; font-size: 11px; }
#panel { background-color: #0a0a0c; border-right: 1px solid #2a2a31; }
#rightpanel { background-color: #0a0a0c; border-left: 1px solid #2a2a31; }
#sectionLabel { color: #6fa3d6; font-size: 12px; font-weight: bold; padding: 4px 2px; }

QPushButton {
    background-color: #16161b; color: #d4d4d4;
    border: 1px solid #2a2a31; border-radius: 6px; padding: 7px 10px;
}
QPushButton:hover { border: 1px solid #6fa3d6; color: #ffffff; }
QPushButton:pressed { background-color: #1d2733; }
QPushButton#cta { border: 1px solid #6fa3d6; color: #ffffff; }
QPushButton#cta:hover { background-color: #1d2733; }

QToolButton {
    background-color: #16161b; color: #d4d4d4;
    border: 1px solid #2a2a31; border-radius: 6px; padding: 8px;
}
QToolButton:hover { border: 1px solid #6fa3d6; color: #ffffff; }
QToolButton:checked { background-color: #1d2733; border: 1px solid #6fa3d6; }

QLineEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #121217; color: #d4d4d4;
    border: 1px solid #2a2a31; border-radius: 5px; padding: 5px;
    selection-background-color: #2d4763;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #6fa3d6; }
QComboBox QAbstractItemView { background-color: #121217; selection-background-color: #2d4763; }

QListWidget { background-color: #121217; border: 1px solid #2a2a31; border-radius: 5px; }
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background-color: #2d4763; color: #ffffff; }

QSlider::groove:horizontal { height: 5px; background: #23232a; border-radius: 2px; }
QSlider::handle:horizontal { background: #6fa3d6; width: 14px; margin: -5px 0; border-radius: 7px; }

QLabel { background-color: transparent; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #0e0e11; width: 12px; }
QScrollBar::handle:vertical { background: #2d4763; border-radius: 6px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #6fa3d6; }
QScrollBar:horizontal { background: #0e0e11; height: 12px; }
QScrollBar::handle:horizontal { background: #2d4763; border-radius: 6px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #6fa3d6; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
"""


# ----------------------------------------------------------------------------- logo / icon
def make_logo(size):
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setBrush(QColor("#14181e")); p.setPen(QPen(QColor("#6fa3d6"), max(2, size // 22)))
    m = size * 0.12
    p.drawRoundedRect(int(m), int(m), int(size - 2 * m), int(size - 2 * m), size // 6, size // 6)
    # three overlapping "layer" diamonds
    cx = size / 2
    cols = ["#6fa3d6", "#9d7fd6", "#d68f6f"]
    for i, col in enumerate(cols):
        c = QColor(col); c.setAlpha(210)
        p.setBrush(c); p.setPen(Qt.PenStyle.NoPen)
        s = size * 0.20
        y = size * (0.34 + i * 0.14)
        p.drawPolygon(*[QPoint(int(cx), int(y - s * 0.5)), QPoint(int(cx + s), int(y)),
                        QPoint(int(cx), int(y + s * 0.5)), QPoint(int(cx - s), int(y))])
    p.end()
    return pm


def logo_pixmap(h):
    for name in ("logo.png", "logo.ico", "icon.ico"):
        for base in (resource_path(name), os.path.join(APP_DIR, name)):
            if os.path.exists(base):
                pm = QPixmap(base)
                if not pm.isNull():
                    return pm.scaledToHeight(h, Qt.TransformationMode.SmoothTransformation)
    return make_logo(h)


def app_icon():
    for name in ("icon.ico", "logo.png", "logo.ico"):
        for base in (resource_path(name), os.path.join(APP_DIR, name)):
            if os.path.exists(base):
                ic = QIcon(base)
                if not ic.isNull():
                    return ic
    return QIcon(make_logo(64))


def make_splash_pixmap():
    W, H = 480, 300
    pm = QPixmap(W, H); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setBrush(QColor("#0e0e11")); p.setPen(QPen(QColor("#2a2a31"), 2))
    p.drawRoundedRect(1, 1, W - 2, H - 2, 16, 16)
    logo = logo_pixmap(110)
    p.drawPixmap((W - logo.width()) // 2, 30, logo)
    p.setPen(QColor("#ffffff")); f = QFont("Segoe UI", 26); f.setBold(True); p.setFont(f)
    p.drawText(0, 150, W, 44, int(Qt.AlignmentFlag.AlignCenter), APP_NAME)
    p.setPen(QColor("#6fa3d6")); f2 = QFont("Segoe UI", 12); f2.setBold(True); p.setFont(f2)
    p.drawText(0, 198, W, 24, int(Qt.AlignmentFlag.AlignCenter), t("Een lichte fotobewerker met lagen."))
    p.setPen(QColor("#8b909a")); p.setFont(QFont("Segoe UI", 10))
    p.drawText(0, 234, W, 22, int(Qt.AlignmentFlag.AlignCenter), f"een {AUTHOR_NAME} product")
    p.setPen(QColor("#5f6b78")); p.setFont(QFont("Segoe UI", 9))
    p.drawText(0, 260, W, 20, int(Qt.AlignmentFlag.AlignCenter), f"v{APP_VERSION}")
    p.end()
    return pm


def section(text):
    l = QLabel(text); l.setObjectName("sectionLabel"); return l


# ----------------------------------------------------------------------------- blend modes
BLEND_MODES = [
    ("Normaal", QPainter.CompositionMode.CompositionMode_SourceOver),
    ("Vermenigvuldigen", QPainter.CompositionMode.CompositionMode_Multiply),
    ("Scherm", QPainter.CompositionMode.CompositionMode_Screen),
    ("Bedekken", QPainter.CompositionMode.CompositionMode_Overlay),
    ("Donkerder", QPainter.CompositionMode.CompositionMode_Darken),
    ("Lichter", QPainter.CompositionMode.CompositionMode_Lighten),
    ("Verschil", QPainter.CompositionMode.CompositionMode_Difference),
]
BLEND_BY_NAME = {n: m for n, m in BLEND_MODES}


# ----------------------------------------------------------------------------- model
class Layer:
    def __init__(self, width, height, name="Laag", fill=None, image=None):
        self.name = name
        self.visible = True
        self.opacity = 100           # 0..100
        self.blend = "Normaal"
        if image is not None:
            self.image = image
        else:
            self.image = QImage(width, height, QImage.Format.Format_ARGB32)
            self.image.fill(fill if fill is not None else Qt.GlobalColor.transparent)

    def to_dict(self):
        ba = self.image.copy()
        from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
        arr = QByteArray(); buf = QBuffer(arr); buf.open(QIODevice.OpenModeFlag.WriteOnly)
        ba.save(buf, "PNG"); buf.close()
        return {
            "name": self.name, "visible": self.visible, "opacity": self.opacity,
            "blend": self.blend,
            "png": base64.b64encode(bytes(arr)).decode("ascii"),
        }

    @staticmethod
    def from_dict(d):
        raw = base64.b64decode(d["png"])
        img = QImage.fromData(raw, "PNG").convertToFormat(QImage.Format.Format_ARGB32)
        lyr = Layer(img.width(), img.height(), name=d.get("name", "Laag"), image=img)
        lyr.visible = d.get("visible", True)
        lyr.opacity = d.get("opacity", 100)
        lyr.blend = d.get("blend", "Normaal")
        return lyr


class Project:
    def __init__(self, width=1000, height=700):
        self.width = width
        self.height = height
        self.layers = []            # index 0 = bottom
        self.active = 0

    @classmethod
    def new(cls, width, height, white_bg=True):
        p = cls(width, height)
        bg = Layer(width, height, name="Achtergrond",
                   fill=Qt.GlobalColor.white if white_bg else Qt.GlobalColor.transparent)
        p.layers = [bg]; p.active = 0
        return p

    def composite(self):
        out = QImage(self.width, self.height, QImage.Format.Format_ARGB32)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        for lyr in self.layers:
            if not lyr.visible or lyr.opacity <= 0:
                continue
            p.setOpacity(lyr.opacity / 100.0)
            p.setCompositionMode(BLEND_BY_NAME.get(lyr.blend,
                                 QPainter.CompositionMode.CompositionMode_SourceOver))
            p.drawImage(0, 0, lyr.image)
        p.end()
        return out

    def to_dict(self):
        return {"app": APP_NAME, "version": APP_VERSION, "width": self.width,
                "height": self.height, "active": self.active,
                "layers": [l.to_dict() for l in self.layers]}

    @classmethod
    def from_dict(cls, d):
        p = cls(d["width"], d["height"])
        p.layers = [Layer.from_dict(x) for x in d["layers"]]
        p.active = min(d.get("active", 0), len(p.layers) - 1)
        if not p.layers:
            p.layers = [Layer(p.width, p.height, name="Achtergrond", fill=Qt.GlobalColor.white)]
            p.active = 0
        return p


# ----------------------------------------------------------------------------- canvas
class Canvas(QWidget):
    cursorMoved = pyqtSignal(int, int)
    changed = pyqtSignal()          # project content/structure changed

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.zoom = 1.0
        self.tool = "brush"
        self.color = QColor("#e0e0e0")
        self.brush_size = 12
        self.setMouseTracking(True)
        self._last = None
        self._drawing = False
        self._move_origin = None
        self._move_start_img = None
        self.selection = None          # QRect in beeld-coördinaten, of None
        self._sel_origin = None
        self._ants = 0                 # marching-ants animatiefase
        self._shape_origin = None
        self._shape_start_img = None
        self.fill_shapes = True
        self.text_handler = None       # door het hoofdvenster gezet
        self.undo_stack = []
        self.redo_stack = []
        self._update_size()

    # -- helpers
    def _update_size(self):
        self.setFixedSize(int(self.project.width * self.zoom),
                          int(self.project.height * self.zoom))
        self.update()

    def set_zoom(self, z):
        self.zoom = max(0.1, min(8.0, z))
        self._update_size()

    def active_layer(self):
        return self.project.layers[self.project.active]

    def _to_image(self, pos):
        return QPoint(int(pos.x() / self.zoom), int(pos.y() / self.zoom))

    # -- undo
    def push_undo(self):
        idx = self.project.active
        self.undo_stack.append((idx, self.project.layers[idx].image.copy()))
        if len(self.undo_stack) > 25:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        idx, img = self.undo_stack.pop()
        if idx < len(self.project.layers):
            self.redo_stack.append((idx, self.project.layers[idx].image.copy()))
            self.project.layers[idx].image = img
            self.update(); self.changed.emit()

    def redo(self):
        if not self.redo_stack:
            return
        idx, img = self.redo_stack.pop()
        if idx < len(self.project.layers):
            self.undo_stack.append((idx, self.project.layers[idx].image.copy()))
            self.project.layers[idx].image = img
            self.update(); self.changed.emit()

    # -- painting on screen
    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        # checkerboard for transparency
        self._draw_checker(p)
        comp = self.project.composite()
        p.drawImage(QRect(0, 0, self.width(), self.height()), comp)
        # border
        p.setPen(QPen(QColor("#2a2a31"), 1)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        # selectie ("marching ants")
        if self.selection is not None and not self.selection.isNull():
            r = self.selection
            sr = QRect(int(r.x() * self.zoom), int(r.y() * self.zoom),
                       int(r.width() * self.zoom), int(r.height() * self.zoom))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(0, 0, 0), 1)); p.drawRect(sr)
            pen = QPen(QColor(255, 255, 255), 1)
            pen.setStyle(Qt.PenStyle.DashLine); pen.setDashOffset(self._ants)
            p.setPen(pen); p.drawRect(sr)
        p.end()

    def selection_clip(self):
        """De selectie als QRect (voor clipping), of None."""
        if self.selection is not None and not self.selection.isNull():
            return self.selection
        return None

    def clear_selection(self):
        self.selection = None; self.update()

    def _draw_checker(self, p):
        s = 12
        light = QColor("#3a3a42"); dark = QColor("#2b2b31")
        p.fillRect(self.rect(), dark)
        for y in range(0, self.height(), s):
            for x in range(0, self.width(), s):
                if ((x // s) + (y // s)) % 2 == 0:
                    p.fillRect(x, y, s, s, light)

    # -- mouse
    def mousePressEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        ip = self._to_image(ev.position())
        if self.tool in ("brush", "eraser"):
            self.push_undo(); self._drawing = True; self._last = ip
            self._paint_to(ip, ip)
        elif self.tool == "fill":
            self.push_undo(); self._flood_fill(ip)
        elif self.tool == "pick":
            self._pick(ip)
        elif self.tool == "move":
            self.push_undo()
            self._move_origin = ip
            self._move_start_img = self.active_layer().image.copy()
        elif self.tool == "select":
            self._sel_origin = ip
            self.selection = QRect(ip, ip)
            self.update()
        elif self.tool in ("rect", "ellipse", "line"):
            self.push_undo()
            self._shape_origin = ip
            self._shape_start_img = self.active_layer().image.copy()
        elif self.tool == "text":
            if self.text_handler:
                self.text_handler(ip)

    def mouseMoveEvent(self, ev):
        ip = self._to_image(ev.position())
        self.cursorMoved.emit(ip.x(), ip.y())
        if self._drawing and self.tool in ("brush", "eraser"):
            self._paint_to(self._last, ip); self._last = ip
        elif self.tool == "move" and self._move_origin is not None:
            dx = ip.x() - self._move_origin.x(); dy = ip.y() - self._move_origin.y()
            base = QImage(self.project.width, self.project.height, QImage.Format.Format_ARGB32)
            base.fill(Qt.GlobalColor.transparent)
            q = QPainter(base); q.drawImage(QPoint(dx, dy), self._move_start_img); q.end()
            self.active_layer().image = base
            self.update(); self.changed.emit()
        elif self.tool == "select" and self._sel_origin is not None:
            self.selection = QRect(self._sel_origin, ip).normalized()
            self.update()
        elif self.tool in ("rect", "ellipse", "line") and self._shape_origin is not None:
            self.active_layer().image = self._shape_start_img.copy()
            self._draw_shape(self._shape_origin, ip)

    def mouseReleaseEvent(self, ev):
        self._drawing = False; self._last = None
        self._move_origin = None; self._move_start_img = None
        self._shape_origin = None; self._shape_start_img = None
        if self.tool == "select" and self._sel_origin is not None:
            self._sel_origin = None
            if self.selection is not None and (self.selection.width() < 3 or self.selection.height() < 3):
                self.selection = None     # te klein -> deselecteren
            # begrens tot het canvas
            if self.selection is not None:
                self.selection = self.selection.intersected(
                    QRect(0, 0, self.project.width, self.project.height))
            self.update()

    def _draw_shape(self, p0, p1):
        lyr = self.active_layer()
        painter = QPainter(lyr.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self.selection_clip()
        if clip is not None:
            painter.setClipRect(clip)
        if self.tool == "line":
            pen = QPen(self.color, self.brush_size)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(p0, p1)
        else:
            rect = QRect(p0, p1).normalized()
            if self.fill_shapes:
                painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(self.color)
            else:
                pen = QPen(self.color, self.brush_size); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
            if self.tool == "rect":
                painter.drawRect(rect)
            else:
                painter.drawEllipse(rect)
        painter.end()
        self.update(); self.changed.emit()

    def _paint_to(self, p0, p1):
        lyr = self.active_layer()
        painter = QPainter(lyr.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self.selection_clip()
        if clip is not None:
            painter.setClipRect(clip)
        if self.tool == "eraser":
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            pen = QPen(QColor(0, 0, 0, 255), self.brush_size)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(self.color, self.brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(p0, p1)
        painter.end()
        self.update(); self.changed.emit()

    def _pick(self, ip):
        comp = self.project.composite()
        if 0 <= ip.x() < comp.width() and 0 <= ip.y() < comp.height():
            self.color = QColor(comp.pixel(ip.x(), ip.y()))
            self.changed.emit()

    def _flood_fill(self, ip):
        lyr = self.active_layer()
        if not (0 <= ip.x() < lyr.image.width() and 0 <= ip.y() < lyr.image.height()):
            return
        if HAVE_PIL:
            img = lyr.image.convertToFormat(QImage.Format.Format_RGBA8888)
            w, h = img.width(), img.height()
            ptr = img.bits(); ptr.setsize(img.sizeInBytes())
            pil = Image.frombytes("RGBA", (w, h), bytes(ptr))
            fill = (self.color.red(), self.color.green(), self.color.blue(), 255)
            from PIL import ImageDraw
            ImageDraw.floodfill(pil, (ip.x(), ip.y()), fill, thresh=40)
            data = pil.tobytes("raw", "RGBA")
            newimg = QImage(data, w, h, QImage.Format.Format_RGBA8888).convertToFormat(
                QImage.Format.Format_ARGB32)
            newimg = newimg.copy()
            clip = self.selection_clip()
            if clip is not None:
                # alleen binnen de selectie de gevulde versie tonen
                result = lyr.image.copy()
                q = QPainter(result); q.setClipRect(clip); q.drawImage(0, 0, newimg); q.end()
                lyr.image = result
            else:
                lyr.image = newimg
        else:
            # simple fallback: fill whole layer (of selectie)
            clip = self.selection_clip()
            if clip is not None:
                q = QPainter(lyr.image); q.fillRect(clip, self.color); q.end()
            else:
                lyr.image.fill(self.color)
        self.update(); self.changed.emit()


# ----------------------------------------------------------------------------- dialogs
class ContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Contact")); self.resize(440, 220)
        v = QVBoxLayout(self)
        v.addWidget(QLabel(f"<b>{APP_NAME}</b> — {AUTHOR_NAME}"))
        v.addWidget(QLabel(f"E-mail: {CONTACT_EMAIL}"))
        v.addWidget(QLabel(f'Website: <a style="color:#6fa3d6" href="{WEBSITE_URL}">{WEBSITE_URL}</a>'))
        msg = QLabel("Vragen, ideeën of een bug gevonden? Mail gerust!")
        msg.setWordWrap(True); v.addWidget(msg)
        v.addStretch(1)
        row = QHBoxLayout(); row.addStretch(1)
        mail = QPushButton("✉️  E-mail openen"); mail.setObjectName("cta")
        mail.clicked.connect(self._mail); row.addWidget(mail)
        copy = QPushButton("Kopieer e-mail"); copy.clicked.connect(self._copy); row.addWidget(copy)
        close = QPushButton(t("Sluiten")); close.clicked.connect(self.accept); row.addWidget(close)
        v.addLayout(row)

    def _mail(self):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        ok = QDesktopServices.openUrl(QUrl(f"mailto:{CONTACT_EMAIL}?subject={APP_NAME}"))
        if not ok:
            self._copy()

    def _copy(self):
        QApplication.clipboard().setText(CONTACT_EMAIL)
        QMessageBox.information(self, t("Contact"), "E-mailadres gekopieerd:\n" + CONTACT_EMAIL)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Instellingen")); self.resize(420, 200)
        cfg = load_config()
        g = QGridLayout(self)
        g.addWidget(QLabel(t("Taal") + ":"), 0, 0)
        self.lang = QComboBox()
        self.lang.addItem(t("Automatisch (computertaal)"), "auto")
        self.lang.addItem(t("Nederlands"), "nl")
        self.lang.addItem(t("English"), "en")
        cur = cfg.get("lang", "auto")
        self.lang.setCurrentIndex({"auto": 0, "nl": 1, "en": 2}.get(cur, 0))
        g.addWidget(self.lang, 0, 1)
        note = QLabel("Taalwijziging geldt na herstart."); note.setStyleSheet("color:#8b909a;")
        g.addWidget(note, 1, 0, 1, 2)
        row = QHBoxLayout(); row.addStretch(1)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        save = QPushButton(t("OK")); save.setObjectName("cta"); save.clicked.connect(self._save); row.addWidget(save)
        g.addLayout(row, 2, 0, 1, 2)

    def _save(self):
        cfg = load_config(); cfg["lang"] = self.lang.currentData(); save_config(cfg)
        self.accept()


class QuickGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("📖 Snelgids") + " - " + APP_NAME); self.resize(640, 600)
        v = QVBoxLayout(self)
        txt = QPlainTextEdit(); txt.setReadOnly(True)
        txt.setPlainText(
            f"{APP_NAME} — {t('Een lichte fotobewerker met lagen.')}\n\n"
            "── AAN DE SLAG ──\n"
            "• Bestand → Nieuw maakt een leeg project. Openen laadt een PNG/JPG.\n"
            "• Kies links een gereedschap en een kleur, en teken op het canvas.\n\n"
            "── GEREEDSCHAP ──\n"
            "• Penseel: tekenen met de huidige kleur en grootte.\n"
            "• Gum: maakt pixels doorzichtig.\n"
            "• Vullen (emmer): vult een gebied met de huidige kleur.\n"
            "• Pipet: klik om een kleur van het beeld over te nemen.\n"
            "• Verplaatsen: sleep de inhoud van de actieve laag.\n\n"
            "── LAGEN (rechts) ──\n"
            "• Nieuwe laag, verwijderen, dupliceren, omhoog/omlaag.\n"
            "• Vinkje = zichtbaar. Dekking en overvloeimodus per laag.\n"
            "• De geselecteerde laag is de 'actieve' laag waarop je tekent.\n\n"
            "── ZOOM & ONGEDAAN MAKEN ──\n"
            "• Zoom met de knoppen onderaan (of 100% / passend).\n"
            "• Ctrl+Z = ongedaan maken, Ctrl+Y = opnieuw (per tekenactie).\n\n"
            "── BEWAREN ──\n"
            "• Opslaan bewaart je project mét lagen (eigen .dravestudio-bestand).\n"
            "• Exporteren maakt een platte PNG of JPG.\n")
        v.addWidget(txt)
        close = QPushButton(t("Sluiten")); close.clicked.connect(self.accept); v.addWidget(close)


class _UpdateWorker(QThread):
    done = pyqtSignal(object)

    def run(self):
        try:
            import urllib.request
            with urllib.request.urlopen(VERSION_URL, timeout=6) as r:
                self.done.emit(r.read().decode("utf-8", "ignore").strip())
        except Exception:
            self.done.emit(None)


# ----------------------------------------------------------------------------- new dialog
class NewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Nieuw project")); self.resize(360, 200)
        g = QGridLayout(self)
        g.addWidget(QLabel(t("Breedte") + ":"), 0, 0)
        self.w = QSpinBox(); self.w.setRange(1, 8000); self.w.setValue(1000); g.addWidget(self.w, 0, 1)
        g.addWidget(QLabel(t("Hoogte") + ":"), 1, 0)
        self.h = QSpinBox(); self.h.setRange(1, 8000); self.h.setValue(700); g.addWidget(self.h, 1, 1)
        g.addWidget(QLabel(t("Achtergrond") + ":"), 2, 0)
        self.bg = QComboBox(); self.bg.addItem("Wit", True); self.bg.addItem("Transparant", False)
        g.addWidget(self.bg, 2, 1)
        row = QHBoxLayout(); row.addStretch(1)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("OK")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        g.addLayout(row, 3, 0, 1, 2)


# ----------------------------------------------------------------------------- text dialog
class TextDialog(QDialog):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Tekst toevoegen")); self.resize(440, 220)
        self.color = color
        g = QGridLayout(self)
        g.addWidget(QLabel(t("Tekst") + ":"), 0, 0)
        self.text = QLineEdit(); g.addWidget(self.text, 0, 1)
        g.addWidget(QLabel(t("Lettertype") + ":"), 1, 0)
        self.font = QFontComboBox(); g.addWidget(self.font, 1, 1)
        g.addWidget(QLabel(t("Tekengrootte") + ":"), 2, 0)
        self.size = QSpinBox(); self.size.setRange(6, 600); self.size.setValue(48); g.addWidget(self.size, 2, 1)
        self.preview = QLabel("Abc"); self.preview.setStyleSheet(f"color:{color.name()};")
        g.addWidget(self.preview, 3, 1)
        self.text.textChanged.connect(self._upd); self.size.valueChanged.connect(self._upd)
        self.font.currentFontChanged.connect(self._upd)
        row = QHBoxLayout(); row.addStretch(1)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("OK")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        g.addLayout(row, 4, 0, 1, 2)
        self._upd()

    def _upd(self):
        f = self.font.currentFont(); f.setPointSize(min(28, max(10, self.size.value() // 2)))
        self.preview.setFont(f)
        self.preview.setText(self.text.text() or "Abc")

    def result(self):
        return self.text.text(), self.font.currentFont().family(), self.size.value()


# ----------------------------------------------------------------------------- main window
class DraveStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = Project.new(1000, 700, white_bg=True)
        self.cur_path = None
        self.setWindowTitle(f"{APP_NAME} - {t('Een lichte fotobewerker met lagen.')}")
        self.resize(1320, 860)

        central = QWidget(); self.setCentralWidget(central)
        outer = QVBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        outer.addWidget(self._header())

        body = QHBoxLayout(); body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0)
        body.addWidget(self._tools_panel())
        body.addWidget(self._center(), 1)
        body.addWidget(self._layers_panel())
        bw = QWidget(); bw.setLayout(body); outer.addWidget(bw, 1)

        self._refresh_layers()
        self._refresh_color()
        self._init_shortcuts()
        self.statusBar().showMessage(APP_NAME)
        self._donate_status()
        # marching-ants animatie
        self._ants_timer = QTimer(self)
        self._ants_timer.timeout.connect(self._tick_ants)
        self._ants_timer.start(120)

    def _tick_ants(self):
        if self.canvas.selection is not None:
            self.canvas._ants = (self.canvas._ants + 1) % 16
            self.canvas.update()

    def deselect(self):
        self.canvas.clear_selection()

    def place_text(self, ip):
        dlg = TextDialog(self.canvas.color, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        text, family, size = dlg.result()
        if not text.strip():
            return
        self.canvas.push_undo()
        lyr = self.canvas.active_layer()
        p = QPainter(lyr.image); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self.canvas.selection_clip()
        if clip is not None:
            p.setClipRect(clip)
        f = QFont(family); f.setPixelSize(size)
        p.setFont(f); p.setPen(self.canvas.color)
        fm = p.fontMetrics()
        p.drawText(QPoint(ip.x(), ip.y() + fm.ascent()), text)
        p.end()
        self.canvas.update(); self.canvas.changed.emit()

    # -- header
    def _header(self):
        h = QWidget(); h.setObjectName("header"); h.setFixedHeight(60)
        lay = QHBoxLayout(h); lay.setContentsMargins(12, 6, 12, 6)
        logo = QLabel(); logo.setPixmap(logo_pixmap(40)); lay.addWidget(logo)
        box = QVBoxLayout(); box.setSpacing(0)
        ttl = QLabel(APP_NAME); ttl.setObjectName("title")
        sub = QLabel(t("Een lichte fotobewerker met lagen.")); sub.setObjectName("subtitle")
        box.addWidget(ttl); box.addWidget(sub); lay.addLayout(box)
        lay.addSpacing(18)
        for label, fn in [(t("Nieuw"), self.new_project), (t("Openen…"), self.open_image),
                          (t("Opslaan"), self.save_project), (t("Exporteren…"), self.export_image)]:
            b = QPushButton(label); b.clicked.connect(fn); lay.addWidget(b)
        lay.addStretch(1)
        for label, fn in [(t("📖 Snelgids"), self.show_guide), (t("✉️ Contact"), self.show_contact),
                          (t("🔄 Updates"), lambda: self.check_updates(silent=False)),
                          (t("ℹ️ Info"), self.show_info), (t("Instellingen…"), self.show_settings)]:
            b = QPushButton(label); b.clicked.connect(fn); lay.addWidget(b)
        return h

    # -- tools
    def _tools_panel(self):
        w = QWidget(); w.setObjectName("panel"); w.setFixedWidth(180)
        lay = QVBoxLayout(w); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(6)
        lay.addWidget(section(t("Gereedschap")))
        self.tool_group = QButtonGroup(self); self.tool_group.setExclusive(True)
        tools = [("brush", "🖌  " + t("Penseel")), ("eraser", "🩹  " + t("Gum")),
                 ("fill", "🪣  " + t("Vullen")), ("pick", "💧  " + t("Pipet")),
                 ("move", "✥  " + t("Verplaatsen")), ("select", "⬚  " + t("Selectie")),
                 ("rect", "▭  " + t("Rechthoek")), ("ellipse", "⬭  " + t("Ovaal")),
                 ("line", "╱  " + t("Lijn")), ("text", "🅣  " + t("Tekst"))]
        for key, label in tools:
            b = QToolButton(); b.setText(label); b.setCheckable(True)
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setStyleSheet("text-align:left; padding:8px;")
            b.clicked.connect(lambda _c=False, k=key: self.set_tool(k))
            self.tool_group.addButton(b); lay.addWidget(b)
            if key == "brush":
                b.setChecked(True)
            setattr(self, f"_toolbtn_{key}", b)
        self.fill_chk = QCheckBox(t("Vorm vullen")); self.fill_chk.setChecked(True)
        self.fill_chk.toggled.connect(lambda v: setattr(self.canvas, "fill_shapes", v))
        lay.addWidget(self.fill_chk)
        desel = QPushButton(t("Deselecteren")); desel.clicked.connect(self.deselect)
        lay.addWidget(desel)

        lay.addSpacing(8)
        lay.addWidget(section(t("Kleur")))
        self.color_btn = QPushButton(); self.color_btn.setFixedHeight(38)
        self.color_btn.clicked.connect(self.pick_color); lay.addWidget(self.color_btn)

        lay.addSpacing(8)
        lay.addWidget(section(t("Grootte")))
        self.size_slider = QSlider(Qt.Orientation.Horizontal); self.size_slider.setRange(1, 120)
        self.size_slider.setValue(12); self.size_slider.valueChanged.connect(self._set_size)
        lay.addWidget(self.size_slider)
        self.size_lbl = QLabel("12 px"); lay.addWidget(self.size_lbl)

        lay.addStretch(1)
        return w

    # -- center (canvas + zoom)
    def _center(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        self.canvas = Canvas(self.project)
        self.canvas.cursorMoved.connect(self._on_cursor)
        self.canvas.changed.connect(self._on_canvas_changed)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.canvas)
        self.canvas.text_handler = self.place_text
        lay.addWidget(self.scroll, 1)

        bar = QWidget(); bar.setFixedHeight(44); blay = QHBoxLayout(bar)
        blay.setContentsMargins(10, 6, 10, 6)
        undo = QToolButton(); undo.setText("↶ " + t("Ongedaan")); undo.setToolTip("Ctrl+Z")
        undo.clicked.connect(self.canvas.undo); blay.addWidget(undo)
        redo = QToolButton(); redo.setText("↷ " + t("Opnieuw")); redo.setToolTip("Ctrl+Y")
        redo.clicked.connect(self.canvas.redo); blay.addWidget(redo)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); sep.setStyleSheet("color:#2a2a31;")
        blay.addWidget(sep)
        zout = QToolButton(); zout.setText("➖"); zout.clicked.connect(lambda: self._zoom(0.8)); blay.addWidget(zout)
        zin = QToolButton(); zin.setText("➕"); zin.clicked.connect(lambda: self._zoom(1.25)); blay.addWidget(zin)
        z100 = QPushButton("100%"); z100.clicked.connect(lambda: self._set_zoom(1.0)); blay.addWidget(z100)
        zfit = QPushButton(t("Passend")); zfit.clicked.connect(self._zoom_fit); blay.addWidget(zfit)
        self.zoom_lbl = QLabel("100%"); blay.addWidget(self.zoom_lbl)
        blay.addStretch(1)
        self.coord_lbl = QLabel(""); blay.addWidget(self.coord_lbl)
        lay.addWidget(bar)
        return w

    # -- layers
    def _layers_panel(self):
        w = QWidget(); w.setObjectName("rightpanel"); w.setFixedWidth(250)
        lay = QVBoxLayout(w); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(6)
        lay.addWidget(section(t("Lagen")))
        self.layer_list = QListWidget()
        self.layer_list.itemSelectionChanged.connect(self._on_layer_selected)
        self.layer_list.itemChanged.connect(self._on_layer_item_changed)
        lay.addWidget(self.layer_list, 1)

        row = QHBoxLayout()
        for txt, fn in [("➕", self.add_layer), ("⧉", self.duplicate_layer), ("🗑", self.delete_layer),
                        ("▲", lambda: self.move_layer(1)), ("▼", lambda: self.move_layer(-1))]:
            b = QToolButton(); b.setText(txt); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)

        lay.addWidget(section(t("Dekking")))
        self.opacity = QSlider(Qt.Orientation.Horizontal); self.opacity.setRange(0, 100)
        self.opacity.setValue(100); self.opacity.valueChanged.connect(self._set_opacity)
        lay.addWidget(self.opacity)

        lay.addWidget(section(t("Overvloeimodus")))
        self.blend = QComboBox()
        for name, _m in BLEND_MODES:
            self.blend.addItem(t(name), name)
        self.blend.currentIndexChanged.connect(self._set_blend)
        lay.addWidget(self.blend)
        return w

    # ------------------------------------------------ tool/colour
    def set_tool(self, key):
        self.canvas.tool = key

    def _set_size(self, v):
        self.canvas.brush_size = v; self.size_lbl.setText(f"{v} px")

    def pick_color(self):
        col = QColorDialog.getColor(self.canvas.color, self, t("Kleur"))
        if col.isValid():
            self.canvas.color = col; self._refresh_color()

    def _refresh_color(self):
        c = self.canvas.color
        self.color_btn.setStyleSheet(
            f"background-color:{c.name()}; border:1px solid #6fa3d6; border-radius:6px;")
        self.color_btn.setText(c.name().upper())

    # ------------------------------------------------ zoom
    def _zoom(self, factor):
        self._set_zoom(self.canvas.zoom * factor)

    def _set_zoom(self, z):
        self.canvas.set_zoom(z)
        self.zoom_lbl.setText(f"{int(self.canvas.zoom * 100)}%")

    def _zoom_fit(self):
        vp = self.scroll.viewport().size()
        zx = vp.width() / self.project.width; zy = vp.height() / self.project.height
        self._set_zoom(min(zx, zy) * 0.98)

    def _on_cursor(self, x, y):
        self.coord_lbl.setText(f"{x}, {y}")

    def _on_canvas_changed(self):
        self._refresh_color()

    # ------------------------------------------------ layers
    def _refresh_layers(self):
        self.layer_list.blockSignals(True)
        self.layer_list.clear()
        # show top layer first
        for i in range(len(self.project.layers) - 1, -1, -1):
            lyr = self.project.layers[i]
            it = QListWidgetItem(lyr.name)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Checked if lyr.visible else Qt.CheckState.Unchecked)
            it.setData(Qt.ItemDataRole.UserRole, i)
            self.layer_list.addItem(it)
            if i == self.project.active:
                it.setSelected(True)
        self.layer_list.blockSignals(False)
        self._sync_layer_props()

    def _sync_layer_props(self):
        lyr = self.project.layers[self.project.active]
        self.opacity.blockSignals(True); self.opacity.setValue(lyr.opacity); self.opacity.blockSignals(False)
        self.blend.blockSignals(True)
        idx = max(0, self.blend.findData(lyr.blend)); self.blend.setCurrentIndex(idx)
        self.blend.blockSignals(False)

    def _on_layer_selected(self):
        items = self.layer_list.selectedItems()
        if items:
            self.project.active = items[0].data(Qt.ItemDataRole.UserRole)
            self._sync_layer_props()

    def _on_layer_item_changed(self, item):
        i = item.data(Qt.ItemDataRole.UserRole)
        if i is None or i >= len(self.project.layers):
            return
        self.project.layers[i].visible = (item.checkState() == Qt.CheckState.Checked)
        self.project.layers[i].name = item.text()
        self.canvas.update()

    def add_layer(self):
        lyr = Layer(self.project.width, self.project.height, name=t("Laag"))
        self.project.layers.append(lyr)
        self.project.active = len(self.project.layers) - 1
        self._refresh_layers(); self.canvas.update()

    def duplicate_layer(self):
        src = self.project.layers[self.project.active]
        dup = Layer(self.project.width, self.project.height, name=src.name + " ✚", image=src.image.copy())
        dup.opacity = src.opacity; dup.blend = src.blend; dup.visible = src.visible
        self.project.layers.insert(self.project.active + 1, dup)
        self.project.active += 1
        self._refresh_layers(); self.canvas.update()

    def delete_layer(self):
        if len(self.project.layers) <= 1:
            QMessageBox.information(self, t("Lagen"), "Er moet minstens één laag blijven."); return
        del self.project.layers[self.project.active]
        self.project.active = max(0, self.project.active - 1)
        self._refresh_layers(); self.canvas.update()

    def move_layer(self, direction):
        i = self.project.active; j = i + direction
        if 0 <= j < len(self.project.layers):
            self.project.layers[i], self.project.layers[j] = self.project.layers[j], self.project.layers[i]
            self.project.active = j
            self._refresh_layers(); self.canvas.update()

    def _set_opacity(self, v):
        self.project.layers[self.project.active].opacity = v; self.canvas.update()

    def _set_blend(self):
        self.project.layers[self.project.active].blend = self.blend.currentData(); self.canvas.update()

    # ------------------------------------------------ shortcuts
    def _init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self.canvas.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self.canvas.redo)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_project)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self.export_image)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.deselect)
        QShortcut(QKeySequence("Escape"), self, activated=self.deselect)

    # ------------------------------------------------ file ops
    def _confirm_discard(self):
        return QMessageBox.question(self, APP_NAME,
            t("Niet-opgeslagen wijzigingen gaan verloren. Doorgaan?")) == QMessageBox.StandardButton.Yes

    def new_project(self):
        dlg = NewDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.project = Project.new(dlg.w.value(), dlg.h.value(), white_bg=dlg.bg.currentData())
        self.cur_path = None
        self.canvas.project = self.project; self.canvas.undo_stack.clear(); self.canvas.redo_stack.clear()
        self.canvas.selection=None; self.canvas._update_size(); self._refresh_layers()

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, t("Openen…"), APP_DIR,
            "Afbeeldingen (*.png *.jpg *.jpeg *.bmp);;Project (*%s);;Alle (*)" % PROJECT_EXT)
        if not path:
            return
        if path.lower().endswith(PROJECT_EXT):
            self._load_project(path); return
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(self, t("Openen…"), "Kon de afbeelding niet laden."); return
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
        self.project = Project(img.width(), img.height())
        self.project.layers = [Layer(img.width(), img.height(), name="Achtergrond", image=img)]
        self.project.active = 0; self.cur_path = None
        self.canvas.project = self.project; self.canvas.undo_stack.clear(); self.canvas.redo_stack.clear()
        self.canvas.selection=None; self.canvas._update_size(); self._refresh_layers()

    def _load_project(self, path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self.project = Project.from_dict(json.load(fh))
        except Exception as e:
            QMessageBox.warning(self, t("Openen…"), str(e)); return
        self.cur_path = path
        self.canvas.project = self.project; self.canvas.undo_stack.clear(); self.canvas.redo_stack.clear()
        self.canvas.selection=None; self.canvas._update_size(); self._refresh_layers()
        self.statusBar().showMessage("Geopend: " + os.path.basename(path))

    def save_project(self):
        path = self.cur_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, t("Opslaan als…"),
                os.path.join(APP_DIR, "project" + PROJECT_EXT), "Project (*%s)" % PROJECT_EXT)
            if not path:
                return
            if not path.endswith(PROJECT_EXT):
                path += PROJECT_EXT
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.project.to_dict(), fh)
            self.cur_path = path
            self.statusBar().showMessage(t("Opgeslagen."))
        except Exception as e:
            QMessageBox.warning(self, t("Opslaan"), str(e))

    def export_image(self):
        path, _ = QFileDialog.getSaveFileName(self, t("Exporteren…"),
            os.path.join(APP_DIR, "export.png"), "PNG (*.png);;JPEG (*.jpg)")
        if not path:
            return
        comp = self.project.composite()
        if path.lower().endswith((".jpg", ".jpeg")):
            flat = QImage(comp.size(), QImage.Format.Format_RGB32); flat.fill(Qt.GlobalColor.white)
            p = QPainter(flat); p.drawImage(0, 0, comp); p.end()
            ok = flat.save(path, "JPEG", 92)
        else:
            ok = comp.save(path, "PNG")
        self.statusBar().showMessage(t("Geëxporteerd.") if ok else "Export mislukt.")

    # ------------------------------------------------ chrome
    def show_guide(self):
        QuickGuideDialog(self).exec()

    def show_contact(self):
        ContactDialog(self).exec()

    def show_settings(self):
        if SettingsDialog(self).exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, t("Instellingen"), "Herstart de app om de taal toe te passen.")

    def show_info(self):
        QMessageBox.information(self, t("ℹ️ Info"),
            f"{APP_NAME} v{APP_VERSION}\nEen {AUTHOR_NAME} product\n{WEBSITE_URL}")

    def _donate_status(self):
        btn = QPushButton(t("♥ Donatie")); btn.setObjectName("cta")
        btn.clicked.connect(self._donate)
        self.statusBar().addPermanentWidget(QLabel(f"v{APP_VERSION}"))
        self.statusBar().addPermanentWidget(btn)

    def _donate(self):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(DONATE_URL))

    def check_updates(self, silent=True):
        self._silent_upd = silent
        self._uw = _UpdateWorker(); self._uw.done.connect(self._on_update); self._uw.start()

    def _on_update(self, latest):
        if not latest:
            if not getattr(self, "_silent_upd", True):
                QMessageBox.information(self, t("Updates"), "Kon niet controleren op updates.")
            return
        if latest != APP_VERSION and latest > APP_VERSION:
            QMessageBox.information(self, t("Updates"),
                f"{t('Er is een nieuwe versie beschikbaar')}: v{latest}\n{WEBSITE_URL}")
        elif not getattr(self, "_silent_upd", True):
            QMessageBox.information(self, t("Updates"), t("Je gebruikt de nieuwste versie."))


# ----------------------------------------------------------------------------- main
def main():
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Dravenlock.DraveStudio")
        except Exception:
            pass
    app = QApplication(sys.argv)
    f = app.font(); f.setPointSize(10); app.setFont(f)
    app.setStyleSheet(DRAVENLOCK_QSS)
    ic = app_icon(); app.setWindowIcon(ic)

    from PyQt6.QtWidgets import QSplashScreen
    splash = QSplashScreen(make_splash_pixmap(), Qt.WindowType.WindowStaysOnTopHint)
    splash.show(); app.processEvents()

    win = DraveStudio(); win.setWindowIcon(ic)

    def _start():
        splash.finish(win); win.show()
        try:
            win.check_updates(silent=True)
        except Exception:
            pass

    QTimer.singleShot(1500, _start)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
