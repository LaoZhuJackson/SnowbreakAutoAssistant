import threading
import time

from PyQt5.QtWidgets import QFrame
from qfluentwidgets import InfoBar, SwitchButton

from app.modules.base_task.base_task import BaseTask
from app.modules.trigger.auto_f import AutoFModule
from app.modules.trigger.nita_auto_e import NitaAutoEModule
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
        self.SwitchButton_f.checkedChanged.connect(self.on_f_toggled)
        self.SwitchButton_e.checkedChanged.connect(self.on_e_toggled)

    def turn_off_e_switch(self, is_running):
        if not is_running:
            self.SwitchButton_e.setChecked(False)

    def turn_off_f_switch(self, is_running):
        if not is_running:
            self.SwitchButton_f.setChecked(False)

    def on_f_toggled(self, isChecked: bool):
        """
        采集f
        :param isChecked:
        :return:
        """
        if isChecked:
            self.f_thread = SubTask(AutoFModule)
            self.f_thread.is_running.connect(self.turn_off_f_switch)
            self.f_thread.start()
        else:
            if self.f_thread.run:
                self.f_thread.stop()
                InfoBar.success(
                    '自动按F',
                    '已关闭',
                    isClosable=True,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    '错误',
                    '游戏未打开',
                    isClosable=True,
                    duration=2000,
                    parent=self
                )

    def on_e_toggled(self, isChecked: bool):
        """
        妮塔e
        :param isChecked:
        :return:
        """
        if isChecked:
            self.nita_e_thread = SubTask(NitaAutoEModule)
            self.nita_e_thread.is_running.connect(self.turn_off_e_switch)
            self.nita_e_thread.start()
        else:
            if self.nita_e_thread.run:
                self.nita_e_thread.stop()
                InfoBar.success(
                    '妮塔自动E',
                    '已关闭',
                    isClosable=True,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    '错误',
                    '游戏未打开',
                    isClosable=True,
                    duration=2000,
                    parent=self
                )
