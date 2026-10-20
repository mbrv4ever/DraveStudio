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
import math
import random
import base64
import locale

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QPointF, QRect, QRectF, QTimer, QSize
from PyQt6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QFont, QPen, QIcon,
    QShortcut, QKeySequence, QRegion, QPolygon, QPainterPath,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSlider, QSpinBox, QToolButton, QFrame,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QDialog, QColorDialog,
    QTabWidget, QInputDialog, QStackedWidget,
    QScrollArea, QPlainTextEdit, QButtonGroup, QCheckBox, QSizePolicy, QFontComboBox,
)

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

try:
    import numpy as _np
    HAVE_NUMPY = True
except Exception:
    HAVE_NUMPY = False

APP_NAME = "DraveStudio"
APP_VERSION = "0.19"
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
        "Lasso": "Lasso", "Toverstaf": "Magic wand", "Toverstaf-tolerantie": "Magic wand tolerance",
        "Curven": "Curves",
        "Penseel": "Brush", "Nieuw…": "New…", "Importeren…": "Import…", "Nieuw penseel": "New brush",
        "Penseel importeren…": "Import brush…", "Naam": "Name", "Vorm": "Shape",
        "Zacht rond": "Soft round", "Hard rond": "Hard round", "Krijt": "Chalk", "Spray": "Spray",
        "Marker": "Marker", "Hardheid": "Hardness", "Tussenafstand": "Spacing", "Spreiding": "Scatter",
        "Vierkant": "Square", "Driehoek": "Triangle", "Zeshoek": "Hexagon", "Ster": "Star", "Hart": "Heart",
        "🎬 Acties": "🎬 Actions", "Acties & presets": "Actions & presets", "Acties": "Actions",
        "Looks": "Looks", "Palet": "Palette",
        "Afspelen": "Play", "Hernoemen": "Rename", "Opslaan als look": "Save as look",
        "● Opname starten": "● Start recording", "■ Opname stoppen": "■ Stop recording",
        "Opname loopt — stappen: ": "Recording — steps: ", "Actie opslaan": "Save action",
        "Mijn actie": "My action", "Toepassen": "Apply", "Gebruiken": "Use",
        "Huidige kleur toevoegen": "Add current colour", "Opgeslagen als look.": "Saved as look.",
        "Opgeslagen.": "Saved.", "Geïmporteerd.": "Imported.",
        "Ingebouwde looks kun je niet verwijderen.": "Built-in looks cannot be deleted.",
        "Geen stappen opgenomen. Pas tijdens de opname een aanpassing of filter toe.": "No steps recorded. Apply an adjustment or filter while recording.",
        "Neem een reeks aanpassingen op en speel ze met één klik af op de actieve laag.": "Record a series of adjustments and replay them on the active layer with one click.",
        "Kant-en-klare looks (en je eigen opgeslagen looks). Klik op Toepassen om ze op de actieve laag te zetten.": "Ready-made looks (and your saved looks). Click Apply to put them on the active layer.",
        "Bewaar je favoriete kleuren. Klik op Gebruiken om een kleur in te stellen.": "Save your favourite colours. Click Use to set a colour.",
        "Je eigen en geïmporteerde penselen. Importeer een PNG als penseelvorm.": "Your own and imported brushes. Import a PNG as a brush shape.",
        "✏️ Vectormodus": "✏️ Vector mode", "🖼 Rastermodus": "🖼 Raster mode", "Vectormodus (SVG)": "Vector mode (SVG)",
        "Vector": "Vector", "Selecteren": "Select", "Pen (pad)": "Pen (path)",
        "Pad sluiten": "Close path", "Pad afronden": "Finish path", "Stijl": "Style",
        "Vulling": "Fill", "Vulkleur": "Fill colour", "Lijnkleur": "Line colour", "Lijndikte": "Line width",
        "Stijl op selectie toepassen": "Apply style to selection", "Object": "Object",
        "Naar voren": "Bring forward", "Naar achteren": "Send back",
        "Tip: rechterklik = niets selecteren. Dubbelklik met de Pen rondt een pad af.": "Tip: right-click = deselect. Double-click with the Pen finishes a path.",
        "Mijn penseel": "My brush", "Penseel geïmporteerd en bewaard in de map 'penselen'.": "Brush imported and saved in the 'penselen' folder.", "Sleep op de lijn om punten te maken/verplaatsen (dubbelklik = punt weg).": "Drag on the line to add/move points (double-click = remove point).",
        "Tekengrootte": "Font size", "Ongedaan": "Undo", "Opnieuw": "Redo", "Passend": "Fit",
        "Vet": "Bold", "Schuin": "Italic",
        "Aanpassingen": "Adjustments", "Helderheid / Contrast": "Brightness / Contrast",
        "Tint / Verzadiging": "Hue / Saturation", "Vervagen": "Blur", "Verscherpen": "Sharpen",
        "Grijswaarden": "Grayscale", "Kleuren omkeren": "Invert colours",
        "Afbeelding": "Image", "Bijsnijden naar selectie": "Crop to selection",
        "90° rechtsom draaien": "Rotate 90° clockwise", "90° linksom draaien": "Rotate 90° counter-clockwise",
        "180° draaien": "Rotate 180°", "Horizontaal spiegelen": "Flip horizontal",
        "Verticaal spiegelen": "Flip vertical",
        "Maak eerst een selectie (rechthoek, lasso of toverstaf).": "Make a selection first (rectangle, lasso or magic wand).",
        "Dit werkt in de rastermodus.": "This works in raster mode.",
        "Helderheid": "Brightness", "Contrast": "Contrast", "Tint": "Hue", "Verzadiging": "Saturation",
        "Straal": "Radius", "Sterkte": "Amount", "Herstel": "Reset", "Toepassen": "Apply",
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
    raw = ""
    # Windows: de meest betrouwbare bron (geeft bv. "nl-NL")
    if os.name == "nt":
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85):
                raw = buf.value or ""
        except Exception:
            raw = ""
    if not raw:
        try:
            raw = locale.getlocale()[0] or ""
            if not raw:
                raw = locale.getdefaultlocale()[0] or ""
        except Exception:
            raw = ""
    if not raw:
        for env in ("LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES"):
            v = os.environ.get(env)
            if v:
                raw = v; break
    r = raw.lower()
    if (r.startswith("nl") or "dutch" in r or "nederland" in r
            or "netherlands" in r or "flemish" in r or "vlaams" in r):
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
#toolscroll { background-color: #0a0a0c; border: none; border-right: 1px solid #2a2a31; }
#toolscroll > QWidget > QWidget { background-color: #0a0a0c; }
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


# ----------------------------------------------------------------------------- penselen
BUILTIN_BRUSHES = [
    ("Zacht rond", "soft", 35, 12, 0),
    ("Hard rond", "hard", 90, 12, 0),
    ("Krijt", "chalk", 80, 18, 6),
    ("Spray", "spray", 100, 8, 0),
    ("Marker", "marker", 70, 10, 0),
    ("Vierkant", "square", 100, 22, 0),
    ("Driehoek", "triangle", 100, 24, 0),
    ("Zeshoek", "hexagon", 100, 24, 0),
    ("Ster", "star", 100, 28, 0),
    ("Hart", "heart", 100, 28, 0),
]

SHAPE_KINDS = ("square", "triangle", "hexagon", "star", "heart")


