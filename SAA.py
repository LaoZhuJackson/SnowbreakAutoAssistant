# coding:utf-8
import os
import sys
import time

from win11toast import toast

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.common.config import config
from app.view.main_window import MainWindow

if '--toast-only' in sys.argv:
    toast(
        'SAA 尘白助手', '体力即将完全恢复，注意使用',
        icon=r'C:\Users\undownding\IdeaProjects\SnowbreakAutoAssistant\app\resource\images\logo.ico',
    )
    time.sleep(5)
    quit()

# enable dpi scale
if config.get(config.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(config.get(config.dpiScale))
else:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = config.get(config.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "app", ".", ":/app/resource/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
w = MainWindow()
w.show()

app.exec()
