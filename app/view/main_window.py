# coding: utf-8
import datetime
import os.path
import re
import subprocess
import threading
import time
import sys

import cv2
import numpy as np
from PyQt5.QtCore import QSize, QTimer, QThread, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QFrame
from qfluentwidgets import FluentIcon as FIF, SystemThemeListener, isDarkTheme, MessageBox
from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, NavigationBarPushButton, FlyoutView, \
    Flyout, setThemeColor

from .additional_features import Additional
from .help import Help
from .home import Home
from .ocr_replacement_table import OcrReplacementTable
from .setting_interface import SettingInterface
from .trigger import Trigger
from ..common.config import config
from ..common.icon import Icon
from ..common.logger import logger
from ..common.matcher import matcher
from ..common.signal_bus import signalBus
from ..common.utils import get_start_arguments, get_gitee_text, get_local_version
from ..modules.ocr import ocr
from ..repackage.custom_message_box import CustomMessageBox
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
        self.tableInterface = OcrReplacementTable('Table Interface', self)
        self.settingInterface = SettingInterface(self)

        self.support_button = NavigationBarPushButton(FIF.HEART, '赞赏', isSelectable=False)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        self.updater = None
        self.message_window = None

        # start theme listener
        self.themeListener.start()

        # 初始化ocr
        ocr_thread = threading.Thread(target=self.init_ocr)
        ocr_thread.daemon = True
        ocr_thread.start()
        # if config.CheckBox_open_game_directly.value:
        #     self.open_game_directly()
        if config.checkUpdateAtStartUp.value:
            # QTimer.singleShot(100, lambda: self.check_update())
            # 当采用其他线程调用时，需要保证messageBox是主线程调用的，使用信号槽机制在主线程调用 QMessageBox
            # update_thread = threading.Thread(target=self.check_update)
            # update_thread.start()
            self.check_update()

        if '--auto' in sys.argv:
            self.homeInterface.on_start_button_click()

    def open_game_directly(self):
        """直接启动游戏"""
        # 用户提供的能在启动器找到的路径
        start_path = config.LineEdit_game_directory.value
        start_path = start_path.replace("/", "\\")
        game_channel = config.server_interface.value
        exe_path = os.path.join(start_path, r'game\Game\Binaries\Win64\Game.exe')
        try:
            launch_args = get_start_arguments(start_path, game_channel)
            if not launch_args:
                logger.error(f"游戏启动失败未找到对应参数，start_path：{start_path}，game_channel:{game_channel}")
                return
            else:
                # 尝试以管理员权限运行
                subprocess.Popen([exe_path] + launch_args)
                logger.debug(f'正在启动 {exe_path} {launch_args}')
        except FileNotFoundError:
            logger.error(f'没有找到对应文件: {exe_path}')
        except Exception as e:
            logger.error(f'出现报错: {e}')

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.showMessageBox.connect(self.showMessageBox)
        signalBus.showScreenshot.connect(self.showScreenshot)
        # signalBus.check_ocr_progress.connect(self.update_ring)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        self.addSubInterface(self.displayInterface, FIF.PHOTO, '展示页')
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.additionalInterface, FIF.APPLICATION, '小工具')
        self.addSubInterface(self.triggerInterface, FIF.COMPLETED, '触发器')
        self.addSubInterface(self.tableInterface, FIF.SYNC, '替换表')

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
        # logger.info(f"区域截图识别每次平均耗时：{benchmark(ocr.run, 'app/resource/images/start_game/age.png')}")

    def initWindow(self):
        self.resize(960, 860)
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
            image="asset/support.jpg",
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
        """保存所有log到html中"""

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
            """保存HTML内容，如果是空内容则跳过"""
            if not content or is_empty_html(content):
                return
            with open(path, "w", encoding='utf-8') as file:
                file.write(content)

        def clean_old_logs(log_dir, max_files=30):
            """清理旧日志文件，保留最多max_files个"""
            if not os.path.exists(log_dir):
                return

            all_logs = [
                f for f in os.listdir(log_dir)
                if f.endswith('.html') and os.path.isfile(os.path.join(log_dir, f))
            ]

            if len(all_logs) <= max_files:
                return

            # 按创建时间排序并删除最旧的文件
            all_logs.sort(key=lambda x: os.path.getctime(os.path.join(log_dir, x)))
            for file_to_remove in all_logs[:len(all_logs) - max_files]:
                os.remove(os.path.join(log_dir, file_to_remove))

        # 日志配置：目录、UI组件、文件名前缀
        log_configs = [
            ("./log/home", self.homeInterface.textBrowser_log, "home"),
            ("./log/fishing", self.additionalInterface.textBrowser_log_fishing, "fishing"),
            ("./log/action", self.additionalInterface.textBrowser_log_action, "action"),
            ("./log/jigsaw", self.additionalInterface.textBrowser_log_jigsaw, "jigsaw"),
            ("./log/water_bomb", self.additionalInterface.textBrowser_log_water_bomb, "water_bomb"),
            ("./log/alien_guardian", self.additionalInterface.textBrowser_log_alien_guardian, "alien_guardian"),
            ("./log/maze", self.additionalInterface.textBrowser_log_maze, "maze"),
            ("./log/massaging", self.additionalInterface.textBrowser_log_massaging, "massaging"),
            ("./log/drink", self.additionalInterface.textBrowser_log_drink, "drink")
        ]

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for log_dir, text_browser, prefix in log_configs:
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)

            # 清理旧日志
            clean_old_logs(log_dir)

            # 获取并保存日志内容
            log_content = text_browser.toHtml()
            filename = f"{prefix}_{timestamp}.html"
            save_html(os.path.join(log_dir, filename), log_content)

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
            # 保存缩放数据
            if config.saveScaleCache.value:
                matcher.save_scale_cache()
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
        # logger.warn('当前测试版还没写更新功能')
        version_online = get_gitee_text("update_data.txt")
        saa_current_version = get_local_version()
        # 返回字典说明必定出现报错了
        if isinstance(version_online, dict):
            logger.error(version_online["error"])
            return
        version = version_online[1]
        if not saa_current_version or saa_current_version != version:
            logger.info(f"出现版本更新{saa_current_version}→{version}，可以前往github或者q群下载新版安装包")
        else:
            logger.debug(f"无需版本更新，当前版本：{saa_current_version}")

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

    def showScreenshot(self, screenshot):
        """
        展示当前截图
        :param screenshot:
        :return:
        """
        def ndarray_to_qpixmap(ndarray):
            # 确保ndarray是3维的 (height, width, channels)
            if ndarray.ndim == 2:
                ndarray = np.expand_dims(ndarray, axis=-1)
                ndarray = np.repeat(ndarray, 3, axis=-1)

            height, width, channel = ndarray.shape
            bytes_per_line = 3 * width
            # 显示需要rgb格式
            ndarray = cv2.cvtColor(ndarray, cv2.COLOR_BGR2RGB)

            # 将ndarray转换为QImage
            qimage = QImage(ndarray.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # 将QImage转换为QPixmap
            return QPixmap.fromImage(qimage)

        def save_screenshot(ndarray):
            # 检查 temp 目录是否存在，如果不存在则创建
            if not os.path.exists('temp'):
                os.makedirs('temp')
            # cv2保存是bgr格式
            cv2.imwrite(f'temp/{time.time()}.png', ndarray)

        save_screenshot(screenshot)

        if not isinstance(self.message_window, CustomMessageBox):
            self.message_window = CustomMessageBox(self, '当前截图', 'image')
        screenshot_pixmap = ndarray_to_qpixmap(screenshot)
        # 按比例缩放图像
        scaled_pixmap = screenshot_pixmap.scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.message_window.content.setPixmap(scaled_pixmap)
        if self.message_window.exec():
            pass
        else:
            pass
