import threading
import time

from PyQt5.QtWidgets import QFrame
from qfluentwidgets import InfoBar

from app.modules.base_task.base_task import BaseTask
from app.modules.trigger.auto_f import AutoFModule
from app.ui.trigger_interface import Ui_trigger
from app.view.base_interface import BaseInterface
from app.view.subtask import SubTask


class Trigger(QFrame, Ui_trigger, BaseInterface):
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
        self.SwitchButton_1.checkedChanged.connect(self.on_f_toggled)

    def on_f_toggled(self, isChecked: bool):
        if isChecked:
            self.f_thread = SubTask(AutoFModule)
            self.f_thread.start()
            InfoBar.success(
                '自动按F',
                '已开启',
                isClosable=True,
                duration=2000,
                parent=self
            )
        else:
            self.f_thread.stop()
            InfoBar.success(
                '自动按F',
                '已关闭',
                isClosable=True,
                duration=2000,
                parent=self
            )
