# coding:utf-8
import os.path
import subprocess
import sys
from functools import partial

from PyQt5.QtCore import Qt, QUrl, QThread
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QLabel
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import (SwitchSettingCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, setTheme, setFont, MessageBox, ProgressBar)

from ..common.config import config, isWin11
from ..common.setting import FEEDBACK_URL, QQ
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..common.utils import get_local_version
from ..repackage.text_edit_card import TextEditCard


class UpdatingThread(QThread):

    def __init__(self, updater):
        super().__init__()
        self.updater = updater

    def run(self):
        self.updater.run()


class SettingCardGroup(CardGroup):

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        setFont(self.titleLabel, 14, QFont.Weight.DemiBold)


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.progressBar = ProgressBar(self)
        self.progressBar.setVisible(False)

        self.app_name = "SAA"
        # 获取当前应用路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            self.app_path = sys.executable
        else:
            # 脚本运行模式
            self.app_path = sys.argv[0]

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            config.micaEnabled,
            self.personalGroup
        )
        self.themeCard = ComboBoxSettingCard(
            config.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.enterCard = ComboBoxSettingCard(
            config.enter_interface,
            FIF.HOME,
            '启动时进入',
            self.tr("选择启动软件时直接进入哪个页面"),
            texts=[
                self.tr('展示页'), self.tr('主页'),
                self.tr('小工具')
            ],
            parent=self.personalGroup
        )
        self.zoomCard = ComboBoxSettingCard(
            config.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        # self.languageCard = ComboBoxSettingCard(
        #     config.language,
        #     FIF.LANGUAGE,
        #     self.tr('Language'),
        #     self.tr('Set your preferred language for UI'),
        #     texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
        #     parent=self.personalGroup
        # )

        # update software
        self.aboutSoftwareGroup = SettingCardGroup(
            self.tr("软件相关"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            '如果开启，每次游戏版本更新会自动更新对应活动刷体力的坐标和SAA提醒的链接',
            configItem=config.checkUpdateAtStartUp,
            parent=self.aboutSoftwareGroup
        )
        self.serverCard = ComboBoxSettingCard(
            config.server_interface,
            FIF.GAME,
            '游戏渠道选择',
            self.tr("请选择你所在的区服"),
            texts=[self.tr('官服'), self.tr('b服'), self.tr('国际服')],
            parent=self.aboutSoftwareGroup
        )
        self.isLogCard = SwitchSettingCard(
            FIF.DEVELOPER_TOOLS,
            self.tr('展示OCR识别结果'),
            '打开将在日志中显示ocr识别结果，获得更详细的日志信息',
            configItem=config.isLog,
            parent=self.aboutSoftwareGroup
        )
        self.showScreenshotCard = SwitchSettingCard(
            FIF.PHOTO,
            self.tr('展示运行时的窗口截图'),
            '用于在查错时查看是否正确截取了游戏对应位置的画面，截取的所有画面会保存在SAA/temp下，需要手动删除',
            configItem=config.showScreenshot,
            parent=self.aboutSoftwareGroup
        )
        self.saveScaleCacheCard = SwitchSettingCard(
            FIF.SAVE,
            self.tr('保存缩放比例数据'),
            '如果你的游戏窗口固定使用，可以选择保存，这样运行会匹配得更快，如果窗口大小经常变化则取消勾选',
            configItem=config.saveScaleCache,
            parent=self.aboutSoftwareGroup
        )
        self.autoScaling = SwitchSettingCard(
            FIF.BACK_TO_WINDOW,
            self.tr('自动缩放比例'),
            '默认开启，在启动SAA时如果发现游戏窗口比例不是16:9会自动缩放成1920*1080并贴在左上角',
            configItem=config.autoScaling,
            parent=self.aboutSoftwareGroup
        )
        self.autoStartTask = SwitchSettingCard(
            FIF.PLAY,
            self.tr('自动开始任务'),
            '打开SAA自动开始运行日常，必须先勾选并配置好自动打开游戏',
            configItem=config.auto_start_task,
            parent=self.aboutSoftwareGroup
        )
        self.autoBootStartup = SwitchSettingCard(
            FIF.POWER_BUTTON,
            self.tr('开机自启'),
            '开机时自动打开SAA',
            configItem=config.auto_boot_startup,
            parent=self.aboutSoftwareGroup
        )
        self.informMessage = SwitchSettingCard(
            FIF.HISTORY,
            self.tr('消息通知'),
            '是否打开体力恢复通知',
            configItem=config.inform_message,
            parent=self.aboutSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.proxyCard = TextEditCard(
            config.update_proxies,
            FIF.GLOBE,
            '代理端口',
            "如‘7890’",
            '如果选择开代理则需要填入代理端口，不开代理则置空',
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            '前往B站',
            FIF.FEEDBACK,
            '提供反馈',
            '唯一平台b站：芬妮舞狮，QQ群：' + QQ,
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            "app/resource/images/logo.png",
            self.tr('About'),
            "本助手免费开源，当前版本：" + get_local_version(),
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 50)

        self.aboutCard.vBoxLayout.addWidget(self.progressBar)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.enterCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        # self.personalGroup.addSettingCard(self.languageCard)

        self.aboutSoftwareGroup.addSettingCard(self.updateOnStartUpCard)
        self.aboutSoftwareGroup.addSettingCard(self.serverCard)
        self.aboutSoftwareGroup.addSettingCard(self.isLogCard)
        self.aboutSoftwareGroup.addSettingCard(self.showScreenshotCard)
        self.aboutSoftwareGroup.addSettingCard(self.saveScaleCacheCard)
        self.aboutSoftwareGroup.addSettingCard(self.autoScaling)
        self.aboutSoftwareGroup.addSettingCard(self.autoStartTask)
        self.aboutSoftwareGroup.addSettingCard(self.autoBootStartup)
        self.aboutSoftwareGroup.addSettingCard(self.informMessage)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.proxyCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=2000,
            parent=self
        )

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        config.appRestartSig.connect(self._showRestartTooltip)

        # personalization
        config.themeChanged.connect(setTheme)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)
        self.autoBootStartup.checkedChanged.connect(self.set_windows_start)

        # check update
        self.aboutCard.clicked.connect(self.check_update)

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def set_windows_start(self, is_checked):
        if is_checked:
            self._enable_windows()
        else:
            self._disable_windows()

    def _enable_windows(self):
        """Windows 启用自启"""
        import winreg as reg

        # 创建启动命令
        command = f'"{self.app_path}"'
        print(command)

        # 注册表路径
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, self.app_name, 0, reg.REG_SZ, command)
            reg.CloseKey(key)
            InfoBar.success(
                '添加自启成功',
                f'已将{command}加入自启',
                isClosable=True,
                duration=2000,
                parent=self
            )
        except Exception as e:
            # 如果权限不足，尝试使用任务计划程序
            InfoBar.error(
                '添加自启失败',
                f"权限不足：{e}",
                isClosable=True,
                duration=2000,
                parent=self
            )

    def _disable_windows(self):
        """Windows 禁用自启"""
        import winreg as reg

        # 尝试删除注册表项
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            try:
                reg.DeleteValue(key, self.app_name)
                InfoBar.success(
                    '删除自启成功',
                    f'已关闭开机自启',
                    isClosable=True,
                    duration=2000,
                    parent=self
                )
            except WindowsError:
                InfoBar.error(
                    '删除自启失败',
                    f"键不存在",
                    isClosable=True,
                    duration=2000,
                    parent=self
                )
            reg.CloseKey(key)
        except Exception as e:
            InfoBar.error(
                '删除自启失败',
                f"{e}",
                isClosable=True,
                duration=2000,
                parent=self
            )

        # 尝试删除任务计划
        # try:
        #     subprocess.run(['schtasks', '/delete', '/tn', self.app_name, '/f'],
        #                    shell=True, check=True)
        # except subprocess.CalledProcessError:
        #     pass  # 任务不存在

    def check_update(self):
        pass
        # try:
        #     updater = Updater()
        #     current_version = VERSION
        #     latest_version = updater.latest_version
        #     if latest_version != current_version and latest_version:
        #         title = '发现新版本'
        #         content = f'检测到新版本：{current_version} -> {latest_version}，是否更新？'
        #         massage_box = MessageBox(title, content, self.window())
        #         if massage_box.exec():
        #             self.start_download(updater)
        #         else:
        #             pass
        #     elif latest_version is None:
        #         title = '未获取到最新版本信息'
        #         if config.update_proxies.value:
        #             content = f'端口{config.update_proxies.value}无法连接至github/gitee，请检查你的网络，确保你的代理设置正确或关闭代理并设置端口为空值'
        #         else:
        #             content = '无法连接至github/gitee，请检查你的网络，确保你的代理设置正确或关闭代理并设置端口为空值'
        #         massage_box = MessageBox(title, content, self.window())
        #         if massage_box.exec():
        #             pass
        #         else:
        #             pass
        #     else:
        #         title = '没有发现新版本'
        #         content = f'当前版本{current_version}已是最新版本'
        #         massage_box = MessageBox(title, content, self.window())
        #         if massage_box.exec():
        #             pass
        #         else:
        #             pass
        # except Exception as e:
        #     title = '网络错误'
        #     if config.update_proxies.value:
        #         content = f'端口{config.update_proxies.value}无法连接至github/gitee，请检查你的网络，确保你的代理设置正确或关闭代理并设置端口为空值'
        #     else:
        #         content = '无法连接至github/gitee，请检查你的网络，确保你的代理设置正确或关闭代理并设置端口为空值'
        #     massage_box = MessageBox(title, content, self.window())
        #     if massage_box.exec():
        #         pass
        #     else:
        #         pass
        #     print(e)
        #     # traceback.print_exc()

    def start_download(self, updater):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.updating_thread = UpdatingThread(updater)
        signalBus.checkUpdateSig.connect(self.update_progress)
        self.updating_thread.finished.connect(partial(self.update_finished, updater.download_file_path))
        self.updating_thread.start()

    def update_progress(self, value):
        """ Update the progress bar """
        self.progressBar.setValue(value)

    def update_finished(self, zip_path):
        """ Hide progress bar and show completion message """
        self.progressBar.setVisible(False)
        if os.path.exists(zip_path):
            title = '更新完成'
            content = f'压缩包已下载至{zip_path}，即将重启更新'
            message_box = MessageBox(title, content, self.parent.window())
            message_box.cancelButton.setVisible(False)
            if message_box.exec():
                subprocess.Popen([sys.executable, 'update.py', zip_path])
                self.parent.close()
        else:
            InfoBar.error(
                '更新下载失败',
                f'请前往github/gitee自行下载release，或者去群{QQ}找最新文件下载',
                isClosable=True,
                duration=-1,
                parent=self
            )

    def scrollToAboutCard(self):
        """ scroll to example card """
        try:
            w = self.aboutCard
            self.verticalScrollBar().setValue(w.y())
        except Exception as e:
            print(e)
