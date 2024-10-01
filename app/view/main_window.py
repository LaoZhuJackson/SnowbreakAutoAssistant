# coding: utf-8
import traceback

from PyQt5.QtCore import QSize, QTimer, QThread, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QFrame

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, MessageBoxBase, SubtitleLabel, \
     BodyLabel, NavigationBarPushButton, FlyoutView, Flyout, setThemeColor
from qfluentwidgets import FluentIcon as FIF

from .additional_features import Additional
from .help import Help
from .home import Home
from .setting_interface import SettingInterface
from ..common.config import config
from ..common.icon import Icon
from ..common.ppOCR import ocr_installer, ocr
from ..common.signal_bus import signalBus
from ..common import resource  # 不能删，设置页的样式需要
from ..ui.display_interface import DisplayInterface


class InstallOcr(QThread):

    def __init__(self, ocr_installer, parent=None):
        super().__init__()
        self.ocr_installer = ocr_installer
        self.parent = parent

    def run(self):
        self.ocr_installer.install_ocr()


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # TODO: create sub interface
        self.displayInterface = DisplayInterface(self)
        self.homeInterface = Home('Home Interface', self)
        self.additionalInterface = Additional('Additional Interface', self)

        self.helpInterface = Help('Help Interface', self)
        self.settingInterface = SettingInterface(self)

        self.support_button = NavigationBarPushButton(FIF.HEART, '赞赏', isSelectable=False)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

        # 检查ocr组件是否安装
        QTimer.singleShot(200, self.check_ocr_install)

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        # signalBus.check_ocr_progress.connect(self.update_ring)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        self.addSubInterface(self.displayInterface, FIF.PHOTO, '展示页')
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.additionalInterface, FIF.APPLICATION, '小工具')

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            'avatar',
            self.support_button,
            self.onSupport,
            NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(self.helpInterface, FIF.HELP, '帮助', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED,
            NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':app/resource/images/logo.png'))
        self.setWindowTitle('SAA尘白助手')

        setThemeColor("#009FAA")

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

    def check_ocr_install(self):
        self.ocr_installer = ocr_installer
        if self.ocr_installer.check_ocr():
            print('OCR组件已安装')
            pass
        else:
            self.messagebox = MessageBoxBase(self)
            title = SubtitleLabel('检测到未下载OCR组件', self)
            self.content = BodyLabel('是否开始下载，若取消则退出程序', self)
            # self.speed = BodyLabel('', self)
            # self.speed.setVisible(False)
            # self.progressRing = ProgressRing()
            # self.progressRing.setValue(0)
            # self.progressRing.setVisible(False)

            self.messagebox.viewLayout.addWidget(title, 0, Qt.AlignLeft)
            self.messagebox.viewLayout.addWidget(self.content, 0, Qt.AlignLeft)
            # self.messagebox.viewLayout.addWidget(self.progressRing, 0, Qt.AlignCenter)
            # self.messagebox.viewLayout.addWidget(self.speed, 0, Qt.AlignCenter)
            self.messagebox.yesButton.setText('下载')
            self.messagebox.cancelButton.setText('退出')
            self.messagebox.yesButton.clicked.connect(self.yes_click)
            self.messagebox.cancelButton.clicked.connect(self.cancel_click)

            self.messagebox.setVisible(True)

    # def update_ring(self, value, speed):
    #     self.progressRing.setValue(value)
    #     self.speed.setText(speed)

    def yes_click(self):
        self.check_ocr_thread = InstallOcr(self.ocr_installer)
        try:
            # self.content.setVisible(False)
            # self.progressRing.setVisible(True)
            # self.speed.setVisible(True)
            self.check_ocr_thread.start()
        except Exception as e:
            print(e)
            # traceback.print_exc()

    def cancel_click(self):
        self.close()

    def onSupport(self):
        view = FlyoutView(
            title="赞助作者",
            content="如果这个助手帮助到你，而你恰巧财力雄厚，可以考虑为作者更新时加杯奶茶(>ω･* )ﾉ",
            image="asset/support.png",
            isClosable=True,
        )
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        w = Flyout.make(view, self.support_button, self)
        view.closed.connect(w.close)

    def switchToSample(self, routeKey, index):
        """
        用于跳转到指定页面
        :param routeKey: 跳转路径
        :param index:
        :return:
        """
        interfaces = self.findChildren(QFrame)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                # w.scrollToCard(index)

    def closeEvent(self, a0):
        print("关闭ocr子进程")
        ocr.exit_ocr()
        a0.accept()
