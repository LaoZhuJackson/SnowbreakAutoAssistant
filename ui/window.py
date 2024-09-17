# coding:utf-8
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QWidget
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, MSFluentWindow)
from qfluentwidgets import FluentIcon as FIF

from ui.home_interface import Ui_home
from widgets.home import Home
from widgets.terminal import Terminal


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()

        # 创建子页面
        # self.homeInterface = Widget('Search Interface', self)
        self.homeInterface = Home('Home Interface', self)

        self.musicInterface = Widget('Music Interface', self)
        self.terminalInterface = Terminal('Terminal Interface', self)
        # self.videoInterface = Widget('Video Interface', self)
        # self.folderInterface = Widget('Folder Interface', self)
        self.settingInterface = Widget('Setting Interface', self)
        # self.albumInterface = Widget('Album Interface', self)
        # self.albumInterface1 = Widget('Album Interface 1', self)
        # self.albumInterface2 = Widget('Album Interface 2', self)
        # self.albumInterface1_1 = Widget('Album Interface 1-1', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.terminalInterface, FIF.COMMAND_PROMPT, '终端')
        self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        # self.navigationInterface.addSeparator()

        # self.addSubInterface(self.albumInterface, FIF.ALBUM, 'Albums', NavigationItemPosition.SCROLL)
        # self.addSubInterface(self.albumInterface1, FIF.ALBUM, 'Album 1', parent=self.albumInterface)
        # self.addSubInterface(self.albumInterface1_1, FIF.ALBUM, 'Album 1.1', parent=self.albumInterface1)
        # self.addSubInterface(self.albumInterface2, FIF.ALBUM, 'Album 2', parent=self.albumInterface)
        # self.addSubInterface(self.folderInterface, FIF.FOLDER, 'Folder library', NavigationItemPosition.SCROLL)

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('LaoZhu', './ui/resource/fenni-removebg.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', position=NavigationItemPosition.BOTTOM)

        # add badge to navigation item
        # item = self.navigationInterface.widget(self.videoInterface.objectName())
        # InfoBadge.attension(
        #     text=9,
        #     parent=item.parent(),
        #     target=item,
        #     position=InfoBadgePosition.NAVIGATION_ITEM
        # )

        # NOTE: enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        self.resize(900, 700)
        # self.setFixedSize(900, 700)
        self.setWindowIcon(QIcon('ui/resource/fenni-removebg.png'))
        self.setWindowTitle('芬妮舞狮')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '欢迎大伙来github上star这个项目，也可以通过issue来提出问题，你的支持就是我更新的最大动力',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/LaoZhuJackson/auto_chenbai"))

    def closeEvent(self, event):
        # 首先关闭子窗口
        if self.terminalInterface:
            self.terminalInterface.close()
        if self.homeInterface:
            self.homeInterface.close()

        # 确保主窗口的关闭事件继续进行
        super().closeEvent(event)