class Brush:
    def __init__(self, name, kind, hardness=80, spacing=12, jitter=0, custom_mask=None, builtin=True):
        self.name = name; self.kind = kind
        self.hardness = hardness; self.spacing = spacing; self.jitter = jitter
        self.custom_mask = custom_mask     # PIL 'L'-beeld voor geïmporteerde penselen
        self.builtin = builtin

    @property
    def random(self):
        return self.kind in ("spray", "chalk")

    def mask(self, size):
        """Grijswaarde-dekkingsmasker (numpy uint8, size×size)."""
        size = max(1, int(size))
        if self.kind == "image" and self.custom_mask is not None:
            m = self.custom_mask.resize((size, size))
            return _np.asarray(m, dtype=_np.uint8)
        if self.kind in SHAPE_KINDS:
            return self._shape_mask(size)
        yy, xx = _np.mgrid[0:size, 0:size]
        c = (size - 1) / 2.0
        r = max(1e-6, size / 2.0)
        d = _np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / r       # 0=midden, 1=rand
        h = self.hardness / 100.0
        if self.kind == "hard":
            a = _np.clip((1.0 - d) * r, 0, 1)
        elif self.kind == "marker":
            a = _np.clip((1.0 - d) * r, 0, 1) * 0.75
        elif self.kind == "spray":
            a = ((_np.random.rand(size, size) < 0.05) & (d <= 1.0)).astype(_np.float32)
        elif self.kind == "chalk":
            base = (d <= 1.0).astype(_np.float32)
            a = base * (_np.random.rand(size, size) < 0.72)
        else:  # soft
            a = _np.clip((1.0 - d) / max(1e-6, (1.0 - h)), 0, 1)
            a[d <= h] = 1.0; a[d >= 1.0] = 0.0
        return (a * 255).astype(_np.uint8)

    def to_dict(self):
        return {"name": self.name, "kind": self.kind, "hardness": self.hardness,
                "spacing": self.spacing, "jitter": self.jitter}

    def _shape_mask(self, size):
        size = max(1, int(size))
        img = QImage(size, size, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(255, 255, 255))
        cx = cy = size / 2.0
        r = size / 2.0 * 0.94
        path = QPainterPath()
        if self.kind == "square":
            m = size * 0.07
            path.addRect(m, m, size - 2 * m, size - 2 * m)
        elif self.kind == "triangle":
            pts = [(cx + r * math.sin(a), cy - r * math.cos(a))
                   for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.closeSubpath()
        elif self.kind == "hexagon":
            pts = [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3),
                    cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.closeSubpath()
        elif self.kind == "star":
            n = 5; outer = r; inner = r * 0.42; first = True
            for i in range(2 * n):
                rad = outer if i % 2 == 0 else inner
                a = -math.pi / 2 + i * math.pi / n
                x = cx + rad * math.cos(a); y = cy + rad * math.sin(a)
                path.moveTo(x, y) if first else path.lineTo(x, y); first = False
            path.closeSubpath()
        elif self.kind == "heart":
            first = True
            for k in range(0, 361, 5):
                tt = math.radians(k)
                hx = 16 * (math.sin(tt) ** 3)
                hy = 13 * math.cos(tt) - 5 * math.cos(2 * tt) - 2 * math.cos(3 * tt) - math.cos(4 * tt)
                x = cx + hx / 17.0 * r; y = cy - hy / 17.0 * r
                path.moveTo(x, y) if first else path.lineTo(x, y); first = False
            path.closeSubpath()
        p.drawPath(path); p.end()
        img = img.convertToFormat(QImage.Format.Format_RGBA8888)
        ptr = img.bits(); ptr.setsize(img.sizeInBytes())
        arr = _np.frombuffer(bytes(ptr), dtype=_np.uint8).reshape(size, size, 4)
        return arr[..., 3].copy()


# ----------------------------------------------------------------------------- image helpers (PIL)
def qimage_to_pil(qimg):
    img = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
    w, h = img.width(), img.height()
    ptr = img.bits(); ptr.setsize(img.sizeInBytes())
    return Image.frombytes("RGBA", (w, h), bytes(ptr))


def pil_to_qimage(pil):
    pil = pil.convert("RGBA")
    data = pil.tobytes("raw", "RGBA")
    q = QImage(data, pil.width, pil.height, QImage.Format.Format_RGBA8888)
    return q.convertToFormat(QImage.Format.Format_ARGB32).copy()


def _apply_rgb(pil, fn):
    """Pas fn toe op de RGB-kanalen en behoud het alpha-kanaal."""
    pil = pil.convert("RGBA")
    r, g, b, a = pil.split()
    rgb = fn(Image.merge("RGB", (r, g, b)))
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def adj_brightness_contrast(pil, p):
    out = _apply_rgb(pil, lambda im: ImageEnhance.Brightness(im).enhance(p["bright"] / 100.0))
    out = _apply_rgb(out, lambda im: ImageEnhance.Contrast(im).enhance(p["contrast"] / 100.0))
    return out


def adj_hue_sat(pil, p):
    out = _apply_rgb(pil, lambda im: ImageEnhance.Color(im).enhance(p["sat"] / 100.0))
    deg = p["hue"]
    if deg:
        off = int(deg / 360.0 * 255) % 256

        def huef(im):
            H, S, V = im.convert("HSV").split()
            H = H.point(lambda x: (x + off) % 256)
            return Image.merge("HSV", (H, S, V)).convert("RGB")
        out = _apply_rgb(out, huef)
    return out


def adj_blur(pil, p):
    return _apply_rgb(pil, lambda im: im.filter(ImageFilter.GaussianBlur(p["radius"] / 10.0)))


def adj_sharpen(pil, p):
    return _apply_rgb(pil, lambda im: im.filter(
        ImageFilter.UnsharpMask(radius=2, percent=p["amount"], threshold=2)))


def adj_grayscale(pil):
    return _apply_rgb(pil, lambda im: ImageOps.grayscale(im).convert("RGB"))


def adj_invert(pil):
    return _apply_rgb(pil, lambda im: ImageOps.invert(im))


def lut_from_points(points):
    pts = sorted([list(p) for p in points])
    out = []
    for x in range(256):
        y = pts[-1][1]
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            if x0 <= x <= x1:
                y = y1 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                break
        out.append(int(max(0, min(255, round(y)))))
    return out


def adj_curves(pil, p):
    lut = lut_from_points(p.get("points", [[0, 0], [255, 255]]))
    return _apply_rgb(pil, lambda im: im.point(lut * 3))


# aanpassings-bewerkingen die je kunt opnemen/afspelen
ADJUST_FUNCS = {
    "bright_contrast": adj_brightness_contrast,
    "hue_sat": adj_hue_sat,
    "blur": adj_blur,
    "sharpen": adj_sharpen,
    "curves": adj_curves,
    "grayscale": lambda pil, p: adj_grayscale(pil),
    "invert": lambda pil, p: adj_invert(pil),
}

OP_LABELS = {
    "bright_contrast": "Helderheid / Contrast", "hue_sat": "Tint / Verzadiging",
    "blur": "Vervagen", "sharpen": "Verscherpen", "curves": "Curven",
    "grayscale": "Grijswaarden", "invert": "Kleuren omkeren",
}

# ingebouwde "looks" (presets) — vaste reeksen bewerkingen
BUILTIN_LOOKS = [
    ("Zwart-wit", [{"op": "grayscale", "params": {}}]),
    ("Negatief", [{"op": "invert", "params": {}}]),
    ("Hoog contrast", [{"op": "bright_contrast", "params": {"bright": 100, "contrast": 155}}]),
    ("Zachter", [{"op": "blur", "params": {"radius": 18}}]),
    ("Scherper", [{"op": "sharpen", "params": {"amount": 140}}]),
    ("Warm", [{"op": "hue_sat", "params": {"hue": 12, "sat": 115}}]),
    ("Koel", [{"op": "hue_sat", "params": {"hue": -12, "sat": 105}}]),
    ("Levendig", [{"op": "hue_sat", "params": {"hue": 0, "sat": 145}},
                  {"op": "bright_contrast", "params": {"bright": 103, "contrast": 112}}]),
]


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
# ----------------------------------------------------------------------------- vector (SVG) laag
def _col_name(c):
    return "none" if c is None else c.name()


class VShape:
    """Eén vector-object: rechthoek, ovaal, lijn, pad of tekst."""
    def __init__(self, kind, fill=None, stroke=None, stroke_w=2, **g):
        self.kind = kind
        self.fill = fill                 # QColor of None
        self.stroke = stroke             # QColor of None
        self.stroke_w = stroke_w
        self.x = g.get("x", 0.0); self.y = g.get("y", 0.0)
        self.w = g.get("w", 0.0); self.h = g.get("h", 0.0)
        self.x2 = g.get("x2", 0.0); self.y2 = g.get("y2", 0.0)
        self.points = list(g.get("points", []))
        self.closed = g.get("closed", False)
        self.text = g.get("text", ""); self.family = g.get("family", "Arial")
        self.size = g.get("size", 32)
        self.bold = g.get("bold", False); self.italic = g.get("italic", False)

    def _font(self):
        f = QFont(self.family); f.setPixelSize(max(1, int(self.size)))
        f.setBold(bool(self.bold)); f.setItalic(bool(self.italic))
        return f

    def qpath(self):
        p = QPainterPath()
        if self.kind == "rect":
            p.addRect(QRectF(self.x, self.y, self.w, self.h))
        elif self.kind == "ellipse":
            p.addEllipse(QRectF(self.x, self.y, self.w, self.h))
        elif self.kind == "line":
            p.moveTo(self.x, self.y); p.lineTo(self.x2, self.y2)
        elif self.kind == "path" and self.points:
            p.moveTo(*self.points[0])
            for q in self.points[1:]:
                p.lineTo(*q)
            if self.closed:
                p.closeSubpath()
        elif self.kind == "text":
            p.addText(QPointF(self.x, self.y), self._font(), self.text or " ")
        return p

    def bounds(self):
        return self.qpath().boundingRect()

    def contains(self, pt):
        b = self.bounds().adjusted(-4, -4, 4, 4)
        if self.kind == "text":
            return b.contains(pt)
        if not b.contains(pt):
            return False
        if self.kind in ("rect", "ellipse") or (self.kind == "path" and self.closed):
            pp = self.qpath()
            if self.fill is not None:
                return pp.contains(pt)
            # alleen omtrek: dicht bij de rand
            return self._near_path(pt)
        return self._near_path(pt)

    def _near_path(self, pt, tol=5):
        pp = self.qpath()
        n = 80
        for i in range(n + 1):
            q = pp.pointAtPercent(i / n)
            if abs(q.x() - pt.x()) <= tol and abs(q.y() - pt.y()) <= tol:
                return True
        return False

    def translate(self, dx, dy):
        self.x += dx; self.y += dy; self.x2 += dx; self.y2 += dy
        self.points = [(px + dx, py + dy) for (px, py) in self.points]

    def scale_about(self, ox, oy, sx, sy):
        def m(x, y):
            return (ox + (x - ox) * sx, oy + (y - oy) * sy)
        if self.kind in ("rect", "ellipse"):
            x0, y0 = m(self.x, self.y); x1, y1 = m(self.x + self.w, self.y + self.h)
            self.x = min(x0, x1); self.y = min(y0, y1)
            self.w = abs(x1 - x0); self.h = abs(y1 - y0)
        elif self.kind == "line":
            self.x, self.y = m(self.x, self.y); self.x2, self.y2 = m(self.x2, self.y2)
        elif self.kind == "path":
            self.points = [m(px, py) for (px, py) in self.points]
        elif self.kind == "text":
            self.x, self.y = m(self.x, self.y)
            self.size = max(4.0, self.size * sy)

    def render(self, painter):
        painter.save()
        pen = QPen(self.stroke, self.stroke_w) if self.stroke is not None else QPen(Qt.PenStyle.NoPen)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        if self.kind == "text":
            painter.setFont(self._font())
            painter.setPen(self.fill or self.stroke or QColor("#000000"))
            painter.drawText(QPointF(self.x, self.y), self.text)
        elif self.kind == "line":
            painter.setPen(QPen(self.stroke or QColor("#000000"), self.stroke_w,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(self.x, self.y), QPointF(self.x2, self.y2))
        else:
            painter.setPen(pen)
            painter.setBrush(self.fill if self.fill is not None else Qt.BrushStyle.NoBrush)
            if self.kind == "rect":
                painter.drawRect(QRectF(self.x, self.y, self.w, self.h))
            elif self.kind == "ellipse":
                painter.drawEllipse(QRectF(self.x, self.y, self.w, self.h))
            elif self.kind == "path":
                painter.drawPath(self.qpath())
        painter.restore()

    def to_svg(self):
        f = _col_name(self.fill); s = _col_name(self.stroke); sw = self.stroke_w
        if self.kind == "rect":
            return (f'<rect x="{self.x:.2f}" y="{self.y:.2f}" width="{self.w:.2f}" '
                    f'height="{self.h:.2f}" fill="{f}" stroke="{s}" stroke-width="{sw}"/>')
        if self.kind == "ellipse":
            return (f'<ellipse cx="{self.x + self.w / 2:.2f}" cy="{self.y + self.h / 2:.2f}" '
                    f'rx="{abs(self.w) / 2:.2f}" ry="{abs(self.h) / 2:.2f}" '
                    f'fill="{f}" stroke="{s}" stroke-width="{sw}"/>')
        if self.kind == "line":
            return (f'<line x1="{self.x:.2f}" y1="{self.y:.2f}" x2="{self.x2:.2f}" '
                    f'y2="{self.y2:.2f}" stroke="{s if self.stroke else "#000000"}" '
                    f'stroke-width="{sw}" stroke-linecap="round"/>')
        if self.kind == "path" and self.points:
            d = "M " + " L ".join(f"{px:.2f} {py:.2f}" for px, py in self.points)
            if self.closed:
                d += " Z"
            return (f'<path d="{d}" fill="{f if self.closed else "none"}" '
                    f'stroke="{s}" stroke-width="{sw}" stroke-linejoin="round" '
                    f'stroke-linecap="round"/>')
        if self.kind == "text":
            import html
            extra = ""
            if self.bold:
                extra += ' font-weight="bold"'
            if self.italic:
                extra += ' font-style="italic"'
            return (f'<text x="{self.x:.2f}" y="{self.y:.2f}" font-family="{self.family}" '
                    f'font-size="{self.size}"{extra} '
                    f'fill="{self.fill.name() if self.fill else "#000000"}">'
                    f'{html.escape(self.text)}</text>')
        return ""

    def clone(self):
        return VShape(self.kind, fill=QColor(self.fill) if self.fill else None,
                      stroke=QColor(self.stroke) if self.stroke else None, stroke_w=self.stroke_w,
                      x=self.x, y=self.y, w=self.w, h=self.h, x2=self.x2, y2=self.y2,
                      points=list(self.points), closed=self.closed,
                      text=self.text, family=self.family, size=self.size,
                      bold=self.bold, italic=self.italic)


def _parse_color(v):
    if v is None or v == "none" or v == "":
        return None
    c = QColor(v)
    return c if c.isValid() else None


class VectorScene:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.shapes = []

    def add(self, sh):
        self.shapes.append(sh)

    def hit(self, pt):
        for i in range(len(self.shapes) - 1, -1, -1):
            if self.shapes[i].contains(pt):
                return i
        return -1

    def render(self, painter):
        for sh in self.shapes:
            sh.render(painter)

    def to_qimage(self, scale=1.0, transparent=True):
        w = max(1, int(self.w * scale)); h = max(1, int(self.h * scale))
        img = QImage(w, h, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent if transparent else Qt.GlobalColor.white)
        p = QPainter(img); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.scale(scale, scale); self.render(p); p.end()
        return img

    def to_svg(self):
        body = "\n".join("  " + s.to_svg() for s in self.shapes if s.to_svg())
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n{body}\n</svg>\n')

    @staticmethod
    def from_svg(text):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(text)

        def tag(e):
            return e.tag.split("}")[-1]
        w = float(root.get("width", 800) or 800); h = float(root.get("height", 600) or 600)
        sc = VectorScene(int(w), int(h))

        def style(e):
            return dict(fill=_parse_color(e.get("fill", "#000000")),
                        stroke=_parse_color(e.get("stroke")),
                        stroke_w=float(e.get("stroke-width", 1) or 1))

        for e in root.iter():
            tg = tag(e)
            st = style(e)
            if tg == "rect":
                sc.add(VShape("rect", x=float(e.get("x", 0)), y=float(e.get("y", 0)),
                              w=float(e.get("width", 0)), h=float(e.get("height", 0)), **st))
            elif tg == "ellipse":
                cx = float(e.get("cx", 0)); cy = float(e.get("cy", 0))
                rx = float(e.get("rx", 0)); ry = float(e.get("ry", 0))
                sc.add(VShape("ellipse", x=cx - rx, y=cy - ry, w=rx * 2, h=ry * 2, **st))
            elif tg == "circle":
                cx = float(e.get("cx", 0)); cy = float(e.get("cy", 0)); r = float(e.get("r", 0))
                sc.add(VShape("ellipse", x=cx - r, y=cy - r, w=r * 2, h=r * 2, **st))
            elif tg == "line":
                sc.add(VShape("line", x=float(e.get("x1", 0)), y=float(e.get("y1", 0)),
                              x2=float(e.get("x2", 0)), y2=float(e.get("y2", 0)), **st))
            elif tg == "path":
                pts, closed = _parse_path_d(e.get("d", ""))
                if pts:
                    sc.add(VShape("path", points=pts, closed=closed, **st))
            elif tg == "text":
                sc.add(VShape("text", x=float(e.get("x", 0)), y=float(e.get("y", 0)),
                              text=(e.text or ""), family=e.get("font-family", "Arial"),
                              size=float(e.get("font-size", 32) or 32),
                              bold=("bold" in (e.get("font-weight", "") or "")),
                              italic=("italic" in (e.get("font-style", "") or "")),
                              fill=_parse_color(e.get("fill", "#000000")), stroke=None))
        return sc


def _parse_path_d(d):
    """Eenvoudige parser voor 'M x y L x y ... [Z]' (onze eigen paden)."""
    pts = []; closed = False
    toks = d.replace(",", " ").split()
    i = 0
    while i < len(toks):
        tk = toks[i]
        if tk in ("M", "L"):
            try:
                x = float(toks[i + 1]); y = float(toks[i + 2]); pts.append((x, y)); i += 3
            except (IndexError, ValueError):
                i += 1
        elif tk in ("Z", "z"):
            closed = True; i += 1
        else:
            try:
                x = float(toks[i]); y = float(toks[i + 1]); pts.append((x, y)); i += 2
            except (IndexError, ValueError):
                i += 1
    return pts, closed


# ----------------------------------------------------------------------------- vector canvas (interactief)
class VectorCanvas(QWidget):
    changed = pyqtSignal()
    cursorMoved = pyqtSignal(int, int)
    selectionChanged = pyqtSignal()

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.zoom = 1.0
        self.tool = "select"
        self.fill = QColor("#6fa3d6")
        self.stroke = QColor("#222222")
        self.stroke_w = 2
        self.use_fill = True
        self.use_stroke = True
        self.text_handler = None
        self.sel = -1                      # geselecteerd object-index
        self._drag = None                  # 'new' | 'move'
        self._start = None
        self._tmp = None                   # vorm in aanmaak
        self._move_last = None
        self._pre_move = None
        self._moved = False
        self._resize = None
        self._pen_points = None
        self.undo_stack = []; self.redo_stack = []
        self.setMouseTracking(True)
        self._update_size()

    def _update_size(self):
        self.setFixedSize(int(self.scene.w * self.zoom), int(self.scene.h * self.zoom))
        self.update()

    def set_zoom(self, z):
        self.zoom = max(0.1, min(8.0, z)); self._update_size()

    def wheelEvent(self, ev):
        d = ev.angleDelta().y()
        if d == 0:
            return
        self.set_zoom(self.zoom * (1.15 if d > 0 else 1 / 1.15)); ev.accept()

    def _to_scene(self, pos):
        return QPointF(pos.x() / self.zoom, pos.y() / self.zoom)

    # -- undo
    def push_undo(self):
        self.undo_stack.append([s.clone() for s in self.scene.shapes])
        if len(self.undo_stack) > 40:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append([s.clone() for s in self.scene.shapes])
            self.scene.shapes = self.undo_stack.pop()
            self.sel = min(self.sel, len(self.scene.shapes) - 1)
            self.update(); self.changed.emit(); self.selectionChanged.emit()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append([s.clone() for s in self.scene.shapes])
            self.scene.shapes = self.redo_stack.pop()
            self.update(); self.changed.emit(); self.selectionChanged.emit()

    def _cur_fill(self):
        return QColor(self.fill) if self.use_fill else None

    def _cur_stroke(self):
        return QColor(self.stroke) if self.use_stroke else None

    # -- paint
    def paintEvent(self, ev):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # checkerboard
        s = 12; light = QColor("#3a3a42"); dark = QColor("#2b2b31")
        p.fillRect(self.rect(), dark)
        for y in range(0, self.height(), s):
            for x in range(0, self.width(), s):
                if ((x // s) + (y // s)) % 2 == 0:
                    p.fillRect(x, y, s, s, light)
        p.save(); p.scale(self.zoom, self.zoom)
        # witte "papier"-achtergrond van het canvas
        p.fillRect(QRectF(0, 0, self.scene.w, self.scene.h), QColor("#ffffff"))
        self.scene.render(p)
        if self._tmp is not None:
            self._tmp.render(p)
        if self._pen_points and len(self._pen_points) >= 1:
            pen = QPen(self._cur_stroke() or QColor("#222"), self.stroke_w)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            for i in range(1, len(self._pen_points)):
                p.drawLine(QPointF(*self._pen_points[i - 1]), QPointF(*self._pen_points[i]))
        p.restore()
        # selectie-kader
        if 0 <= self.sel < len(self.scene.shapes):
            b = self.scene.shapes[self.sel].bounds()
            r = QRectF(b.x() * self.zoom, b.y() * self.zoom, b.width() * self.zoom, b.height() * self.zoom)
            r = r.adjusted(-3, -3, 3, 3)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(0, 0, 0), 2)); p.drawRect(r)
            wp = QPen(QColor("#6fa3d6"), 2); wp.setStyle(Qt.PenStyle.DashLine)
            p.setPen(wp); p.drawRect(r)
            # schaalgrepen
            p.setPen(QPen(QColor(0, 0, 0), 1)); p.setBrush(QColor("#ffffff"))
            for (hx, hy) in self._handles():
                p.drawRect(QRectF(hx * self.zoom - 4, hy * self.zoom - 4, 8, 8))
        p.setPen(QPen(QColor("#2a2a31"), 1)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()

    def _handles(self):
        if not (0 <= self.sel < len(self.scene.shapes)):
            return []
        b = self.scene.shapes[self.sel].bounds().adjusted(-3, -3, 3, 3)
        l, t_, r, bo = b.left(), b.top(), b.right(), b.bottom()
        cx, cy = (l + r) / 2, (t_ + bo) / 2
        return [(l, t_), (cx, t_), (r, t_), (r, cy), (r, bo), (cx, bo), (l, bo), (l, cy)]

    def _handle_at(self, sp):
        tol = 8 / max(0.1, self.zoom)
        for i, (hx, hy) in enumerate(self._handles()):
            if abs(hx - sp.x()) <= tol and abs(hy - sp.y()) <= tol:
                return i
        return -1

    # -- mouse
    def mousePressEvent(self, ev):
        sp = self._to_scene(ev.position())
        if ev.button() == Qt.MouseButton.RightButton:
            self.sel = -1; self.update(); self.selectionChanged.emit(); return
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        if self.tool == "select":
            # eerst: greep van het geselecteerde object?
            if 0 <= self.sel < len(self.scene.shapes):
                hidx = self._handle_at(sp)
                if hidx >= 0:
                    b = self.scene.shapes[self.sel].bounds()
                    anchors = {0: (b.right(), b.bottom()), 1: (b.left(), b.bottom()),
                               2: (b.left(), b.bottom()), 3: (b.left(), b.top()),
                               4: (b.left(), b.top()), 5: (b.left(), b.top()),
                               6: (b.right(), b.top()), 7: (b.right(), b.top())}
                    self._resize = {"h": hidx, "ax": anchors[hidx][0], "ay": anchors[hidx][1],
                                    "ow": max(1.0, b.width()), "oh": max(1.0, b.height()),
                                    "orig": self.scene.shapes[self.sel].clone()}
                    self._pre_move = [s.clone() for s in self.scene.shapes]
                    self._drag = "resize"; self._moved = False
                    return
            idx = self.scene.hit(sp)
            self.sel = idx
            if idx >= 0:
                self._pre_move = [s.clone() for s in self.scene.shapes]
                self._drag = "move"; self._move_last = sp; self._moved = False
            self.update(); self.selectionChanged.emit()
        elif self.tool == "text":
            idx = self.scene.hit(sp)
            if idx >= 0 and self.scene.shapes[idx].kind == "text":
                self.sel = idx; self.update(); self.selectionChanged.emit()
                if self.text_handler:
                    self.text_handler(sp, idx)
            elif self.text_handler:
                self.text_handler(sp, None)
        elif self.tool == "pen":
            if self._pen_points is None:
                self._pen_points = [(sp.x(), sp.y())]
            else:
                self._pen_points.append((sp.x(), sp.y()))
            self.update()
        else:  # rect / ellipse / line
            self._drag = "new"; self._start = sp
            self._tmp = self._make_shape(sp, sp)

    def mouseMoveEvent(self, ev):
        sp = self._to_scene(ev.position())
        self.cursorMoved.emit(int(sp.x()), int(sp.y()))
        if self._drag == "new" and self._start is not None:
            self._tmp = self._make_shape(self._start, sp)
            self.update()
        elif self._drag == "resize" and self._resize is not None and 0 <= self.sel < len(self.scene.shapes):
            rz = self._resize; h = rz["h"]
            both = h in (0, 2, 4, 6); only_y = h in (1, 5); only_x = h in (3, 7)
            sx = 1.0; sy = 1.0
            if both or only_x:
                sx = max(2.0, abs(sp.x() - rz["ax"])) / rz["ow"]
            if both or only_y:
                sy = max(2.0, abs(sp.y() - rz["ay"])) / rz["oh"]
            sh = rz["orig"].clone(); sh.scale_about(rz["ax"], rz["ay"], sx, sy)
            self.scene.shapes[self.sel] = sh
            self._moved = True; self.update(); self.changed.emit()
        elif self._drag == "move" and self._move_last is not None and 0 <= self.sel < len(self.scene.shapes):
            dx = sp.x() - self._move_last.x(); dy = sp.y() - self._move_last.y()
            self.scene.shapes[self.sel].translate(dx, dy)
            self._move_last = sp; self._moved = True; self.update(); self.changed.emit()

    def mouseReleaseEvent(self, ev):
        if self._drag == "new" and self._tmp is not None:
            # alleen toevoegen als hij groot genoeg is
            b = self._tmp.bounds()
            if b.width() >= 2 or b.height() >= 2 or self._tmp.kind == "line":
                self.push_undo(); self.scene.add(self._tmp)
                self.sel = len(self.scene.shapes) - 1
                self.changed.emit(); self.selectionChanged.emit()
            self._tmp = None
        elif self._drag in ("move", "resize") and getattr(self, "_moved", False) and self._pre_move is not None:
            # één versleep-/schaal-actie = één undo-stap
            self.undo_stack.append(self._pre_move)
            if len(self.undo_stack) > 60:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
        self._pre_move = None; self._moved = False; self._resize = None
        self._drag = None; self._start = None; self._move_last = None
        self.update()

    def mouseDoubleClickEvent(self, ev):
        sp = self._to_scene(ev.position())
        idx = self.scene.hit(sp)
        if idx >= 0 and self.scene.shapes[idx].kind == "text":
            self.sel = idx; self.update(); self.selectionChanged.emit()
            if self.text_handler:
                self.text_handler(sp, idx)
            return
        # pen afronden bij dubbelklik
        if self.tool == "pen" and self._pen_points and len(self._pen_points) >= 2:
            self.push_undo()
            self.scene.add(VShape("path", points=list(self._pen_points), closed=False,
                                  fill=None, stroke=self._cur_stroke() or QColor("#222"),
                                  stroke_w=self.stroke_w))
            self.sel = len(self.scene.shapes) - 1
            self._pen_points = None
            self.update(); self.changed.emit(); self.selectionChanged.emit()

    def finish_pen(self, closed=False):
        if self._pen_points and len(self._pen_points) >= 2:
            self.push_undo()
            self.scene.add(VShape("path", points=list(self._pen_points), closed=closed,
                                  fill=self._cur_fill() if closed else None,
                                  stroke=self._cur_stroke() or QColor("#222"), stroke_w=self.stroke_w))
            self.sel = len(self.scene.shapes) - 1
            self._pen_points = None
            self.update(); self.changed.emit(); self.selectionChanged.emit()

    def _make_shape(self, p0, p1):
        x = min(p0.x(), p1.x()); y = min(p0.y(), p1.y())
        w = abs(p1.x() - p0.x()); h = abs(p1.y() - p0.y())
        if self.tool == "rect":
            return VShape("rect", x=x, y=y, w=w, h=h, fill=self._cur_fill(),
                          stroke=self._cur_stroke(), stroke_w=self.stroke_w)
        if self.tool == "ellipse":
            return VShape("ellipse", x=x, y=y, w=w, h=h, fill=self._cur_fill(),
                          stroke=self._cur_stroke(), stroke_w=self.stroke_w)
        if self.tool == "line":
            return VShape("line", x=p0.x(), y=p0.y(), x2=p1.x(), y2=p1.y(),
                          stroke=self._cur_stroke() or QColor("#222"), stroke_w=self.stroke_w)
        return VShape("rect", x=x, y=y, w=w, h=h)

    def add_text(self, sp, text, family, size, bold=False, italic=False):
        if not text.strip():
            return
        self.push_undo()
        self.scene.add(VShape("text", x=sp.x(), y=sp.y(), text=text, family=family,
                              size=size, bold=bold, italic=italic,
                              fill=self._cur_fill() or QColor("#222"), stroke=None))
        self.sel = len(self.scene.shapes) - 1
        self.update(); self.changed.emit(); self.selectionChanged.emit()

    def delete_selected(self):
        if 0 <= self.sel < len(self.scene.shapes):
            self.push_undo(); del self.scene.shapes[self.sel]; self.sel = -1
            self.update(); self.changed.emit(); self.selectionChanged.emit()

    def apply_style_to_selected(self):
        if 0 <= self.sel < len(self.scene.shapes):
            self.push_undo()
            sh = self.scene.shapes[self.sel]
            if sh.kind == "text":
                sh.fill = self._cur_fill() or QColor("#222")
            else:
                sh.fill = self._cur_fill(); sh.stroke = self._cur_stroke(); sh.stroke_w = self.stroke_w
            self.update(); self.changed.emit()

    def raise_selected(self, up=True):
        i = self.sel
        if 0 <= i < len(self.scene.shapes):
            j = i + 1 if up else i - 1
            if 0 <= j < len(self.scene.shapes):
                self.push_undo()
                self.scene.shapes[i], self.scene.shapes[j] = self.scene.shapes[j], self.scene.shapes[i]
                self.sel = j; self.update(); self.changed.emit(); self.selectionChanged.emit()


class Canvas(QWidget):
    cursorMoved = pyqtSignal(int, int)
    changed = pyqtSignal()          # project content/structure changed
    zoomChanged = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.zoom = 1.0
        self.tool = "brush"
        self.color = QColor("#e0e0e0")
        self.brush_size = 12
        self.brush = Brush(*BUILTIN_BRUSHES[0])
        self._stamp_cache = {}
        self.setMouseTracking(True)
        self._last = None
        self._drawing = False
        self._move_origin = None
        self._move_start_img = None
        self.selection = None          # QRegion in beeld-coördinaten, of None
        self._sel_origin = None
        self._sel_rect = None          # live rechthoek-voorbeeld
        self._lasso_pts = None         # live lasso-punten
        self.wand_tolerance = 32
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

    def wheelEvent(self, ev):
        d = ev.angleDelta().y()
        if d == 0:
            return
        self.set_zoom(self.zoom * (1.15 if d > 0 else 1 / 1.15))
        self.zoomChanged.emit(); ev.accept()

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

    def _project_state(self):
        return ("project", self.project.width, self.project.height,
                [l.image.copy() for l in self.project.layers])

    def _restore_project(self, st):
        _, w, h, imgs = st
        if len(imgs) != len(self.project.layers):
            return
        self.project.width, self.project.height = w, h
        for l, im in zip(self.project.layers, imgs):
            l.image = im
        self.selection = None
        self._update_size(); self.changed.emit()

    def undo(self):
        if not self.undo_stack:
            return
        if self.undo_stack[-1][0] == "project":
            st = self.undo_stack.pop()
            self.redo_stack.append(self._project_state())
            self._restore_project(st); return
        idx, img = self.undo_stack.pop()
        if idx < len(self.project.layers):
            self.redo_stack.append((idx, self.project.layers[idx].image.copy()))
            self.project.layers[idx].image = img
            self.update(); self.changed.emit()

    def redo(self):
        if not self.redo_stack:
            return
        if self.redo_stack[-1][0] == "project":
            st = self.redo_stack.pop()
            self.undo_stack.append(self._project_state())
            self._restore_project(st); return
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
        # selectie tonen (exacte vorm via lichte tint + dikke dansende rand)
        if self.selection is not None and not self.selection.isEmpty():
            p.save(); p.scale(self.zoom, self.zoom)
            p.setClipRegion(self.selection)
            p.fillRect(self.selection.boundingRect(), QColor(111, 163, 214, 50))
            p.setClipping(False)
            p.setBrush(Qt.BrushStyle.NoBrush)
            path = QPainterPath(); path.addRegion(self.selection); path = path.simplified()
            black = QPen(QColor(0, 0, 0), 2.4); black.setCosmetic(True)
            p.setPen(black); p.drawPath(path)
            white = QPen(QColor(255, 255, 255), 2.4); white.setCosmetic(True)
            white.setStyle(Qt.PenStyle.DashLine); white.setDashPattern([5, 5])
            white.setDashOffset(self._ants)
            p.setPen(white); p.drawPath(path)
            p.restore()
        # live voorbeeld tijdens slepen
        if self._sel_rect is not None:
            sr = self._scaled_rect(self._sel_rect)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(0, 0, 0), 2)); p.drawRect(sr)
            wp = QPen(QColor(255, 255, 255), 2); wp.setStyle(Qt.PenStyle.DashLine)
            p.setPen(wp); p.drawRect(sr)
        if self._lasso_pts:
            p.save(); p.scale(self.zoom, self.zoom)
            p.setBrush(Qt.BrushStyle.NoBrush)
            bp = QPen(QColor(0, 0, 0), 2.4); bp.setCosmetic(True)
            p.setPen(bp); p.drawPolyline(QPolygon(self._lasso_pts))
            wp = QPen(QColor(255, 255, 255), 2.4); wp.setCosmetic(True); wp.setStyle(Qt.PenStyle.DashLine)
            p.setPen(wp); p.drawPolyline(QPolygon(self._lasso_pts))
            p.restore()
        p.end()

    def _scaled_rect(self, r):
        return QRect(int(r.x() * self.zoom), int(r.y() * self.zoom),
                     int(r.width() * self.zoom), int(r.height() * self.zoom))

    def selection_clip(self):
        """De selectie als QRegion (voor clipping), of None."""
        if self.selection is not None and not self.selection.isEmpty():
            return self.selection
        return None

    def clear_selection(self):
        self.selection = None; self._sel_rect = None; self._lasso_pts = None; self.update()

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
        if ev.button() == Qt.MouseButton.RightButton:
            self.clear_selection(); return
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
            self._sel_rect = QRect(ip, ip)
            self.update()
        elif self.tool == "lasso":
            self._lasso_pts = [ip]
            self.update()
        elif self.tool == "wand":
            self._magic_wand(ip)
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
            self._sel_rect = QRect(self._sel_origin, ip).normalized()
            self.update()
        elif self.tool == "lasso" and self._lasso_pts is not None:
            self._lasso_pts.append(ip)
            self.update()
        elif self.tool in ("rect", "ellipse", "line") and self._shape_origin is not None:
            self.active_layer().image = self._shape_start_img.copy()
            self._draw_shape(self._shape_origin, ip)

    def mouseReleaseEvent(self, ev):
        self._drawing = False; self._last = None
        self._move_origin = None; self._move_start_img = None
        self._shape_origin = None; self._shape_start_img = None
        bounds = QRect(0, 0, self.project.width, self.project.height)
        if self.tool == "select" and self._sel_origin is not None:
            self._sel_origin = None
            r = self._sel_rect; self._sel_rect = None
            if r is not None and r.width() >= 3 and r.height() >= 3:
                self.selection = QRegion(r.intersected(bounds))
            else:
                self.selection = None
            self.update()
        elif self.tool == "lasso" and self._lasso_pts is not None:
            pts = self._lasso_pts; self._lasso_pts = None
            if pts and len(pts) >= 3:
                self.selection = QRegion(QPolygon(pts), Qt.FillRule.WindingFill).intersected(QRegion(bounds))
            self.update()

    def _draw_shape(self, p0, p1):
        lyr = self.active_layer()
        painter = QPainter(lyr.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self.selection_clip()
        if clip is not None:
            painter.setClipRegion(clip)
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

    def set_brush(self, brush):
        self.brush = brush
        self._stamp_cache.clear()

    def _stamp_qimage(self, size, color):
        """Gekleurde (of witte voor gum) stempel als RGBA-beeld."""
        size = max(1, int(size))
        key = (self.brush.name, size, self.brush.hardness,
               None if color is None else color.rgb())
        if not self.brush.random and key in self._stamp_cache:
            return self._stamp_cache[key]
        m = self.brush.mask(size)
        h, w = m.shape
        arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        if color is None:
            arr[..., 0] = 255; arr[..., 1] = 255; arr[..., 2] = 255
        else:
            arr[..., 0] = color.red(); arr[..., 1] = color.green(); arr[..., 2] = color.blue()
        arr[..., 3] = m
        img = QImage(arr.tobytes(), w, h, QImage.Format.Format_RGBA8888).copy()
        if not self.brush.random:
            self._stamp_cache[key] = img
        return img

    def _paint_to(self, p0, p1):
        lyr = self.active_layer()
        erase = (self.tool == "eraser")
        size = max(1, int(self.brush_size))
        if not HAVE_NUMPY:
            # eenvoudige terugval: ronde lijn
            painter = QPainter(lyr.image); painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            clip = self.selection_clip()
            if clip is not None:
                painter.setClipRegion(clip)
            if erase:
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                pen = QPen(QColor(0, 0, 0, 255), size)
            else:
                pen = QPen(self.color, size)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen); painter.drawLine(p0, p1); painter.end()
            self.update(); self.changed.emit(); return

        spacing = max(1.0, size * self.brush.spacing / 100.0)
        dx = p1.x() - p0.x(); dy = p1.y() - p0.y()
        dist = math.hypot(dx, dy)
        n = max(1, int(dist / spacing) + 1)
        painter = QPainter(lyr.image)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        clip = self.selection_clip()
        if clip is not None:
            painter.setClipRegion(clip)
        if erase:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        jit = size * self.brush.jitter / 100.0
        for i in range(n + 1):
            t = i / n
            x = p0.x() + dx * t; y = p0.y() + dy * t
            if jit:
                x += random.uniform(-jit, jit); y += random.uniform(-jit, jit)
            stamp = self._stamp_qimage(size, None if erase else self.color)
            painter.drawImage(QPointF(x - size / 2.0, y - size / 2.0), stamp)
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
                q = QPainter(result); q.setClipRegion(clip); q.drawImage(0, 0, newimg); q.end()
                lyr.image = result
            else:
                lyr.image = newimg
        else:
            # simple fallback: fill whole layer (of selectie)
            clip = self.selection_clip()
            if clip is not None:
                q = QPainter(lyr.image); q.setClipRegion(clip); q.fillRect(clip.boundingRect(), self.color); q.end()
            else:
                lyr.image.fill(self.color)
        self.update(); self.changed.emit()

    def _magic_wand(self, ip):
        """Selecteer aangrenzende pixels met (ongeveer) dezelfde kleur op de actieve laag."""
        if not (HAVE_PIL and HAVE_NUMPY):
            return
        lyr = self.active_layer()
        if not (0 <= ip.x() < lyr.image.width() and 0 <= ip.y() < lyr.image.height()):
            return
        rgb = qimage_to_pil(lyr.image).convert("RGB")
        seed = rgb.getpixel((ip.x(), ip.y()))
        fillv = (0, 0, 0) if seed != (0, 0, 0) else (255, 255, 255)
        work = rgb.copy()
        ImageDraw.floodfill(work, (ip.x(), ip.y()), fillv, thresh=float(self.wand_tolerance))
        a = _np.asarray(work).astype(_np.int16); b = _np.asarray(rgb).astype(_np.int16)
        mask = _np.any(a != b, axis=2)
        mask[ip.y(), ip.x()] = True
        region = QRegion()
        for row in range(mask.shape[0]):
            r = mask[row]
            if not r.any():
                continue
            edges = _np.where(_np.diff(_np.concatenate(([0], r.view(_np.int8), [0]))) != 0)[0]
            for k in range(0, len(edges), 2):
                x0 = int(edges[k]); x1 = int(edges[k + 1])
                region += QRegion(x0, row, x1 - x0, 1)
        self.selection = region if not region.isEmpty() else None
        self.update()


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
            "• Nieuw maakt een leeg project. Openen laadt een PNG/JPG of een\n"
            "  eerder opgeslagen .dravestudio-project.\n"
            "• Kies links een gereedschap, een penseel, een kleur en een grootte,\n"
            "  en teken op het canvas. Het linkerpaneel is scrollbaar.\n\n"
            "── TEKEN-GEREEDSCHAP ──\n"
            "• Penseel: tekenen met de huidige kleur, penseelvorm en grootte.\n"
            "• Gum: maakt pixels doorzichtig (volgt dezelfde penseelvorm).\n"
            "• Vullen (emmer): vult een aaneengesloten gebied met de kleur.\n"
            "• Pipet: klik om een kleur uit het beeld over te nemen.\n"
            "• Verplaatsen: sleep de inhoud van de actieve laag.\n"
            "• Vormen: Rechthoek, Ovaal, Lijn. Met 'Vorm vullen' kies je gevuld\n"
            "  of alleen omtrek (de lijndikte volgt de penseelgrootte).\n"
            "• Tekst: klik op het canvas, typ je tekst en kies lettertype/grootte.\n\n"
            "── PENSELEN ──\n"
            "• Keuzelijst 'Penseel' met o.a. Zacht/Hard rond, Krijt, Spray, Marker\n"
            "  en vormen: Vierkant, Driehoek, Zeshoek, Ster, Hart.\n"
            "• 'Nieuw…': maak een eigen penseel (vorm + hardheid, tussenafstand,\n"
            "  spreiding) met een naam; het wordt bewaard.\n"
            "• 'Importeren…': kies een PNG als penseelvorm. Deze komt in de map\n"
            "  'penselen' naast de app en verschijnt voortaan in de lijst.\n\n"
            "── SELECTEREN ──\n"
            "• Selectie (rechthoek), Lasso (vrije vorm) en Toverstaf (klik op een\n"
            "  kleur; stel de tolerantie in met de schuif).\n"
            "• Tekenen, vullen en aanpassingen werken binnen de selectie.\n"
            "• Deselecteren: knop Deselecteren, Ctrl+D, Escape, of rechterklik op\n"
            "  het canvas.\n\n"
            "── AANPASSINGEN & FILTERS (knop bovenin) ──\n"
            "• Helderheid/Contrast, Tint/Verzadiging, Vervagen, Verscherpen, Curven\n"
            "  — met live voorbeeld (Toepassen/Annuleren/Herstel).\n"
            "• Grijswaarden en Kleuren omkeren als directe filters.\n"
            "• Werkt op de actieve laag, of binnen de selectie als die er is.\n\n"
            "── LAGEN (rechts) ──\n"
            "• Nieuwe laag, verwijderen, dupliceren, omhoog/omlaag.\n"
            "• Vinkje = zichtbaar. Dekking en overvloeimodus per laag.\n"
            "• De geselecteerde laag is de 'actieve' laag waarop je tekent.\n\n"
            "── ZOOM & ONGEDAAN MAKEN ──\n"
            "• Zoom met de knoppen onderaan (➖ ➕ / 100% / Passend).\n"
            "• Knoppen Ongedaan (↶) en Opnieuw (↷); ook Ctrl+Z en Ctrl+Y.\n\n"
            "── BEWAREN ──\n"
            "• Opslaan bewaart je project mét lagen (eigen .dravestudio-bestand).\n"
            "• Exporteren maakt een platte PNG of JPG.\n\n"
            "── TAAL ──\n"
            "• De app neemt automatisch je computertaal over; handmatig instelbaar\n"
            "  via Instellingen → Taal (Nederlands/English).\n")
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
        self.bold = QCheckBox(t("Vet")); self.italic = QCheckBox(t("Schuin"))
        srow = QHBoxLayout(); srow.addWidget(self.bold); srow.addWidget(self.italic); srow.addStretch(1)
        g.addLayout(srow, 3, 1)
        self.preview = QLabel("Abc"); self.preview.setStyleSheet(f"color:{color.name()};")
        g.addWidget(self.preview, 4, 1)
        self.text.textChanged.connect(self._upd); self.size.valueChanged.connect(self._upd)
        self.font.currentFontChanged.connect(self._upd)
        self.bold.toggled.connect(self._upd); self.italic.toggled.connect(self._upd)
        row = QHBoxLayout(); row.addStretch(1)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("OK")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        g.addLayout(row, 5, 0, 1, 2)
        self._upd()

    def _upd(self):
        f = self.font.currentFont(); f.setPointSize(min(28, max(10, self.size.value() // 2)))
        f.setBold(self.bold.isChecked()); f.setItalic(self.italic.isChecked())
        self.preview.setFont(f)
        self.preview.setText(self.text.text() or "Abc")

    def result(self):
        return (self.text.text(), self.font.currentFont().family(), self.size.value(),
                self.bold.isChecked(), self.italic.isChecked())


# ----------------------------------------------------------------------------- adjust dialog
class AdjustDialog(QDialog):
    """Aanpassing met schuiven en live voorbeeld op het canvas."""
    def __init__(self, win, title, sliders, transform, parent=None):
        super().__init__(parent)
        self.win = win; self.transform = transform
        self.setWindowTitle(title); self.resize(420, 80 + 60 * len(sliders))
        self.original = win.canvas.active_layer().image.copy()
        self._pil = qimage_to_pil(self.original)
        self.controls = {}
        g = QGridLayout(self); r = 0
        for label, lo, hi, default, key in sliders:
            g.addWidget(QLabel(label), r, 0)
            s = QSlider(Qt.Orientation.Horizontal); s.setRange(lo, hi); s.setValue(default)
            val = QLabel(str(default)); val.setFixedWidth(44)
            s.valueChanged.connect(lambda v, lb=val: lb.setText(str(v)))
            s.valueChanged.connect(self._preview)
            g.addWidget(s, r, 1); g.addWidget(val, r, 2)
            self.controls[key] = s; r += 1
        row = QHBoxLayout(); row.addStretch(1)
        reset = QPushButton(t("Herstel")); reset.clicked.connect(self._reset); row.addWidget(reset)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("Toepassen")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        g.addLayout(row, r, 0, 1, 3)
        self._defaults = {k: s.value() for k, s in self.controls.items()}
        self._preview()

    def _params(self):
        return {k: s.value() for k, s in self.controls.items()}

    def get_params(self):
        return self._params()

    def _compose(self, newfull):
        clip = self.win.canvas.selection_clip()
        if clip is None:
            return newfull
        res = self.original.copy()
        q = QPainter(res); q.setClipRegion(clip); q.drawImage(0, 0, newfull); q.end()
        return res

    def _preview(self):
        try:
            out = self.transform(self._pil, self._params())
            newimg = pil_to_qimage(out)
            self.win.canvas.active_layer().image = self._compose(newimg)
            self.win.canvas.update()
        except Exception:
            pass

    def _reset(self):
        for k, s in self.controls.items():
            s.setValue(self._defaults[k])

    def reject(self):
        self.win.canvas.active_layer().image = self.original
        self.win.canvas.update()
        super().reject()

    def accept(self):
        cv = self.win.canvas
        idx = cv.project.active
        cv.undo_stack.append((idx, self.original)); cv.redo_stack.clear()
        if len(cv.undo_stack) > 25:
            cv.undo_stack.pop(0)
        cv.changed.emit()
        super().accept()


# ----------------------------------------------------------------------------- brush dialog
class BrushDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Nieuw penseel")); self.resize(420, 320)
        g = QGridLayout(self); r = 0
        g.addWidget(QLabel(t("Naam") + ":"), r, 0)
        self.name = QLineEdit(t("Mijn penseel")); g.addWidget(self.name, r, 1, 1, 2); r += 1
        g.addWidget(QLabel(t("Vorm") + ":"), r, 0)
        self.kind = QComboBox()
        self._kinds = [("soft", t("Zacht rond")), ("hard", t("Hard rond")),
                       ("chalk", t("Krijt")), ("spray", t("Spray")), ("marker", t("Marker")),
                       ("square", t("Vierkant")), ("triangle", t("Driehoek")),
                       ("hexagon", t("Zeshoek")), ("star", t("Ster")), ("heart", t("Hart"))]
        for k, lbl in self._kinds:
            self.kind.addItem(lbl)
        g.addWidget(self.kind, r, 1, 1, 2); r += 1
        self.sl = {}
        for key, label, lo, hi, dv in [("hardness", t("Hardheid"), 0, 100, 60),
                                       ("spacing", t("Tussenafstand"), 1, 100, 12),
                                       ("jitter", t("Spreiding"), 0, 100, 0)]:
            g.addWidget(QLabel(label), r, 0)
            s = QSlider(Qt.Orientation.Horizontal); s.setRange(lo, hi); s.setValue(dv)
            val = QLabel(str(dv)); val.setFixedWidth(40)
            s.valueChanged.connect(lambda v, lb=val: lb.setText(str(v)))
            s.valueChanged.connect(self._preview)
            g.addWidget(s, r, 1); g.addWidget(val, r, 2); self.sl[key] = s; r += 1
        self.kind.currentIndexChanged.connect(self._preview)
        self.preview = QLabel(); self.preview.setFixedSize(120, 120)
        self.preview.setStyleSheet("background:#1a1a20; border:1px solid #2a2a31;")
        g.addWidget(self.preview, r, 0, 1, 3, Qt.AlignmentFlag.AlignCenter); r += 1
        row = QHBoxLayout(); row.addStretch(1)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("Opslaan")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        g.addLayout(row, r, 0, 1, 3)
        self._preview()

    def _cur_kind(self):
        return self._kinds[self.kind.currentIndex()][0]

    def _preview(self):
        if not HAVE_NUMPY:
            return
        b = Brush("_", self._cur_kind(), self.sl["hardness"].value(),
                  self.sl["spacing"].value(), self.sl["jitter"].value())
        m = b.mask(100)
        h, w = m.shape
        arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        arr[..., 0] = 230; arr[..., 1] = 230; arr[..., 2] = 230; arr[..., 3] = m
        img = QImage(arr.tobytes(), w, h, QImage.Format.Format_RGBA8888).copy()
        self.preview.setPixmap(QPixmap.fromImage(img).scaled(
            110, 110, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def result(self):
        return (self.name.text(), self.sl["hardness"].value(),
                self.sl["spacing"].value(), self.sl["jitter"].value(), self._cur_kind())


# ----------------------------------------------------------------------------- curves
class CurveEditor(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(256, 256)
        self.points = [[0, 0], [255, 255]]   # (invoer, uitvoer) 0..255
        self._drag = None

    def reset(self):
        self.points = [[0, 0], [255, 255]]; self._drag = None
        self.update(); self.changed.emit()

    def lut(self):
        return lut_from_points(self.points)

    def paintEvent(self, ev):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor("#121217"))
        p.setPen(QPen(QColor("#2a2a31"), 1))
        for i in range(1, 4):
            g = i * 64
            p.drawLine(g, 0, g, 255); p.drawLine(0, g, 255, g)
        p.setPen(QPen(QColor("#3a3a42"), 1)); p.drawLine(0, 255, 255, 0)
        lut = self.lut()
        p.setPen(QPen(QColor("#6fa3d6"), 2))
        prev = None
        for x in range(256):
            cur = QPoint(x, 255 - lut[x])
            if prev is not None:
                p.drawLine(prev, cur)
            prev = cur
        p.setBrush(QColor("#ffffff")); p.setPen(QPen(QColor("#6fa3d6"), 1))
        for x, y in self.points:
            p.drawEllipse(QPoint(x, 255 - y), 4, 4)
        p.setPen(QColor("#2a2a31")); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(0, 0, 255, 255); p.end()

    def _data(self, pos):
        return int(max(0, min(255, pos.x()))), int(max(0, min(255, 255 - pos.y())))

    def mousePressEvent(self, ev):
        x, y = self._data(ev.position())
        # dichtstbijzijnde punt?
        for i, (px, py) in enumerate(self.points):
            if abs(px - x) <= 10 and abs(py - y) <= 10:
                self._drag = i; return
        # nieuw punt invoegen
        self.points.append([x, y]); self.points.sort()
        self._drag = self.points.index([x, y])
        self.update(); self.changed.emit()

    def mouseMoveEvent(self, ev):
        if self._drag is None:
            return
        x, y = self._data(ev.position())
        i = self._drag; last = len(self.points) - 1
        if i == 0:
            x = 0
        elif i == last:
            x = 255
        else:
            x = max(self.points[i - 1][0] + 1, min(self.points[i + 1][0] - 1, x))
        self.points[i] = [x, y]
        self.update(); self.changed.emit()

    def mouseReleaseEvent(self, ev):
        self._drag = None

    def mouseDoubleClickEvent(self, ev):
        x, y = self._data(ev.position())
        for i, (px, py) in enumerate(self.points):
            if 0 < i < len(self.points) - 1 and abs(px - x) <= 10 and abs(py - y) <= 10:
                del self.points[i]; self.update(); self.changed.emit(); return


class CurvesDialog(QDialog):
    def __init__(self, win, parent=None):
        super().__init__(parent)
        self.win = win
        self.setWindowTitle(t("Curven")); self.resize(340, 380)
        self.original = win.canvas.active_layer().image.copy()
        self._pil = qimage_to_pil(self.original)
        v = QVBoxLayout(self)
        v.addWidget(QLabel(t("Sleep op de lijn om punten te maken/verplaatsen "
                             "(dubbelklik = punt weg).")))
        self.editor = CurveEditor(); self.editor.changed.connect(self._preview)
        wrap = QHBoxLayout(); wrap.addStretch(1); wrap.addWidget(self.editor); wrap.addStretch(1)
        v.addLayout(wrap)
        row = QHBoxLayout(); row.addStretch(1)
        reset = QPushButton(t("Herstel")); reset.clicked.connect(self.editor.reset); row.addWidget(reset)
        cancel = QPushButton(t("Annuleren")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
        ok = QPushButton(t("Toepassen")); ok.setObjectName("cta"); ok.clicked.connect(self.accept); row.addWidget(ok)
        v.addLayout(row)
        self._preview()

    def _compose(self, newfull):
        clip = self.win.canvas.selection_clip()
        if clip is None:
            return newfull
        res = self.original.copy()
        q = QPainter(res); q.setClipRegion(clip); q.drawImage(0, 0, newfull); q.end()
        return res

    def _preview(self):
        try:
            lut = self.editor.lut()
            out = _apply_rgb(self._pil, lambda im: im.point(lut * 3))
            self.win.canvas.active_layer().image = self._compose(pil_to_qimage(out))
            self.win.canvas.update()
        except Exception:
            pass

    def reject(self):
        self.win.canvas.active_layer().image = self.original
        self.win.canvas.update(); super().reject()

    def accept(self):
        cv = self.win.canvas; idx = cv.project.active
        cv.undo_stack.append((idx, self.original)); cv.redo_stack.clear()
        if len(cv.undo_stack) > 25:
            cv.undo_stack.pop(0)
        cv.changed.emit(); super().accept()


# ----------------------------------------------------------------------------- acties & presets venster
class AssetsDialog(QDialog):
    def __init__(self, win, parent=None):
        super().__init__(parent)
        self.win = win
        self.setWindowTitle(t("Acties & presets")); self.resize(560, 560)
        v = QVBoxLayout(self)
        tabs = QTabWidget(); v.addWidget(tabs, 1)
        tabs.addTab(self._tab_actions(), t("Acties"))
        tabs.addTab(self._tab_looks(), t("Looks"))
        tabs.addTab(self._tab_palette(), t("Palet"))
        tabs.addTab(self._tab_brushes(), t("Penselen"))
        row = QHBoxLayout()
        exp = QPushButton(t("Exporteren…")); exp.clicked.connect(self._export); row.addWidget(exp)
        imp = QPushButton(t("Importeren…")); imp.clicked.connect(self._import); row.addWidget(imp)
        row.addStretch(1)
        close = QPushButton(t("Sluiten")); close.clicked.connect(self.accept); row.addWidget(close)
        v.addLayout(row)

    # ---- Acties
    def _tab_actions(self):
        w = QWidget(); v = QVBoxLayout(w)
        info = QLabel(t("Neem een reeks aanpassingen op en speel ze met één klik af "
                        "op de actieve laag."))
        info.setWordWrap(True); v.addWidget(info)
        self.rec_btn = QPushButton(); self.rec_btn.clicked.connect(self._toggle_record)
        v.addWidget(self.rec_btn)
        self.rec_lbl = QLabel(""); v.addWidget(self.rec_lbl)
        self.act_list = QListWidget(); v.addWidget(self.act_list, 1)
        row = QHBoxLayout()
        for label, fn in [(t("Afspelen"), self._play_action), (t("Hernoemen"), self._rename_action),
                          (t("Verwijderen"), self._del_action),
                          (t("Opslaan als look"), self._action_to_look)]:
            b = QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        v.addLayout(row)
        self._refresh_actions(); self._update_rec_ui()
        return w

    def _update_rec_ui(self):
        if self.win.recording:
            self.rec_btn.setText(t("■ Opname stoppen"))
            self.rec_lbl.setText(t("Opname loopt — stappen: ") + str(len(self.win.record_steps)))
        else:
            self.rec_btn.setText(t("● Opname starten"))
            self.rec_lbl.setText("")

    def _toggle_record(self):
        if not self.win.recording:
            self.win.recording = True; self.win.record_steps = []
        else:
            self.win.recording = False
            steps = self.win.record_steps; self.win.record_steps = []
            if steps:
                name, ok = QInputDialog.getText(self, t("Actie opslaan"), t("Naam") + ":",
                                                text=t("Mijn actie"))
                if ok and name.strip():
                    self.win.actions.append({"name": name.strip(), "steps": steps})
                    self.win._save_assets(); self._refresh_actions()
            else:
                QMessageBox.information(self, t("Acties"),
                                       t("Geen stappen opgenomen. Pas tijdens de opname een "
                                         "aanpassing of filter toe."))
        self._update_rec_ui()

    def _refresh_actions(self):
        self.act_list.clear()
        for a in self.win.actions:
            self.act_list.addItem("%s  (%d)" % (a.get("name", "?"), len(a.get("steps", []))))

    def _sel_action(self):
        i = self.act_list.currentRow()
        return i if 0 <= i < len(self.win.actions) else -1

    def _play_action(self):
        i = self._sel_action()
        if i >= 0:
            self.win.play_steps(self.win.actions[i].get("steps", []))

    def _rename_action(self):
        i = self._sel_action()
        if i < 0:
            return
        name, ok = QInputDialog.getText(self, t("Hernoemen"), t("Naam") + ":",
                                        text=self.win.actions[i].get("name", ""))
        if ok and name.strip():
            self.win.actions[i]["name"] = name.strip()
            self.win._save_assets(); self._refresh_actions()

    def _del_action(self):
        i = self._sel_action()
        if i >= 0:
            del self.win.actions[i]; self.win._save_assets(); self._refresh_actions()

    def _action_to_look(self):
        i = self._sel_action()
        if i < 0:
            return
        a = self.win.actions[i]
        self.win.presets.append({"name": a.get("name", "look"), "steps": a.get("steps", [])})
        self.win._save_assets(); self._refresh_looks()
        QMessageBox.information(self, t("Looks"), t("Opgeslagen als look."))

    # ---- Looks (presets)
    def _tab_looks(self):
        w = QWidget(); v = QVBoxLayout(w)
        info = QLabel(t("Kant-en-klare looks (en je eigen opgeslagen looks). "
                        "Klik op Toepassen om ze op de actieve laag te zetten."))
        info.setWordWrap(True); v.addWidget(info)
        self.look_list = QListWidget(); v.addWidget(self.look_list, 1)
        row = QHBoxLayout()
        ap = QPushButton(t("Toepassen")); ap.clicked.connect(self._apply_look); row.addWidget(ap)
        dl = QPushButton(t("Verwijderen")); dl.clicked.connect(self._del_look); row.addWidget(dl)
        v.addLayout(row)
        self._refresh_looks()
        return w

    def _all_looks(self):
        items = [("builtin", n, s) for (n, s) in BUILTIN_LOOKS]
        items += [("user", a.get("name", "?"), a.get("steps", [])) for a in self.win.presets]
        return items

    def _refresh_looks(self):
        self.look_list.clear()
        for kind, name, steps in self._all_looks():
            tag = "" if kind == "builtin" else "  ★"
            self.look_list.addItem(("%s%s" % (name, tag)))

    def _apply_look(self):
        i = self.look_list.currentRow()
        items = self._all_looks()
        if 0 <= i < len(items):
            self.win.play_steps(items[i][2])

    def _del_look(self):
        i = self.look_list.currentRow()
        items = self._all_looks()
        if 0 <= i < len(items):
            if items[i][0] != "user":
                QMessageBox.information(self, t("Looks"), t("Ingebouwde looks kun je niet verwijderen."))
                return
            ui = i - len(BUILTIN_LOOKS)
            if 0 <= ui < len(self.win.presets):
                del self.win.presets[ui]; self.win._save_assets(); self._refresh_looks()

    # ---- Palet
    def _tab_palette(self):
        w = QWidget(); v = QVBoxLayout(w)
        info = QLabel(t("Bewaar je favoriete kleuren. Klik op Gebruiken om een kleur "
                        "in te stellen."))
        info.setWordWrap(True); v.addWidget(info)
        self.pal_list = QListWidget(); self.pal_list.setIconSize(QSize(28, 18))
        self.pal_list.itemDoubleClicked.connect(lambda *_: self._use_color())
        v.addWidget(self.pal_list, 1)
        row = QHBoxLayout()
        add = QPushButton(t("Huidige kleur toevoegen")); add.clicked.connect(self._add_color); row.addWidget(add)
        use = QPushButton(t("Gebruiken")); use.clicked.connect(self._use_color); row.addWidget(use)
        dl = QPushButton(t("Verwijderen")); dl.clicked.connect(self._del_color); row.addWidget(dl)
        v.addLayout(row)
        self._refresh_palette()
        return w

    def _refresh_palette(self):
        self.pal_list.clear()
        for c in self.win.palette:
            pm = QPixmap(28, 18); pm.fill(QColor(c))
            self.pal_list.addItem(QListWidgetItem(QIcon(pm), c))

    def _add_color(self):
        self.win.add_palette_color(self.win.canvas.color.name())
        self._refresh_palette()

    def _use_color(self):
        i = self.pal_list.currentRow()
        if 0 <= i < len(self.win.palette):
            self.win.canvas.color = QColor(self.win.palette[i]); self.win._refresh_color()

    def _del_color(self):
        i = self.pal_list.currentRow()
        if 0 <= i < len(self.win.palette):
            del self.win.palette[i]; self.win._save_assets(); self._refresh_palette()

    # ---- Penselen
    def _tab_brushes(self):
        w = QWidget(); v = QVBoxLayout(w)
        info = QLabel(t("Je eigen en geïmporteerde penselen. Importeer een PNG als "
                        "penseelvorm."))
        info.setWordWrap(True); v.addWidget(info)
        self.brush_list = QListWidget(); v.addWidget(self.brush_list, 1)
        row = QHBoxLayout()
        imp = QPushButton(t("Importeren…")); imp.clicked.connect(self._imp_brush); row.addWidget(imp)
        dl = QPushButton(t("Verwijderen")); dl.clicked.connect(self._del_brush); row.addWidget(dl)
        v.addLayout(row)
        self._refresh_brushlist()
        return w

    def _user_brushes(self):
        return [b for b in self.win.brushes if not b.builtin]

    def _refresh_brushlist(self):
        self.brush_list.clear()
        for b in self._user_brushes():
            self.brush_list.addItem("%s  (%s)" % (b.name, b.kind))

    def _imp_brush(self):
        self.win._import_brush(); self._refresh_brushlist()

    def _del_brush(self):
        ub = self._user_brushes()
        i = self.brush_list.currentRow()
        if not (0 <= i < len(ub)):
            return
        b = ub[i]
        if b.kind == "image":
            try:
                os.remove(os.path.join(self.win.brushes_dir, b.name + ".png"))
            except Exception:
                pass
        self.win.brushes.remove(b)
        self.win._save_custom_brushes(); self.win._reload_brush_combo(); self._refresh_brushlist()

    # ---- import/export
    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, t("Exporteren…"),
                                              os.path.join(APP_DIR, "mijn-presets.dravepreset"),
                                              "DraveStudio presets (*.dravepreset)")
        if not path:
            return
        try:
            self.win.export_assets(path)
            QMessageBox.information(self, t("Exporteren…"), t("Opgeslagen."))
        except Exception as e:
            QMessageBox.warning(self, t("Exporteren…"), str(e))

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(self, t("Importeren…"), APP_DIR,
                                              "DraveStudio presets (*.dravepreset);;JSON (*.json)")
        if not path:
            return
        try:
            self.win.import_assets(path)
            self._refresh_actions(); self._refresh_looks()
            self._refresh_palette(); self._refresh_brushlist()
            QMessageBox.information(self, t("Importeren…"), t("Geïmporteerd."))
        except Exception as e:
            QMessageBox.warning(self, t("Importeren…"), str(e))


# ----------------------------------------------------------------------------- main window
class DraveStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = Project.new(1000, 700, white_bg=True)
        self.cur_path = None
        self.brushes_dir = os.path.join(APP_DIR, "penselen")
        try:
            os.makedirs(self.brushes_dir, exist_ok=True)
        except Exception:
            pass
        self.brushes = self._load_brushes()
        cfg = load_config()
        self.actions = cfg.get("actions", [])
        self.presets = cfg.get("presets", [])      # door gebruiker bewaarde looks
        self.palette = cfg.get("palette", [])
        self.recording = False
        self.record_steps = []
        self.setWindowTitle(f"{APP_NAME} - {t('Een lichte fotobewerker met lagen.')}")
        self.resize(1320, 860)

        central = QWidget(); self.setCentralWidget(central)
        outer = QVBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        outer.addWidget(self._header())

        self.mode = "raster"
        self.scene = VectorScene(self.project.width, self.project.height)
        self.vcanvas = VectorCanvas(self.scene)

        self.tools_stack = QStackedWidget()
        self.tools_stack.addWidget(self._tools_panel())
        self.tools_stack.addWidget(self._vector_tools_panel())
        self.center_stack = QStackedWidget()
        self.center_stack.addWidget(self._center())
        self.center_stack.addWidget(self._vector_center())

        body = QHBoxLayout(); body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0)
        body.addWidget(self.tools_stack)
        body.addWidget(self.center_stack, 1)
        body.addWidget(self._layers_panel())
        bw = QWidget(); bw.setLayout(body); outer.addWidget(bw, 1)

        self._refresh_layers()
        self._refresh_color()
        self.canvas.set_brush(self.brushes[0])
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

    # ------------------------------------------------ modus (raster / vector)
    def _toggle_mode(self):
        self.set_mode("vector" if self.mode == "raster" else "raster")

    def set_mode(self, mode):
        self.mode = mode
        if mode == "vector":
            self.center_stack.setCurrentIndex(1); self.tools_stack.setCurrentIndex(1)
            self.mode_btn.setText(t("🖼 Rastermodus"))
            self.statusBar().showMessage(t("Vectormodus (SVG)"))
        else:
            self.center_stack.setCurrentIndex(0); self.tools_stack.setCurrentIndex(0)
            self.mode_btn.setText(t("✏️ Vectormodus"))
            self.statusBar().showMessage(APP_NAME)

    def _vector_center(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        self.vcanvas.cursorMoved.connect(self._on_cursor)
        self.vcanvas.text_handler = self.place_vtext
        self.vscroll = QScrollArea(); self.vscroll.setWidgetResizable(False)
        self.vscroll.setAlignment(Qt.AlignmentFlag.AlignCenter); self.vscroll.setWidget(self.vcanvas)
        lay.addWidget(self.vscroll, 1)
        bar = QWidget(); bar.setFixedHeight(44); blay = QHBoxLayout(bar)
        blay.setContentsMargins(10, 6, 10, 6)
        undo = QToolButton(); undo.setText("↶ " + t("Ongedaan")); undo.clicked.connect(self.vcanvas.undo)
        redo = QToolButton(); redo.setText("↷ " + t("Opnieuw")); redo.clicked.connect(self.vcanvas.redo)
        blay.addWidget(undo); blay.addWidget(redo)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); blay.addWidget(sep)
        zo = QToolButton(); zo.setText("➖"); zo.clicked.connect(lambda: self.vcanvas.set_zoom(self.vcanvas.zoom * 0.8))
        zi = QToolButton(); zi.setText("➕"); zi.clicked.connect(lambda: self.vcanvas.set_zoom(self.vcanvas.zoom * 1.25))
        z1 = QPushButton("100%"); z1.clicked.connect(lambda: self.vcanvas.set_zoom(1.0))
        blay.addWidget(zo); blay.addWidget(zi); blay.addWidget(z1)
        blay.addStretch(1)
        lay.addWidget(bar)
        return w

    def _vector_tools_panel(self):
        inner = QWidget(); inner.setObjectName("panel")
        lay = QVBoxLayout(inner); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(6)
        lay.addWidget(section(t("Vector")))
        self.vtool_group = QButtonGroup(self); self.vtool_group.setExclusive(True)
        vtools = [("select", "⬚  " + t("Selecteren")), ("rect", "▭  " + t("Rechthoek")),
                  ("ellipse", "⬭  " + t("Ovaal")), ("line", "╱  " + t("Lijn")),
                  ("pen", "✎  " + t("Pen (pad)")), ("text", "🅣  " + t("Tekst"))]
        for key, label in vtools:
            b = QToolButton(); b.setText(label); b.setCheckable(True)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setStyleSheet("text-align:left; padding:8px;")
            b.clicked.connect(lambda _c=False, k=key: setattr(self.vcanvas, "tool", k))
            self.vtool_group.addButton(b); lay.addWidget(b)
            if key == "select":
                b.setChecked(True)
        crow = QHBoxLayout()
        pclose = QPushButton(t("Pad sluiten")); pclose.clicked.connect(lambda: self.vcanvas.finish_pen(True))
        popen = QPushButton(t("Pad afronden")); popen.clicked.connect(lambda: self.vcanvas.finish_pen(False))
        crow.addWidget(pclose); crow.addWidget(popen); lay.addLayout(crow)

        lay.addSpacing(8); lay.addWidget(section(t("Stijl")))
        self.vfill_chk = QCheckBox(t("Vulling")); self.vfill_chk.setChecked(True)
        self.vfill_chk.toggled.connect(lambda v: setattr(self.vcanvas, "use_fill", v))
        lay.addWidget(self.vfill_chk)
        self.vfill_btn = QPushButton(t("Vulkleur")); self.vfill_btn.clicked.connect(self._pick_vfill)
        lay.addWidget(self.vfill_btn)
        self.vstroke_chk = QCheckBox(t("Lijn")); self.vstroke_chk.setChecked(True)
        self.vstroke_chk.toggled.connect(lambda v: setattr(self.vcanvas, "use_stroke", v))
        lay.addWidget(self.vstroke_chk)
        self.vstroke_btn = QPushButton(t("Lijnkleur")); self.vstroke_btn.clicked.connect(self._pick_vstroke)
        lay.addWidget(self.vstroke_btn)
        lay.addWidget(QLabel(t("Lijndikte")))
        self.vsw = QSlider(Qt.Orientation.Horizontal); self.vsw.setRange(1, 40); self.vsw.setValue(2)
        self.vsw.valueChanged.connect(lambda v: setattr(self.vcanvas, "stroke_w", v))
        lay.addWidget(self.vsw)
        applyb = QPushButton(t("Stijl op selectie toepassen"))
        applyb.clicked.connect(lambda: self.vcanvas.apply_style_to_selected()); lay.addWidget(applyb)

        lay.addSpacing(8); lay.addWidget(section(t("Object")))
        orow = QHBoxLayout()
        fb = QPushButton(t("Naar voren")); fb.clicked.connect(lambda: self.vcanvas.raise_selected(True))
        bb = QPushButton(t("Naar achteren")); bb.clicked.connect(lambda: self.vcanvas.raise_selected(False))
        orow.addWidget(fb); orow.addWidget(bb); lay.addLayout(orow)
        delb = QPushButton(t("Verwijderen")); delb.clicked.connect(lambda: self.vcanvas.delete_selected())
        lay.addWidget(delb)
        hint = QLabel(t("Tip: rechterklik = niets selecteren. Dubbelklik met de Pen "
                        "rondt een pad af."))
        hint.setWordWrap(True); hint.setStyleSheet("color:#8b909a;"); lay.addWidget(hint)
        lay.addStretch(1)
        self._refresh_vstyle_btns()
        scroll = QScrollArea(); scroll.setObjectName("toolscroll")
        scroll.setWidget(inner); scroll.setWidgetResizable(True); scroll.setFixedWidth(232)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    def _refresh_vstyle_btns(self):
        self.vfill_btn.setStyleSheet(
            "background:%s; color:%s; border:1px solid #2a2a31;" % (
                self.vcanvas.fill.name(),
                "#000" if self.vcanvas.fill.lightness() > 128 else "#fff"))
        self.vstroke_btn.setStyleSheet(
            "background:%s; color:%s; border:1px solid #2a2a31;" % (
                self.vcanvas.stroke.name(),
                "#000" if self.vcanvas.stroke.lightness() > 128 else "#fff"))

    def _pick_vfill(self):
        c = QColorDialog.getColor(self.vcanvas.fill, self, t("Vulkleur"))
        if c.isValid():
            self.vcanvas.fill = c; self._refresh_vstyle_btns()

    def _pick_vstroke(self):
        c = QColorDialog.getColor(self.vcanvas.stroke, self, t("Lijnkleur"))
        if c.isValid():
            self.vcanvas.stroke = c; self._refresh_vstyle_btns()

    def place_vtext(self, sp, idx=None):
        if idx is not None and 0 <= idx < len(self.vcanvas.scene.shapes):
            sh = self.vcanvas.scene.shapes[idx]
            dlg = TextDialog(sh.fill or self.vcanvas.fill, self)
            dlg.text.setText(sh.text); dlg.size.setValue(int(sh.size))
            dlg.font.setCurrentFont(QFont(sh.family))
            dlg.bold.setChecked(bool(sh.bold)); dlg.italic.setChecked(bool(sh.italic)); dlg._upd()
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            text, family, size, bold, italic = dlg.result()
            if not text.strip():
                return
            self.vcanvas.push_undo()
            sh.text = text; sh.family = family; sh.size = size; sh.bold = bold; sh.italic = italic
            self.vcanvas.update(); self.vcanvas.changed.emit()
            return
        dlg = TextDialog(self.vcanvas.fill, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        text, family, size, bold, italic = dlg.result()
        self.vcanvas.add_text(sp, text, family, size, bold, italic)

    # -- aanpassingen & filters
    def _adjust_menu(self):
        from PyQt6.QtWidgets import QMenu
        if not HAVE_PIL:
            QMessageBox.information(self, t("Aanpassingen"), "Pillow ontbreekt."); return
        m = QMenu(self)
        m.addAction(t("Helderheid / Contrast"), self._adj_bright_contrast)
        m.addAction(t("Tint / Verzadiging"), self._adj_hue_sat)
        m.addAction(t("Vervagen"), self._adj_blur)
        m.addAction(t("Verscherpen"), self._adj_sharpen)
        m.addAction(t("Curven"), self._adj_curves)
        m.addSeparator()
        m.addAction(t("Grijswaarden"), lambda: self.apply_adjustment("grayscale", {}))
        m.addAction(t("Kleuren omkeren"), lambda: self.apply_adjustment("invert", {}))
        m.exec(self._adj_btn.mapToGlobal(self._adj_btn.rect().bottomLeft()))

    # -- afbeelding: bijsnijden, draaien, spiegelen (alle lagen tegelijk)
    def _image_menu(self):
        from PyQt6.QtWidgets import QMenu
        m = QMenu(self)
        m.addAction(t("Bijsnijden naar selectie"), self.crop_to_selection)
        m.addSeparator()
        m.addAction(t("90° rechtsom draaien"), lambda: self.rotate_image(90))
        m.addAction(t("90° linksom draaien"), lambda: self.rotate_image(-90))
        m.addAction(t("180° draaien"), lambda: self.rotate_image(180))
        m.addSeparator()
        m.addAction(t("Horizontaal spiegelen"), lambda: self.flip_image(True))
        m.addAction(t("Verticaal spiegelen"), lambda: self.flip_image(False))
        m.exec(self._img_btn.mapToGlobal(self._img_btn.rect().bottomLeft()))

    def _image_op(self, fn, new_w, new_h):
        """Voert fn(QImage)->QImage uit op elke laag, met één undo-stap."""
        if self.mode != "raster":
            QMessageBox.information(self, t("Afbeelding"), t("Dit werkt in de rastermodus.")); return
        cv = self.canvas
        cv.undo_stack.append(cv._project_state()); cv.redo_stack.clear()
        if len(cv.undo_stack) > 25:
            cv.undo_stack.pop(0)
        for l in self.project.layers:
            l.image = fn(l.image).convertToFormat(QImage.Format.Format_ARGB32)
        self.project.width, self.project.height = new_w, new_h
        cv.clear_selection(); cv._update_size(); cv.changed.emit()
        self._refresh_layers()

    def crop_to_selection(self):
        clip = self.canvas.selection_clip()
        if clip is None:
            QMessageBox.information(self, t("Afbeelding"),
                                    t("Maak eerst een selectie (rechthoek, lasso of toverstaf).")); return
        r = clip.boundingRect().intersected(QRect(0, 0, self.project.width, self.project.height))
        if r.width() < 1 or r.height() < 1:
            return
        self._image_op(lambda im: im.copy(r), r.width(), r.height())

    def rotate_image(self, deg):
        from PyQt6.QtGui import QTransform
        w, h = self.project.width, self.project.height
        nw, nh = (h, w) if deg in (90, -90) else (w, h)
        self._image_op(lambda im: im.transformed(QTransform().rotate(deg)), nw, nh)

    def flip_image(self, horizontal):
        w, h = self.project.width, self.project.height
        def fn(im):
            try:   # PyQt6 >= 6.9
                return im.flipped(Qt.Orientation.Horizontal if horizontal else Qt.Orientation.Vertical)
            except AttributeError:
                return im.mirrored(horizontal, not horizontal)
        self._image_op(fn, w, h)

    # -- centrale aanpassing (gebruikt door menu, acties en looks)
    def apply_adjustment(self, op, params, record=True):
        if not HAVE_PIL or op not in ADJUST_FUNCS:
            return
        cv = self.canvas
        original = cv.active_layer().image.copy()
        try:
            out = pil_to_qimage(ADJUST_FUNCS[op](qimage_to_pil(original), params or {}))
        except Exception as e:
            QMessageBox.warning(self, t("Aanpassingen"), str(e)); return
        clip = cv.selection_clip()
        if clip is not None:
            res = original.copy()
            q = QPainter(res); q.setClipRegion(clip); q.drawImage(0, 0, out); q.end()
            out = res
        cv.undo_stack.append((cv.project.active, original)); cv.redo_stack.clear()
        if len(cv.undo_stack) > 25:
            cv.undo_stack.pop(0)
        cv.active_layer().image = out; cv.update(); cv.changed.emit()
        if record and self.recording:
            self.record_steps.append({"op": op, "params": params or {}})

    def play_steps(self, steps):
        for st in steps:
            self.apply_adjustment(st.get("op"), st.get("params", {}), record=False)

    def _record_step(self, op, params):
        if self.recording:
            self.record_steps.append({"op": op, "params": params})

    def _adj_bright_contrast(self):
        dlg = AdjustDialog(self, t("Helderheid / Contrast"),
                           [(t("Helderheid"), 0, 200, 100, "bright"),
                            (t("Contrast"), 0, 200, 100, "contrast")],
                           adj_brightness_contrast, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._record_step("bright_contrast", dlg.get_params())

    def _adj_hue_sat(self):
        dlg = AdjustDialog(self, t("Tint / Verzadiging"),
                           [(t("Tint"), -180, 180, 0, "hue"),
                            (t("Verzadiging"), 0, 200, 100, "sat")],
                           adj_hue_sat, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._record_step("hue_sat", dlg.get_params())

    def _adj_blur(self):
        dlg = AdjustDialog(self, t("Vervagen"),
                           [(t("Straal"), 0, 100, 0, "radius")], adj_blur, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._record_step("blur", dlg.get_params())

    def _adj_sharpen(self):
        dlg = AdjustDialog(self, t("Verscherpen"),
                           [(t("Sterkte"), 0, 300, 0, "amount")], adj_sharpen, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._record_step("sharpen", dlg.get_params())

    def _adj_curves(self):
        if not HAVE_PIL:
            QMessageBox.information(self, t("Curven"), "Pillow ontbreekt."); return
        dlg = CurvesDialog(self, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._record_step("curves", {"points": [list(p) for p in dlg.editor.points]})

    def _apply_filter(self, fn):
        """Directe filters (grijswaarden, omkeren) mét undo + selectie-respect."""
        cv = self.canvas
        original = cv.active_layer().image.copy()
        try:
            out = pil_to_qimage(fn(qimage_to_pil(original)))
        except Exception as e:
            QMessageBox.warning(self, t("Aanpassingen"), str(e)); return
        clip = cv.selection_clip()
        if clip is not None:
            res = original.copy()
            q = QPainter(res); q.setClipRegion(clip); q.drawImage(0, 0, out); q.end()
            out = res
        cv.undo_stack.append((cv.project.active, original)); cv.redo_stack.clear()
        if len(cv.undo_stack) > 25:
            cv.undo_stack.pop(0)
        cv.active_layer().image = out; cv.update(); cv.changed.emit()

    def place_text(self, ip):
        dlg = TextDialog(self.canvas.color, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        text, family, size, bold, italic = dlg.result()
        if not text.strip():
            return
        self.canvas.push_undo()
        lyr = self.canvas.active_layer()
        p = QPainter(lyr.image); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        clip = self.canvas.selection_clip()
        if clip is not None:
            p.setClipRegion(clip)
        f = QFont(family); f.setPixelSize(size); f.setBold(bold); f.setItalic(italic)
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
        adj = QPushButton(t("Aanpassingen")); adj.clicked.connect(self._adjust_menu)
        lay.addWidget(adj); self._adj_btn = adj
        afb = QPushButton(t("Afbeelding")); afb.clicked.connect(self._image_menu)
        lay.addWidget(afb); self._img_btn = afb
        ap = QPushButton(t("🎬 Acties")); ap.clicked.connect(self.show_assets)
        lay.addWidget(ap)
        self.mode_btn = QPushButton(t("✏️ Vectormodus")); self.mode_btn.setObjectName("mode")
        self.mode_btn.clicked.connect(self._toggle_mode); lay.addWidget(self.mode_btn)
        lay.addStretch(1)
        for label, fn in [(t("📖 Snelgids"), self.show_guide), (t("✉️ Contact"), self.show_contact),
                          (t("🔄 Updates"), lambda: self.check_updates(silent=False)),
                          (t("ℹ️ Info"), self.show_info), (t("Instellingen…"), self.show_settings)]:
            b = QPushButton(label); b.clicked.connect(fn); lay.addWidget(b)
        return h

    # -- tools
    def _tools_panel(self):
        inner = QWidget(); inner.setObjectName("panel")
        lay = QVBoxLayout(inner); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(6)
        lay.addWidget(section(t("Gereedschap")))
        self.tool_group = QButtonGroup(self); self.tool_group.setExclusive(True)
        tools = [("brush", "🖌  " + t("Penseel")), ("eraser", "🩹  " + t("Gum")),
                 ("fill", "🪣  " + t("Vullen")), ("pick", "💧  " + t("Pipet")),
                 ("move", "✥  " + t("Verplaatsen")), ("select", "⬚  " + t("Selectie")),
                 ("lasso", "✎  " + t("Lasso")), ("wand", "🪄  " + t("Toverstaf")),
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
        lay.addWidget(QLabel(t("Toverstaf-tolerantie")))
        self.tol_slider = QSlider(Qt.Orientation.Horizontal); self.tol_slider.setRange(0, 150)
        self.tol_slider.setValue(32)
        self.tol_slider.valueChanged.connect(lambda v: setattr(self.canvas, "wand_tolerance", v))
        lay.addWidget(self.tol_slider)

        lay.addSpacing(8)
        lay.addWidget(section(t("Kleur")))
        self.color_btn = QPushButton(); self.color_btn.setFixedHeight(38)
        self.color_btn.clicked.connect(self.pick_color); lay.addWidget(self.color_btn)

        lay.addSpacing(8)
        lay.addWidget(section(t("Penseel")))
        self.brush_combo = QComboBox()
        self.brush_combo.currentIndexChanged.connect(self._on_brush_changed)
        lay.addWidget(self.brush_combo)
        brow = QHBoxLayout()
        nb = QPushButton(t("Nieuw…")); nb.clicked.connect(self._new_brush); brow.addWidget(nb)
        ib = QPushButton(t("Importeren…")); ib.clicked.connect(self._import_brush); brow.addWidget(ib)
        lay.addLayout(brow)
        self._reload_brush_combo()

        lay.addSpacing(8)
        lay.addWidget(section(t("Grootte")))
        self.size_slider = QSlider(Qt.Orientation.Horizontal); self.size_slider.setRange(1, 300)
        self.size_slider.setValue(12); self.size_slider.valueChanged.connect(self._set_size)
        lay.addWidget(self.size_slider)
        self.size_lbl = QLabel("12 px"); lay.addWidget(self.size_lbl)

        lay.addStretch(1)
        scroll = QScrollArea(); scroll.setObjectName("toolscroll")
        scroll.setWidget(inner); scroll.setWidgetResizable(True)
        scroll.setFixedWidth(232)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    # -- center (canvas + zoom)
    def _center(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        self.canvas = Canvas(self.project)
        self.canvas.cursorMoved.connect(self._on_cursor)
        self.canvas.changed.connect(self._on_canvas_changed)
        self.canvas.zoomChanged.connect(
            lambda: self.zoom_lbl.setText(f"{int(self.canvas.zoom * 100)}%"))
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

    # ------------------------------------------------ penselen
    def _load_brushes(self):
        brushes = [Brush(n, k, h, s, j) for (n, k, h, s, j) in BUILTIN_BRUSHES]
        cfg = load_config()
        for d in cfg.get("brushes", []):
            try:
                brushes.append(Brush(d["name"], d.get("kind", "soft"),
                                     d.get("hardness", 80), d.get("spacing", 12),
                                     d.get("jitter", 0), builtin=False))
            except Exception:
                pass
        if HAVE_PIL:
            try:
                for fn in sorted(os.listdir(self.brushes_dir)):
                    if fn.lower().endswith(".png"):
                        try:
                            m = Image.open(os.path.join(self.brushes_dir, fn)).convert("L")
                            brushes.append(Brush(os.path.splitext(fn)[0], "image",
                                                 custom_mask=m, builtin=False))
                        except Exception:
                            pass
            except Exception:
                pass
        return brushes

    def _reload_brush_combo(self):
        self.brush_combo.blockSignals(True)
        self.brush_combo.clear()
        for b in self.brushes:
            self.brush_combo.addItem(b.name)
        self.brush_combo.blockSignals(False)

    def _on_brush_changed(self, idx):
        if 0 <= idx < len(self.brushes):
            self.canvas.set_brush(self.brushes[idx])
            # naar penseel schakelen voor direct gebruik
            if self.canvas.tool not in ("brush", "eraser"):
                self.set_tool("brush"); self._toolbtn_brush.setChecked(True)

    def _save_custom_brushes(self):
        cfg = load_config()
        cfg["brushes"] = [b.to_dict() for b in self.brushes
                          if not b.builtin and b.kind != "image"]
        save_config(cfg)

    def _new_brush(self):
        dlg = BrushDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name, hardness, spacing, jitter, kind = dlg.result()
        if not name.strip():
            return
        self.brushes.append(Brush(name.strip(), kind, hardness, spacing, jitter, builtin=False))
        self._save_custom_brushes()
        self._reload_brush_combo()
        self.brush_combo.setCurrentIndex(len(self.brushes) - 1)

    def _import_brush(self):
        if not HAVE_PIL:
            QMessageBox.information(self, t("Penseel"), "Pillow ontbreekt."); return
        path, _ = QFileDialog.getOpenFileName(self, t("Penseel importeren…"), APP_DIR,
                                              "PNG (*.png);;Afbeelding (*.png *.jpg *.jpeg)")
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
            # gebruik alpha als masker; geen alpha -> gebruik (omgekeerde) helderheid
            if img.getextrema()[3][0] == 255:
                mask = img.convert("L").point(lambda v: 255 - v)   # donker = vol penseel
            else:
                mask = img.split()[3]
            name = os.path.splitext(os.path.basename(path))[0]
            dest = os.path.join(self.brushes_dir, name + ".png")
            mask.save(dest)
            self.brushes.append(Brush(name, "image", custom_mask=mask, builtin=False))
            self._reload_brush_combo()
            self.brush_combo.setCurrentIndex(len(self.brushes) - 1)
            QMessageBox.information(self, t("Penseel"),
                                   t("Penseel geïmporteerd en bewaard in de map 'penselen'."))
        except Exception as e:
            QMessageBox.warning(self, t("Penseel"), str(e))

    # ------------------------------------------------ acties / presets / palet  (opslag + import/export)
    def _save_assets(self):
        cfg = load_config()
        cfg["actions"] = self.actions
        cfg["presets"] = self.presets
        cfg["palette"] = self.palette
        save_config(cfg)

    def add_palette_color(self, hexcol):
        if hexcol and hexcol not in self.palette:
            self.palette.append(hexcol); self._save_assets()

    def _brush_export(self, b):
        if b.kind == "image" and b.custom_mask is not None:
            import io
            buf = io.BytesIO(); b.custom_mask.save(buf, "PNG")
            return {"name": b.name, "kind": "image",
                    "png": base64.b64encode(buf.getvalue()).decode("ascii")}
        return b.to_dict()

    def export_assets(self, path):
        data = {"dravestudio_assets": 1,
                "actions": self.actions, "presets": self.presets, "palette": self.palette,
                "brushes": [self._brush_export(b) for b in self.brushes if not b.builtin]}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def import_assets(self, path):
        import io
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        names = {a.get("name") for a in self.actions}
        for a in data.get("actions", []):
            nm = a.get("name", "actie")
            while nm in names:
                nm += " (2)"
            self.actions.append({"name": nm, "steps": a.get("steps", [])}); names.add(nm)
        pnames = {a.get("name") for a in self.presets}
        for a in data.get("presets", []):
            nm = a.get("name", "look")
            while nm in pnames:
                nm += " (2)"
            self.presets.append({"name": nm, "steps": a.get("steps", [])}); pnames.add(nm)
        for c in data.get("palette", []):
            if c not in self.palette:
                self.palette.append(c)
        for bd in data.get("brushes", []):
            try:
                if bd.get("kind") == "image" and "png" in bd and HAVE_PIL:
                    raw = base64.b64decode(bd["png"])
                    m = Image.open(io.BytesIO(raw)).convert("L")
                    m.save(os.path.join(self.brushes_dir, bd["name"] + ".png"))
                    self.brushes.append(Brush(bd["name"], "image", custom_mask=m, builtin=False))
                else:
                    self.brushes.append(Brush(bd["name"], bd.get("kind", "soft"),
                                              bd.get("hardness", 80), bd.get("spacing", 12),
                                              bd.get("jitter", 0), builtin=False))
            except Exception:
                pass
        self._save_assets(); self._save_custom_brushes(); self._reload_brush_combo()

    def show_assets(self):
        AssetsDialog(self, self).exec()

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
            "Afbeeldingen (*.png *.jpg *.jpeg *.bmp);;SVG (*.svg);;Project (*%s);;Alle (*)" % PROJECT_EXT)
        if not path:
            return
        if path.lower().endswith(".svg"):
            self._load_svg(path); return
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

    def _load_svg(self, path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self.scene = VectorScene.from_svg(fh.read())
        except Exception as e:
            QMessageBox.warning(self, t("Openen…"), str(e)); return
        self.vcanvas.scene = self.scene; self.vcanvas.sel = -1
        self.vcanvas.undo_stack.clear(); self.vcanvas.redo_stack.clear()
        self.vcanvas._update_size()
        self.set_mode("vector")
        self.statusBar().showMessage("Geopend (SVG): " + os.path.basename(path))

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
        if self.mode == "vector":
            path, _ = QFileDialog.getSaveFileName(self, t("Opslaan als…"),
                os.path.join(APP_DIR, "tekening.svg"), "SVG (*.svg)")
            if not path:
                return
            if not path.lower().endswith(".svg"):
                path += ".svg"
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self.scene.to_svg())
                self.statusBar().showMessage(t("Opgeslagen."))
            except Exception as e:
                QMessageBox.warning(self, t("Opslaan"), str(e))
            return
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
        filters = ("PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;WEBP (*.webp);;"
                   "TIFF (*.tif *.tiff);;GIF (*.gif);;ICO (*.ico)")
        path, sel = QFileDialog.getSaveFileName(
            self, t("Exporteren…"), os.path.join(APP_DIR, "export.png"), filters)
        if not path:
            return
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if not ext:   # geen extensie getypt -> uit het gekozen filter afleiden
            for e, tag in [("png", "PNG"), ("jpg", "JPEG"), ("bmp", "BMP"), ("webp", "WEBP"),
                           ("tif", "TIFF"), ("gif", "GIF"), ("ico", "ICO")]:
                if sel.startswith(tag):
                    ext = e; path += "." + e; break
            else:
                ext = "png"; path += ".png"
        fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "bmp": "BMP", "webp": "WEBP",
                   "tif": "TIFF", "tiff": "TIFF", "gif": "GIF", "ico": "ICO"}
        fmt = fmt_map.get(ext, "PNG")
        comp = self.scene.to_qimage(1.0) if self.mode == "vector" else self.project.composite()
        ok = False
        try:
            if HAVE_PIL:
                pil = qimage_to_pil(comp)                    # RGBA
                if fmt in ("JPEG", "BMP", "ICO"):            # geen transparantie -> witte ondergrond
                    bg = Image.new("RGB", pil.size, (255, 255, 255))
                    bg.paste(pil, mask=pil.split()[3]); pil = bg
                kw = {}
                if fmt == "JPEG":
                    kw = {"quality": 92}
                elif fmt == "GIF":
                    pil = pil.convert("P", palette=Image.ADAPTIVE)
                elif fmt == "ICO":
                    mx = min(pil.size)
                    sizes = [(s, s) for s in (256, 128, 64, 48, 32, 16) if s <= mx] or [pil.size]
                    kw = {"sizes": sizes}
                pil.save(path, fmt, **kw); ok = True
            else:
                if fmt in ("JPEG", "BMP", "ICO"):
                    flat = QImage(comp.size(), QImage.Format.Format_RGB32); flat.fill(Qt.GlobalColor.white)
                    p = QPainter(flat); p.drawImage(0, 0, comp); p.end()
                    ok = flat.save(path, fmt)
                else:
                    ok = comp.save(path, fmt)
        except Exception as e:
            QMessageBox.warning(self, t("Exporteren…"), str(e)); return
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
