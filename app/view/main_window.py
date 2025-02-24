# coding: utf-8
import datetime
import os.path
import re
import subprocess
import threading
import time
import traceback

import pyautogui
from PyQt5.QtCore import QSize, QTimer, QThread, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QFrame
from qfluentwidgets import FluentIcon as FIF, SystemThemeListener, isDarkTheme, MessageBox, Dialog
from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, MessageBoxBase, SubtitleLabel, \
    BodyLabel, NavigationBarPushButton, FlyoutView, Flyout, setThemeColor

from .additional_features import Additional
from .help import Help
from .home import Home
from .setting_interface import SettingInterface
from .trigger import Trigger
from ..common.config import config
from ..common.icon import Icon
from ..common.logger import logger
from ..common.setting import VERSION
from ..common.signal_bus import signalBus
from ..modules.ocr import ocr
from ..ui.display_interface import DisplayInterface
from ..common import resource


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

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        # TODO: create sub interface
        self.displayInterface = DisplayInterface(self)
        self.homeInterface = Home('Home Interface', self)
        self.additionalInterface = Additional('Additional Interface', self)
        self.triggerInterface = Trigger('Trigger Interface', self)

        self.helpInterface = Help('Help Interface', self)
        self.settingInterface = SettingInterface(self)

        self.support_button = NavigationBarPushButton(FIF.HEART, '赞赏', isSelectable=False)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        self.updater = None

        # start theme listener
        self.themeListener.start()

        # 初始化ocr
        ocr_thread = threading.Thread(target=self.init_ocr)
        ocr_thread.daemon = True
        ocr_thread.start()
        if config.CheckBox_auto_open_starter.value:
            self.open_starter()
        if config.checkUpdateAtStartUp.value:
            # QTimer.singleShot(100, lambda: self.check_update())
            # 当采用其他线程调用时，需要保证messageBox是主线程调用的，使用信号槽机制在主线程调用 QMessageBox
            update_thread = threading.Thread(target=self.check_update)
            update_thread.start()

    def open_starter(self):
        windows = pyautogui.getWindowsWithTitle(config.LineEdit_starter_name.value)
        if windows:
            logger.debug("已打开游戏")
            return
        starter_path = config.LineEdit_starter_directory.value
        try:
            subprocess.Popen(starter_path)
            logger.debug(f'打开 {starter_path} 成功')
        except FileNotFoundError:
            logger.error(f'没有找到对应启动器: {starter_path}')
        except Exception as e:
            logger.error(f'出现报错: {e}')

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.showMessageBox.connect(self.showMessageBox)
        # signalBus.check_ocr_progress.connect(self.update_ring)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        self.addSubInterface(self.displayInterface, FIF.PHOTO, '展示页')
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.additionalInterface, FIF.APPLICATION, '小工具')
        self.addSubInterface(self.triggerInterface, FIF.COMPLETED, '触发器')

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

        self.stackedWidget.setCurrentIndex(config.enter_interface.value)

    def init_ocr(self):
        def benchmark(ocr_func, img, runs=30):
            # 预热
            for _ in range(10):
                ocr_func(img, is_log=False)

            # 正式测试
            start = time.time()
            for _ in range(runs):
                ocr_func(img, is_log=False)
            return (time.time() - start) / runs

        ocr.instance_ocr()
        logger.info(f"区域截图识别每次平均耗时：{benchmark(ocr.run, 'app/resource/images/start_game/age.png')}")
        logger.debug("初始化OCR完成")

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':app/resource/images/logo.png'))
        self.setWindowTitle('SAA尘白助手')

        setThemeColor("#009FAA")

        # 触发重绘，使一开始的背景颜色正确
        # self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        # self.setBackgroundColor(QColor(240, 244, 249))
        self.setMicaEffectEnabled(config.get(config.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(150, 150))
        self.splashScreen.raise_()

        position = config.position.value
        if position:
            self.move(position[0], position[1])
            self.show()
        else:
            desktop = QApplication.primaryScreen().availableGeometry()
            w, h = desktop.width(), desktop.height()
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
            self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

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
            content="如果这个助手帮助到你，可以考虑赞助作者一杯奶茶(>ω･* )ﾉ",
            image="app/resource/images/support.jpg",
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

    def save_log(self):
        """保存所有log到txt中"""

        def is_empty_html(content):
            """
            判断 HTML 内容是否为空
            """
            # 使用正则表达式匹配空的段落 (<p>) 或者换行 (<br />)
            empty_html_pattern = re.compile(r'<p[^>]*>\s*(<br\s*/?>)?\s*</p>', re.IGNORECASE)

            # 去掉默认的头部信息后，检查是否只剩下空的段落
            body_content = re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|<head[^>]*>.*?</head>|<body[^>]*>|</body>|</html>', '',
                                  content, flags=re.DOTALL)
            return bool(empty_html_pattern.fullmatch(body_content.strip()))

        def save_html(path, content):
            # 使用了 strip() 方法来去掉内容中的空白字符（例如空格、换行符等）
            # print(is_empty_html(content))
            if is_empty_html(content):
                return
            if content:
                # "w"模式实现先清空再写入
                with open(path, "w", encoding='utf-8') as file:
                    file.write(content)

        def clean_old_logs(log_dir, max_files=30):
            """检查日志文件夹，删除最早的文件以保持最多 `max_files` 个文件"""
            # 获取所有日志文件并按文件创建时间排序
            all_logs = [f for f in os.listdir(log_dir) if f.endswith('.html')]
            all_logs.sort(key=lambda x: os.path.getctime(os.path.join(log_dir, x)))  # 按创建时间排序

            # 如果文件数量超过 max_files，则删除最早的文件
            if len(all_logs) >= max_files:
                # 删除最早的文件
                os.remove(os.path.join(log_dir, all_logs[0]))

        home_log_dir = "./log/home"
        fishing_log_dir = "./log/fishing"
        action_log_dir = "./log/action"
        jigsaw_log_dir = "./log/jigsaw"
        log_path_list = [home_log_dir, fishing_log_dir, action_log_dir, jigsaw_log_dir]
        for log_dir in log_path_list:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            else:
                # 清理旧日志文件（如果存在超过 30 个文件）
                clean_old_logs(log_dir)

        home_log = self.homeInterface.textBrowser_log.toHtml()
        fishing_log = self.additionalInterface.textBrowser_log_fishing.toHtml()
        action_log = self.additionalInterface.textBrowser_log_action.toHtml()
        jigsaw_log = self.additionalInterface.textBrowser_log_jigsaw.toHtml()

        name_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_html(os.path.join(home_log_dir, f"home_log_{name_time}.html"), home_log)
        save_html(os.path.join(fishing_log_dir, f"fishing_log_{name_time}.html"), fishing_log)
        save_html(os.path.join(action_log_dir, f"action_log_{name_time}.html"), action_log)
        save_html(os.path.join(jigsaw_log_dir, f"jigsaw_log_{name_time}.html"), jigsaw_log)

    def save_position(self):
        # 获取当前窗口的位置和大小
        geometry = self.geometry()
        position = (geometry.left(), geometry.top())
        config.set(config.position, position)

    def closeEvent(self, a0):
        ocr.stop_ocr()
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        try:
            # 保存日志到文件
            self.save_log()
            self.save_position()
        except Exception as e:
            logger.error(e)
            # traceback.print_exc()
        super().closeEvent(a0)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))

    def check_update(self):
        logger.warn('当前测试版还没写更新功能')
        pass

    def showMessageBox(self, title, content):
        massage = MessageBox(title, content, self)
        if massage.exec():
            w = self.settingInterface
            self.stackedWidget.setCurrentWidget(w, False)
            w.scrollToAboutCard()
            if self.updater:
                self.settingInterface.start_download(self.updater)
        else:
            pass
