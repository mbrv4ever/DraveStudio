# Test bijsnijden/draaien/spiegelen (Claudio, 19 okt 2026) - verandert niets aan je bestanden
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.argv = [sys.argv[0]]
import dravestudio as ds
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QRegion, QColor
from PyQt6.QtCore import QRect
QMessageBox.information = staticmethod(lambda *a, **k: print("  (melding)", a[2] if len(a) > 2 else ""))
app = QApplication.instance() or QApplication(sys.argv)
w = ds.DraveStudio()
w.project = w.canvas.project
p = w.project
p.layers.append(ds.Layer(p.width, p.height, name="Rood"))
p.layers[1].image.setPixelColor(10, 20, QColor("red"))
print("start", p.width, p.height, "lagen", len(p.layers))
w.rotate_image(90); print("90 rechts", p.width, p.height, p.layers[1].image.width(), p.layers[1].image.height(), "rood op", (p.height and [ (x,y) for x in range(p.width) for y in (20,10,p.height-11,p.height-21) if p.layers[1].image.pixelColor(x,y).red()==255][:1]))
w.canvas.undo(); print("ongedaan", p.width, p.height, "rood terug:", p.layers[1].image.pixelColor(10, 20).red() == 255)
w.canvas.redo(); print("opnieuw", p.width, p.height); w.canvas.undo()
w.flip_image(True); print("spiegel H: rood op x=%d" % (p.width - 11), p.layers[1].image.pixelColor(p.width - 11, 20).red() == 255); w.canvas.undo()
w.crop_to_selection()
w.canvas.selection = QRegion(QRect(5, 10, 300, 200)); w.crop_to_selection()
print("bijgesneden", p.width, p.height, "rood op (5,10):", p.layers[1].image.pixelColor(5, 10).red() == 255)
w.canvas.undo(); print("ongedaan", p.width, p.height)
w.rotate_image(180); w.rotate_image(-90); print("180 + links", p.width, p.height)
print("ALLES OK")
