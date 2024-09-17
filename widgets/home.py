import os
import re
import subprocess
import sys
from functools import partial

import psutil
import pyautogui

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QWidget

from config.config import config
from ui.home_interface import Ui_home
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition, CheckBox, ComboBox, ToolButton

from utilities.logger import logger, stdout_stream, stderr_stream, original_stdout, original_stderr
from utilities.operation import back_to_home, move_to_then_click


def close_process(p1_pid):
    process = psutil.Process(p1_pid)
    # list children & kill them
    for c in process.children(recursive=True):
        c.kill()
    process.kill()


class StartThread(QThread):
    is_running_signal = pyqtSignal(bool)

    def __init__(self, checkbox_dic):
        super().__init__()
        self.checkbox_dic = checkbox_dic
        self._is_running = True
        self.name_list = ['enter_game.py', 'get_power.py', 'shopping.py', 'use_stamina.py', 'person.py', 'chasm.py',
                          'get_reward.py']
        self.name_list_zh = ['自动登录', '领取体力', '商店购买', '刷体力', '刷碎片', '刷深渊', '领取奖励']

    def run(self):
        self.is_running_signal.emit(True)
        try:
            for key, value in self.checkbox_dic.items():
                if value and self._is_running:
                    index = int(re.search(r'\d+', key).group()) - 1
                    logger.info(f"当前任务：{self.name_list_zh[index]}")
                    process = subprocess.Popen(['python', f'./modules/{self.name_list[index]}'], stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)
                    # 读取输出
                    while process.poll() is None:
                        line = process.stdout.readline()
                        result = line.decode('utf-8').strip('\r\n')
                        if result:
                            logger.info(result)
        except Exception as e:
            logger.error(e)
        finally:
            # 运行完成
            self.is_running_signal.emit(False)

    def stop_subprocess(self):
        self._is_running = False
        logger.info("已发送停止指令，等待剩余动作执行完成后停止")


def select_all(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(True)


def no_select(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(False)


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


class Home(QFrame, Ui_home):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['商店', '体力', '奖励']

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.is_running = False
        # self.start_thread = StartThread([])

        self._initWidget()
        self._connect_to_slot()
        self._redirectOutput()

    def _initWidget(self):
        for tool_button in self.SimpleCardWidget_option.findChildren(ToolButton):
            tool_button.setIcon(FIF.SETTING)

        self.ComboBox_after_use.setPlaceholderText("请选择")
        after_use_items = ['无动作', '退出游戏和代理', '退出代理', '退出游戏']
        self.ComboBox_after_use.addItems(after_use_items)
        self.ComboBox_power_day.setPlaceholderText("请选择")
        power_day_items = ['1', '2', '3', '4', '5', '6']
        self.ComboBox_power_day.addItems(power_day_items)

        self.PopUpAniStackedWidget.setCurrentIndex(0)

        self.TitleLabel_setting.setText("设置-" + self.setting_name_list[self.PopUpAniStackedWidget.currentIndex()])

        self._load_config()
        # 和其他控件有相关状态判断的，要放在load_config后
        self.ComboBox_power_day.setEnabled(self.CheckBox_is_use_power.isChecked())

    def _connect_to_slot(self):
        self.PushButton_start.clicked.connect(self.click_start)
        self.PushButton_select_all.clicked.connect(lambda: select_all(self.SimpleCardWidget_option))
        self.PushButton_no_select.clicked.connect(lambda: no_select(self.SimpleCardWidget_option))

        self.ToolButton_shop.clicked.connect(lambda: self.set_current_index(0))
        self.ToolButton_use_power.clicked.connect(lambda: self.set_current_index(1))
        self.ToolButton_reward.clicked.connect(lambda: self.set_current_index(2))

        self._connect_to_save_changed()

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

    def _load_config(self):
        config_data = config.load_config()
        for key, value in config_data.items():
            widget = self.findChild(QWidget, key)
            if widget:
                if isinstance(widget, CheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, ComboBox):
                    widget.setCurrentIndex(value)

    def _connect_to_save_changed(self):
        children_list = get_all_children(self)
        for children in children_list:
            # 此时不能用lambda，会使传参出错
            if isinstance(children, CheckBox):
                # children.stateChanged.connect(lambda: save_changed(children))
                children.stateChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, ComboBox):
                children.currentIndexChanged.connect(partial(self.save_changed, children))

    def click_start(self):
        checkbox_dic = {}
        for checkbox in self.SimpleCardWidget_option.findChildren(CheckBox):
            if checkbox.isChecked():
                checkbox_dic[checkbox.objectName()] = True
            else:
                checkbox_dic[checkbox.objectName()] = False
        if any(checkbox_dic.values()):
            # 对字典进行排序
            sorted_dict = dict(sorted(checkbox_dic.items(), key=lambda item: int(re.search(r'\d+', item[0]).group())))
            # logger.debug(sorted_dict)
            self.start_thread = StartThread(sorted_dict)
            self.start_thread.is_running_signal.connect(self.set_is_running)
            self.toggle_button()
        else:
            InfoBar.error(
                title='未勾选工作',
                content="需要至少勾选一项工作才能开始",
                orient=Qt.Horizontal,
                isClosable=False,  # disable close button
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def toggle_button(self):
        # logger.debug(self.is_running)
        if not self.is_running:
            self.start_thread.start()
            # self.is_running = True
            self.PushButton_start.setText("停止")
        else:
            self.start_thread.stop_subprocess()

    def set_is_running(self, is_running):
        logger.debug(f"执行set_is_running:{is_running}")
        self.is_running = is_running
        if is_running:
            self.set_checkbox_enable(False)
            self.PushButton_start.setText("停止")
        else:
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            if self.ComboBox_after_use.currentIndex() == 1:
                back_to_home()
                pyautogui.press('esc')
                move_to_then_click("images/in_game/yes.png")
                self.parent.close()
            elif self.ComboBox_after_use.currentIndex() == 2:
                self.parent.close()
            elif self.ComboBox_after_use.currentIndex() == 2:
                back_to_home()
                pyautogui.press('esc')
                move_to_then_click("images/in_game/yes.png")

    def set_checkbox_enable(self, enable: bool):
        for checkbox in self.findChildren(CheckBox):
            checkbox.setEnabled(enable)

    def set_current_index(self, index):
        try:
            self.TitleLabel_setting.setText("设置-" + self.setting_name_list[index])
            self.PopUpAniStackedWidget.setCurrentIndex(index)
        except Exception as e:
            logger.error(e)

    def save_changed(self, widget):
        # logger.debug(f"触发save_changed:{widget.objectName()}")
        # 当与配置相关的控件状态改变时调用此函数保存配置
        if isinstance(widget, CheckBox):
            config.set_value(widget.objectName(), widget.isChecked())
            if widget.objectName() == 'CheckBox_is_use_power':
                self.ComboBox_power_day.setEnabled(widget.isChecked())
        if isinstance(widget, ComboBox):
            config.set_value(widget.objectName(), widget.currentIndex())

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
