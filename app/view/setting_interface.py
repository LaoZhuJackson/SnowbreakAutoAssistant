# coding:utf-8
import time
import traceback

from qfluentwidgets import (SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme, setFont, MessageBox, ProgressBar)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths, QThread
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QProgressBar

from updater import Updater
from ..repackage.text_edit_card import TextEditCard
from ..common.config import config, isWin11
from ..common.setting import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, QQ
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet


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
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.progressBar = ProgressBar(self)
        self.progressBar.setVisible(False)

        self.update_success = False

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
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            '版本更稳定且拥有更多新功能',
            configItem=config.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.proxyCard = TextEditCard(
            config.update_proxies,
            FIF.GLOBE,
            '代理端口',
            "如‘7890’",
            '设置你的代理端口，方便连接至github',
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
            "本助手免费开源，当前版本：" + VERSION,
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

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.proxyCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        config.appRestartSig.connect(self._showRestartTooltip)

        # personalization
        config.themeChanged.connect(setTheme)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # check update
        self.aboutCard.clicked.connect(self.check_update)

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def check_update(self):
        try:
            updater = Updater()
            current_version = VERSION
            latest_version = updater.latest_version
            if latest_version != current_version and latest_version:
                title = '发现新版本'
                content = f'检测到新版本：{current_version} -> {latest_version}，是否更新？'
                massage_box = MessageBox(title, content, self.window())
                if massage_box.exec():
                    self.progressBar.setValue(0)
                    self.progressBar.setVisible(True)
                    self.updating_thread = UpdatingThread(updater)
                    signalBus.checkUpdateSig.connect(self.update_progress)
                    self.updating_thread.finished.connect(self.update_finished)
                    self.updating_thread.start()
                else:
                    print('Cancel button is pressed')
            elif latest_version is None:
                title = '未获取到最新版本信息'
                content = f'端口{config.update_proxies.value}无法连接至github，请检查你的网络，确保你的代理设置正确'
                massage_box = MessageBox(title, content, self.window())
                if massage_box.exec():
                    pass
                else:
                    pass
            else:
                title = '没有发现新版本'
                content = f'当前版本{current_version}已是最新版本'
                massage_box = MessageBox(title, content, self.window())
                if massage_box.exec():
                    pass
                else:
                    pass
        except Exception as e:
            title = '网络错误'
            content = f'端口{config.update_proxies.value}无法连接至github，请检查你的网络，确保你的代理设置正确'
            massage_box = MessageBox(title, content, self.window())
            if massage_box.exec():
                pass
            else:
                pass
            print(e)
            # traceback.print_exc()

    def update_progress(self, value):
        """ Update the progress bar """
        self.progressBar.setValue(value)
        if value >= 98:
            self.update_success = True

    def update_finished(self):
        """ Hide progress bar and show completion message """
        self.progressBar.setVisible(False)
        if self.update_success:
            # todo 实现自动重启更新
            InfoBar.success(
                '更新下载完成',
                '请到助手目录下的“temp”文件夹中剪切解压好的文件到exe目录下',
                isClosable=True,
                duration=-1,
                parent=self
            )
        else:
            InfoBar.error(
                '更新下载失败',
                '请前往github自行下载release，或者去群里找最新文件下载',
                isClosable=True,
                duration=-1,
                parent=self
            )
