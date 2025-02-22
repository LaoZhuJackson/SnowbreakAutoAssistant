import re
import sys
import time
import traceback
from datetime import datetime
from functools import partial

import win32con
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QWidget, QTreeWidgetItemIterator, QFileDialog
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition, CheckBox, ComboBox, ToolButton, LineEdit, \
    BodyLabel, ProgressBar

from app.common.config import config
from app.common.logger import stdout_stream, stderr_stream, logger, original_stdout, original_stderr
from app.common.style_sheet import StyleSheet
from app.common.utils import get_all_children
from app.modules.base_task.base_task import BaseTask
from app.modules.chasm.chasm import ChasmModule
from app.modules.collect_supplies.collect_supplies import CollectSuppliesModule
from app.modules.enter_game.enter_game import EnterGameModule
from app.modules.get_reward.get_reward import GetRewardModule
from app.modules.ocr import ocr
from app.modules.person.person import PersonModule
from app.modules.shopping.shopping import ShoppingModule
from app.modules.use_power.use_power import UsePowerModule
from app.repackage.tree import TreeFrame_person, TreeFrame_weapon
from app.ui.home_interface import Ui_home
from app.view.base_interface import BaseInterface


class StartThread(QThread, BaseTask):
    is_running_signal = pyqtSignal(bool)
    stop_signal = pyqtSignal()  # 添加停止信号

    def __init__(self, checkbox_dic):
        super().__init__()
        self.checkbox_dic = checkbox_dic
        self._is_running = True
        self.name_list_zh = ['自动登录', '领取体力', '商店购买', '刷体力', '人物碎片', '精神拟境', '领取奖励']

    def run(self):
        self.is_running_signal.emit(True)
        self.auto.reset()
        try:
            for key, value in self.checkbox_dic.items():
                if value:
                    index = int(re.search(r'\d+', key).group()) - 1
                    logger.info(f"当前任务：{self.name_list_zh[index]}")
                    if index == 0:
                        module = EnterGameModule()
                        module.run()
                    elif index == 1:
                        module = CollectSuppliesModule()
                        module.run()
                    elif index == 2:
                        module = ShoppingModule()
                        module.run()
                    elif index == 3:
                        module = UsePowerModule()
                        module.run()
                    elif index == 4:
                        module = PersonModule()
                        module.run()
                    elif index == 5:
                        module = ChasmModule()
                        module.run()
                    elif index == 6:
                        module = GetRewardModule()
                        module.run()
                else:
                    # 如果value为false则进行下一个任务的判断
                    continue
        except Exception as e:
            ocr.stop_ocr()
            self.logger.warn(e)
            # traceback.print_exc()
        finally:
            # 运行完成
            self.is_running_signal.emit(False)


