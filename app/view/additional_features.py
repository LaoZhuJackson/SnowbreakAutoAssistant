import sys

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFrame, QWidget

from app.common.logger import logger, stdout_stream, stderr_stream, original_stdout, original_stderr

from app.modules.fishing import fishing_module
from app.ui.additional_features_interface import Ui_additional_features


class RunFishing(QThread):
    is_running_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._is_running = True
        self.module = fishing_module()

    def run(self):
        self.is_running_signal.emit(True)
        try:
            logger.debug(self._is_running)
            self.module.fishing()

        except Exception as e:
            logger.error(e)

    def stop_subprocess(self):
        self._is_running = False
        self.module.stop_fishing()
        logger.info("已发送停止指令，等待剩余动作执行完成后停止")


class Additional(QFrame, Ui_additional_features):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['商店', '体力', '奖励']

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self._initWidget()
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

        pass

    def _connect_to_slot(self):
        # 反向链接
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.PushButton_start_fishing.clicked.connect(self.start_fishing)

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
        self.run_fishing_thread.is_running_signal.connect(self.set_is_running)
        self.run_fishing_thread.start()

    def set_is_running(self, is_running):
        logger.debug(f"执行set_is_running:{is_running}")

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
