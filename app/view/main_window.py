# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF

from .additional_features import Additional
from .help import Help
from .home import Home
from .setting_interface import SettingInterface
from ..common.config import config
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common import resource


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # TODO: create sub interface
        self.homeInterface = Home('Home Interface', self)
        self.additionalInterface = Additional('Additional Interface', self)

        self.helpInterface = Help('Help Interface', self)
        self.settingInterface = SettingInterface(self)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.additionalInterface, FIF.APPLICATION, '小工具')

        # add custom widget to bottom
        self.addSubInterface(self.helpInterface,FIF.HELP,'帮助',position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED,
            NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':app/resource/images/logo.png'))
        self.setWindowTitle('芬妮舞狮')

        # self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setBackgroundColor(QColor(240, 244, 249))
        self.setMicaEffectEnabled(config.get(config.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