def select_all(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(True)


def no_select(widget):
    # 遍历 widget 的所有子控件
    for checkbox in widget.findChildren(CheckBox):
        checkbox.setChecked(False)


class Home(QFrame, Ui_home, BaseInterface):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['登录', '物资', '商店', '体力', '碎片']
        self.person_dic = {
            "人物碎片": "item_person_0",
            "肴": "item_person_1",
            "安卡希雅": "item_person_2",
            "里芙": "item_person_3",
            "辰星": "item_person_4",
            "茉莉安": "item_person_5",
            "芬妮": "item_person_6",
            "芙提雅": "item_person_7",
            "瑟瑞斯": "item_person_8",
            "琴诺": "item_person_9",
            "猫汐尔": "item_person_10",
            "晴": "item_person_11",
            "恩雅": "item_person_12",
            "妮塔": "item_person_13",
        }
        self.weapon_dic = {
            "武器": "item_weapon_0",
            "彩虹打火机": "item_weapon_1",
            "草莓蛋糕": "item_weapon_2",
            "深海呼唤": "item_weapon_3",
        }

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.is_running = False
        self.select_person = TreeFrame_person(parent=self.ScrollArea, enableCheck=True)
        self.select_weapon = TreeFrame_weapon(parent=self.ScrollArea, enableCheck=True)

        self._initWidget()
        self._connect_to_slot()
        self.redirectOutput(self.textBrowser_log)

    def _initWidget(self):
        for tool_button in self.SimpleCardWidget_option.findChildren(ToolButton):
            tool_button.setIcon(FIF.SETTING)

        # 设置combobox选项
        after_use_items = ['无动作', '退出游戏和代理', '退出代理', '退出游戏']
        power_day_items = ['1', '2', '3', '4', '5', '6']
        power_usage_items = ['活动材料本', '其他待开发']
        self.ComboBox_after_use.addItems(after_use_items)
        self.ComboBox_power_day.addItems(power_day_items)
        self.ComboBox_power_usage.addItems(power_usage_items)
        self.LineEdit_c1.setPlaceholderText("未输入")
        self.LineEdit_c2.setPlaceholderText("未输入")
        self.LineEdit_c3.setPlaceholderText("未输入")
        self.LineEdit_c4.setPlaceholderText("未输入")

        self.BodyLabel_enter_tip.setText(
            "### 提示\n* 日志说没有找到截图窗口需要调整自己的窗口进程名\n* 不同服，不同启动器的进程名都不同\n* 打开任务管理器可查看进程名\n* 启动器进程名可能和游戏窗口进程名不同")
        self.BodyLabel_person_tip.setText(
            "### 提示\n* 输入代号而非全名，比如想要刷“凯茜娅-朝翼”，就输入“朝翼”")
        self.PopUpAniStackedWidget.setCurrentIndex(0)
        self.TitleLabel_setting.setText("设置-" + self.setting_name_list[self.PopUpAniStackedWidget.currentIndex()])
        self.get_tips()
        self.PushButton_start.setShortcut("F1")
        self.PushButton_start.setToolTip("快捷键：F1")

        # 查找 button1 在布局中的索引
        self.gridLayout.addWidget(self.select_person, 1, 0)
        self.gridLayout.addWidget(self.select_weapon, 2, 0)

        self._load_config()
        # 和其他控件有相关状态判断的，要放在load_config后
        self.ComboBox_power_day.setEnabled(self.CheckBox_is_use_power.isChecked())
        self.PushButton_select_directory.setEnabled(self.CheckBox_auto_open_starter.isChecked())

        StyleSheet.HOME_INTERFACE.apply(self)
        # 使背景透明，适应主题
        self.ScrollArea.enableTransparentBackground()

    def _connect_to_slot(self):
        self.PushButton_start.clicked.connect(self.on_start_button_click)
        self.PushButton_select_all.clicked.connect(lambda: select_all(self.SimpleCardWidget_option))
        self.PushButton_no_select.clicked.connect(lambda: no_select(self.SimpleCardWidget_option))
        self.PushButton_select_directory.clicked.connect(self.on_select_directory_click)

        self.ToolButton_entry.clicked.connect(lambda: self.set_current_index(0))
        self.ToolButton_collect.clicked.connect(lambda: self.set_current_index(1))
        self.ToolButton_shop.clicked.connect(lambda: self.set_current_index(2))
        self.ToolButton_use_power.clicked.connect(lambda: self.set_current_index(3))
        self.ToolButton_person.clicked.connect(lambda: self.set_current_index(4))

        self._connect_to_save_changed()

    def _load_config(self):
        for widget in self.findChildren(QWidget):
            # 动态获取 config 对象中与 widget.objectName() 对应的属性值
            config_item = getattr(config, widget.objectName(), None)
            if config_item:
                if isinstance(widget, CheckBox):
                    widget.setChecked(config_item.value)  # 使用配置项的值设置 CheckBox 的状态
                elif isinstance(widget, ComboBox):
                    # widget.setPlaceholderText("未选择")
                    widget.setCurrentIndex(config_item.value)
                elif isinstance(widget, LineEdit):
                    widget.setText(config_item.value)
        self._load_item_config()

    def _load_item_config(self):
        item = QTreeWidgetItemIterator(self.select_person.tree)
        while item.value():
            config_item = getattr(config, self.person_dic[item.value().text(0)], None)
            item.value().setCheckState(0, Qt.Checked if config_item.value else Qt.Unchecked)
            item += 1

        item2 = QTreeWidgetItemIterator(self.select_weapon.tree)
        while item2.value():
            config_item2 = getattr(config, self.weapon_dic[item2.value().text(0)], None)
            item2.value().setCheckState(0, Qt.Checked if config_item2.value else Qt.Unchecked)
            item2 += 1

    def _connect_to_save_changed(self):
        # 人物和武器的单独保存
        self.select_person.itemStateChanged.connect(self.save_item_changed)
        self.select_weapon.itemStateChanged.connect(self.save_item2_changed)

        children_list = get_all_children(self)
        for children in children_list:
            # 此时不能用lambda，会使传参出错
            if isinstance(children, CheckBox):
                # children.stateChanged.connect(lambda: save_changed(children))
                children.stateChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, ComboBox):
                children.currentIndexChanged.connect(partial(self.save_changed, children))
            elif isinstance(children, LineEdit):
                children.editingFinished.connect(partial(self.save_changed, children))

    def on_select_directory_click(self):
        """ 选择启动器路径 """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择启动器", config.LineEdit_starter_directory.value,
                                                   "Executable Files (*.exe);;All Files (*)")
        if not file_path or config.LineEdit_starter_directory.value == file_path:
            return
        self.LineEdit_starter_directory.setText(file_path)
        self.LineEdit_starter_directory.editingFinished.emit()

    def on_start_button_click(self):
        checkbox_dic = {}
        for checkbox in self.SimpleCardWidget_option.findChildren(CheckBox):
            if checkbox.isChecked():
                checkbox_dic[checkbox.objectName()] = True
            else:
                checkbox_dic[checkbox.objectName()] = False
        if any(checkbox_dic.values()):
            if not self.is_running:
                # 对字典进行排序
                sorted_dict = dict(
                    sorted(checkbox_dic.items(), key=lambda item: int(re.search(r'\d+', item[0]).group())))
                # logger.debug(sorted_dict)
                self.start_thread = StartThread(sorted_dict)
                self.start_thread.start()
                self.start_thread.is_running_signal.connect(self.handle_start)
            else:
                self.start_thread.stop()
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

    def handle_start(self, is_running):
        """设置按钮"""
        if is_running:
            self.is_running = True
            self.set_checkbox_enable(False)
            self.PushButton_start.setText("停止")
            self.start_thread.start()
            self.redirectOutput(self.textBrowser_log)
        else:
            self.is_running = False
            self.start_thread.stop()
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")

    def after_finish(self):
        # 任务结束后的后处理
        if self.ComboBox_after_use.currentIndex() == 1:
            win32gui.SendMessage(self.auto.hwnd, win32con.WM_CLOSE, 0, 0)
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 2:
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 3:
            win32gui.SendMessage(self.auto.hwnd, win32con.WM_CLOSE, 0, 0)

    def set_checkbox_enable(self, enable: bool):
        for checkbox in self.findChildren(CheckBox):
            checkbox.setEnabled(enable)

    def set_current_index(self, index):
        try:
            self.TitleLabel_setting.setText("设置-" + self.setting_name_list[index])
            self.PopUpAniStackedWidget.setCurrentIndex(index)
        except Exception as e:
            self.logger.error(e)

    def save_changed(self, widget):
        # logger.debug(f"触发save_changed:{widget.objectName()}")
        # 当与配置相关的控件状态改变时调用此函数保存配置
        if isinstance(widget, CheckBox):
            config.set(getattr(config, widget.objectName(), None), widget.isChecked())
            if widget.objectName() == 'CheckBox_is_use_power':
                self.ComboBox_power_day.setEnabled(widget.isChecked())
            elif widget.objectName() == 'CheckBox_auto_open_starter':
                self.PushButton_select_directory.setEnabled(widget.isChecked())
        elif isinstance(widget, ComboBox):
            config.set(getattr(config, widget.objectName(), None), widget.currentIndex())
        elif isinstance(widget, LineEdit):
            config.set(getattr(config, widget.objectName(), None), widget.text())

    def save_item_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_person_{index}", None), False if check_state == 0 else True)

    def save_item2_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_weapon_{index}", None), False if check_state == 0 else True)

    def get_time_difference(self, start_time_str: str, end_time_str: str):
        """
        通过给入终止时间获取剩余时间差和时间百分比
        :param start_time_str: 开始时间，格式'2024-12-31'
        :param end_time_str: 结束时间，格式'2024-12-31'
        :return:如果活动过期，则返回None,否则返回时间差，剩余百分比
        """
        # 终止时间，可以根据需要修改。例如，假设你要设置为 2024 年 12 月 31 日。
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d')
        # 获取当前日期和时间
        now = datetime.now()
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d')
        total_difference = end_time - start_time
        total_day = total_difference.days + 1
        if now < start_time:
            # 将当前日期替换成开始日期
            now = start_time
        # print(end_time)
        # print(now)
        time_difference = end_time - now
        days_remaining = time_difference.days + 1
        if days_remaining < 0:
            return 0, 0

        return days_remaining, (days_remaining / total_day) * 100, days_remaining == total_day

    def get_tips(self):
        tips_dic = {}
        config.set(config.date_tip, [
            ["活动", "2024-12-19", "2025-1-23"],
            ["豹豹卡池", "2024-12-19", "2025-1-9"],
            ["朝翼卡池", "2025-1-2", "2025-1-23"],
            ["噬神斗场", "2024-12-19", "2025-1-16"],
            ["心意寄语", "2024-12-31", "2025-1-14"],
            ["珍宝行囊", "2024-12-19", "2025-1-23"],
            ["七日派对", "2024-12-26", "2025-1-9"],
            ["远山沉沉", "2024-12-30", "2025-1-13"],
            ["永续联机", "2024-12-23", "2025-1-6"],
            ["禁区协议", "2025-1-6", "2025-1-20"],
        ])
        date_tip = config.date_tip.value
        for activity in date_tip:
            tips_dic[activity[0]] = self.get_time_difference(activity[1], activity[2])
        label_children = self.SimpleCardWidget_tips.findChildren(BodyLabel)
        progress_children = self.SimpleCardWidget_tips.findChildren(ProgressBar)
        sorted_label_widgets = sorted(label_children, key=lambda widget: int(widget.objectName().split('_')[-1]))
        sorted_progress_widgets = sorted(progress_children, key=lambda widget: int(widget.objectName().split('_')[-1]))

        index = 0
        # print(tips_dic['活动'])
        try:
            for key, value in tips_dic.items():
                # print(value)
                # print(type(value))
                if value[0] == 0:
                    sorted_label_widgets[index].setText(f"{key}已结束")
                else:
                    if value[2]:
                        sorted_label_widgets[index].setText(f"{key}未开始")
                    else:
                        sorted_label_widgets[index].setText(f"{key}剩余：{value[0]}天")
                sorted_progress_widgets[index].setValue(value[1])
                index += 1
        except Exception as e:
            self.logger.error(e)

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
