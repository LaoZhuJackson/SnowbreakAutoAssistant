import threading
import time

from PyQt5.QtWidgets import QFrame
from qfluentwidgets import InfoBar

from app.modules.automation import auto
from app.ui.trigger_interface import Ui_trigger


class Trigger(QFrame, Ui_trigger):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.collect_thread = None
        self.collect_thread_running = False

        self._initWidget()
        self._connect_to_slot()

    def _initWidget(self):
        pass

    def _connect_to_slot(self):
        self.checkBox.toggled.connect(self.on_f_toggled)

    def on_f_toggled(self, checked):
        # 线程的目标函数
        def perform_action():
            while self.collect_thread_running:
                if auto.find_element("app/resource/images/fishing/collect.png", "image", threshold=0.7,
                                     crop=(1506 / 1920, 684 / 1080, 41 / 1920, 47 / 1080)):
                    auto.press_key("f")

        # 启动线程
        def start_thread():
            if not self.collect_thread_running:
                self.collect_thread_running = True
                self.collect_thread = threading.Thread(target=perform_action, daemon=True)
                self.collect_thread.start()

        # 停止线程
        def stop_thread():
            if self.collect_thread_running:
                self.collect_thread_running = False
                if self.collect_thread:
                    self.collect_thread.join()  # 等待线程安全退出
                self.collect_thread = None

        if checked:
            start_thread()
            InfoBar.success(
                '自动按F',
                '已开启',
                isClosable=True,
                duration=2000,
                parent=self
            )
        else:
            stop_thread()
            InfoBar.success(
                '自动按F',
                '已关闭',
                isClosable=True,
                duration=2000,
                parent=self
            )
