import sys
import time
import traceback
from functools import partial

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFrame, QWidget
from qfluentwidgets import SpinBox, CheckBox, ComboBox

from app.common.config import config
from app.common.logger import logger, stdout_stream, stderr_stream, original_stdout, original_stderr
from app.modules.fishing.fishing import FishingModule

from app.ui.additional_features_interface import Ui_additional_features


class RunFishing(QThread):
    is_running_fishing = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.module = FishingModule()

    def run(self):
        self.is_running_fishing.emit(True)
        logger.info("请确保游戏窗口是全屏，分辨率是1920*1080，并在三秒内确保游戏窗口置顶无遮挡")
        time.sleep(3)
        try:
            for i in range(config.SpinBox_fish_times.value):
                print(f"is_running_fishing:{is_running}")
                if not is_running:
                    break
                logger.info(f"开始第 {i+1} 次钓鱼")
                self.module.run()
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
        finally:
            self.is_running_fishing.emit(False)


def get_all_children(widget):
    """
    递归地获取指定QWidget及其所有后代控件的列表。

    :param widget: QWidget对象，从该对象开始递归查找子控件。
    :return: 包含所有子控件（包括后代）的列表。
    """
    children = []
    for child in widget.children():
        children.append(child)
        children.extend(get_all_children(child))  # 递归调用以获取后代控件
    return children


class Additional(QFrame, Ui_additional_features):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['商店', '体力', '奖励']

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.is_running_fish = False

        self._initWidget()
        self._load_config()
        self._connect_to_slot()
        self._redirectOutput()

    def _initWidget(self):
        # 正向链接
        self.SegmentedWidget.addItem(self.page_fishing.objectName(), '自动钓鱼',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_fishing))
        self.SegmentedWidget.addItem(self.page_2.objectName(), '待开发1',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.SegmentedWidget.addItem(self.page_3.objectName(), '待开发2',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.SegmentedWidget.setCurrentItem(self.page_fishing.objectName())

        self.stackedWidget.setCurrentIndex(0)

    def _load_config(self):
        # 钓鱼相关
        self.SpinBox_fish_times.setValue(config.SpinBox_fish_times.value)
        self.CheckBox_is_save_fish.setChecked(config.CheckBox_is_save_fish.value)

    def _connect_to_slot(self):
        # 反向链接
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.PushButton_start_fishing.clicked.connect(self.start_fishing)

        # 链接各种需要保存修改的控件
        self._connect_to_save_changed()

    def _connect_to_save_changed(self):
        children_list = get_all_children(self)
        for children in children_list:
            # 此时不能用lambda，会使传参出错
            if isinstance(children, CheckBox):
                children.stateChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, ComboBox):
                children.currentIndexChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, SpinBox):
                children.valueChanged.connect(partial(self.save_changed, children))

    def _redirectOutput(self):
        # 普通输出
        sys.stdout = stdout_stream
        # 报错输出
        sys.stderr = stderr_stream
        # 将新消息信号连接到QTextEdit
        stdout_stream.message.connect(self.__updateDisplay)
        stderr_stream.message.connect(self.__updateDisplay)

    def __updateDisplay(self, message):
        # 将消息添加到 QTextEdit，自动识别 HTML
        self.textBrowser_log.insertHtml(message)
        self.textBrowser_log.insertPlainText('\n')  # 为下一行消息留出空间
        self.textBrowser_log.ensureCursorVisible()  # 滚动到最新消息

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())

    def start_fishing(self):
        self.run_fishing_thread = RunFishing()
        self.run_fishing_thread.is_running_fishing.connect(self.toggle_fish_button)
        self.set_fish_running()

    def toggle_fish_button(self, running):
        # logger.debug(f"执行set_is_running:{is_running}")
        self.is_running_fish = running
        if running:
            self.SpinBox_fish_times.setEnabled(False)
            self.PushButton_start_fishing.setText("停止钓鱼")
        else:
            self.SpinBox_fish_times.setEnabled(True)
            self.PushButton_start_fishing.setText("开始钓鱼")

    def set_fish_running(self):
        if not self.is_running_fish:
            global is_running
            is_running = True
            self.run_fishing_thread.start()
        else:
            is_running = False
            logger.info("已发生停止指令，等待当前钓鱼完成")


    def save_changed(self, widget):
        if isinstance(widget, SpinBox):
            config.set(getattr(config, widget.objectName(), None), widget.value())
        if isinstance(widget, CheckBox):
            config.set(getattr(config, widget.objectName(), None), widget.isChecked())

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
