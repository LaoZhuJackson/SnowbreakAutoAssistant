import re
import sys
import time
import traceback
from datetime import datetime
from functools import partial

import psutil
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QWidget, QTreeWidgetItemIterator, QFileDialog
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition, CheckBox, ComboBox, ToolButton, LineEdit, \
    BodyLabel, ProgressBar

from ..common.config import config
from ..common.logger import logger, stdout_stream, stderr_stream, original_stdout, original_stderr
from ..common.setting import ACTIVITY_END_TIME, ACTIVITY_START_TIME, INTEREST_START_TIME, INTEREST_END_TIME, \
    MAZES_START_TIME, MAZES_END_TIME, ONLINE_CHALLENGE_START_TIME, ONLINE_CHALLENGE_END_TIME, BOSS_CHALLENGE_START_TIME, \
    BOSS_CHALLENGE_END_TIME, GAME_START_TIME, GAME_END_TIME, \
    UPPER_START_TIME, UPPER_END_TIME, BOTTOM_START_TIME, BOTTOM_END_TIME
from ..common.style_sheet import StyleSheet
from ..modules.automation import auto
from ..modules.chasm.chasm import ChasmModule
from ..modules.enter_game.enter_game import EnterGameModule
from ..modules.get_power.get_power import GetPowerModule
from ..modules.get_reward.get_reward import GetRewardModule
from ..modules.person.person import PersonModule
from ..modules.shopping.shopping import ShoppingModule
from ..modules.use_stamina.use_stamina import UseStaminaModule
from ..repackage.tree import TreeFrame_person, TreeFrame_weapon
from ..ui.home_interface import Ui_home


def close_process(p1_pid):
    process = psutil.Process(p1_pid)
    # list children & kill them
    for c in process.children(recursive=True):
        c.kill()
    process.kill()


class StartThread(QThread):
    is_running_signal = pyqtSignal(bool)
    stop_signal = pyqtSignal()  # 添加停止信号

    def __init__(self, checkbox_dic):
        super().__init__()
        self.checkbox_dic = checkbox_dic
        self._is_running = True
        self.name_list_zh = ['自动登录', '领取体力', '商店购买', '刷体力', '人物碎片', '精神拟境', '领取奖励']

    def run(self):
        self.is_running_signal.emit(True)
        try:
            logger.info("请确保游戏窗口分辨率是1920*1080，三秒后将自动激活窗口")
            time.sleep(3)
            auto.activate_window(config.LineEdit_game_name.value)
            for key, value in self.checkbox_dic.items():
                # print(f"value:{value}")
                # print(f"is_running:{is_running}")
                # logger.debug(f"是否正在运行：{is_running}")
                if value and is_running:
                    index = int(re.search(r'\d+', key).group()) - 1
                    logger.info(f"当前任务：{self.name_list_zh[index]}")
                    # 给每个任务增加时间间隔
                    time.sleep(2)
                    if index == 0:
                        module = EnterGameModule()
                        module.run()
                    elif index == 1:
                        module = GetPowerModule()
                        module.run()
                    elif index == 2:
                        module = ShoppingModule()
                        module.run()
                    elif index == 3:
                        module = UseStaminaModule()
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
                elif not is_running:
                    self.is_running_signal.emit(False)
                    logger.info("已退出")
                    break
                else:
                    # 如果value为false则进行下一个任务的判断
                    continue
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
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
        self.setting_name_list = ['登录', '商店', '体力', '碎片', '奖励']
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
        # self.start_thread = StartThread([])

        # self.logger = Logger(self.textBrowser_log)

        self.select_person = TreeFrame_person(parent=self.ScrollArea, enableCheck=True)
        self.select_weapon = TreeFrame_weapon(parent=self.ScrollArea, enableCheck=True)

        self._initWidget()
        self._connect_to_slot()
        self._redirectOutput()

    def _initWidget(self):
        for tool_button in self.SimpleCardWidget_option.findChildren(ToolButton):
            tool_button.setIcon(FIF.SETTING)

        # 设置combobox选项
        after_use_items = ['无动作', '退出游戏和代理', '退出代理', '退出游戏']
        power_day_items = ['1', '2', '3', '4', '5', '6']
        power_usage_items = ['活动材料本', '其他待开发']
        person_items = ["不选择", "凯茜娅-朝翼", "瑟瑞斯-瞬刻", "薇蒂雅-龙舌兰", "琴诺-悖谬", "里芙-无限之视",
                        "凯茜娅-蓝闪", "肴-冬至", "芬妮-辉耀", "安卡希雅-辉夜", "里芙-狂猎", "茉莉安-雨燕",
                        "芙提雅-缄默", "芬妮-咎冠", "恩雅-羽蜕", "伊切尔-豹豹", "苔丝-魔术师", "茉莉安-幽潮",
                        "晴-藏锋", "猫汐尔-溯影", "辰星-云篆"]
        self.ComboBox_after_use.addItems(after_use_items)
        self.ComboBox_power_day.addItems(power_day_items)
        self.ComboBox_power_usage.addItems(power_usage_items)
        self.ComboBox_c1.addItems(person_items)
        self.ComboBox_c2.addItems(person_items)
        self.ComboBox_c3.addItems(person_items)
        self.ComboBox_c4.addItems(person_items)

        self.BodyLabel_enter_tip.setText(
            "### 提示\n* 日志说没有找到截图窗口需要调整自己的窗口进程名\n* 不同服，不同启动器的进程名都不同\n* 打开任务管理器可查看进程名\n* 启动器进程名可能和游戏窗口进程名不同")
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
        self.PushButton_start.clicked.connect(self.click_start)
        self.PushButton_select_all.clicked.connect(lambda: select_all(self.SimpleCardWidget_option))
        self.PushButton_no_select.clicked.connect(lambda: no_select(self.SimpleCardWidget_option))
        self.PushButton_select_directory.clicked.connect(self.on_select_directory_click)

        self.ToolButton_entry.clicked.connect(lambda: self.set_current_index(0))
        self.ToolButton_shop.clicked.connect(lambda: self.set_current_index(1))
        self.ToolButton_use_power.clicked.connect(lambda: self.set_current_index(2))
        self.ToolButton_person.clicked.connect(lambda: self.set_current_index(3))
        self.ToolButton_reward.clicked.connect(lambda: self.set_current_index(4))

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
            self.start_thread.is_running_signal.connect(self.toggle_button)
            self.set_is_running()
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

    def on_select_directory_click(self):
        """ 选择启动器路径 """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择启动器", config.LineEdit_starter_directory.value,
                                                   "Executable Files (*.exe);;All Files (*)")
        if not file_path or config.LineEdit_starter_directory.value == file_path:
            return
        self.LineEdit_starter_directory.setText(file_path)
        self.LineEdit_starter_directory.editingFinished.emit()

    def set_is_running(self):
        """根据主进程中的self.is_running控制全局变量is_running"""
        # logger.debug(self.is_running)
        if not self.is_running:
            global is_running
            is_running = True
            self.start_thread.start()
            # self.is_running = True
            # self.PushButton_start.setText("停止")
        else:
            is_running = False
            logger.info("已发生停止指令，等待当前任务完成，下一个任务执行前停止")
            # self.start_thread.stop_signal.emit()

    def toggle_button(self, running):
        """设置按钮"""
        # 更新self.is_running,当再次点击开始按钮时，会执行set_is_running将全局变量设置为false
        self.is_running = running
        if running:
            self.set_checkbox_enable(False)
            self.PushButton_start.setText("停止")
        else:
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            if self.ComboBox_after_use.currentIndex() == 1:
                auto.press_key("esc")
                time.sleep(1)
                if auto.click_element("确定", "text", include=True, max_retries=5, action="move_click"):
                    self.parent.close()
            elif self.ComboBox_after_use.currentIndex() == 2:
                self.parent.close()
            elif self.ComboBox_after_use.currentIndex() == 2:
                auto.press_key("esc")
                time.sleep(1)
                auto.click_element("确定", "text", include=True, max_retries=5, action="move_click")

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

    def get_time_difference(self, end_time_str: str, total_day=None, start_time_str=None):
        """
        通过给入终止时间获取剩余时间差和时间百分比
        :param start_time_str: 开始时间，格式'2024-12-31'
        :param total_day: 持续总天数
        :param end_time_str: 结束时间，格式'2024-12-31'
        :return:如果活动过期，则返回None,否则返回时间差，剩余百分比
        """
        # 终止时间，可以根据需要修改。例如，假设你要设置为 2024 年 12 月 31 日。
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d')
        # 获取当前日期和时间
        now = datetime.now()
        # 如果输入了开始日期
        if start_time_str:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d')
            total_difference = end_time - start_time
            total_day = total_difference.days
            if now < start_time:
                # 将当前日期替换成开始日期
                now = start_time
        # print(end_time)
        # print(now)
        time_difference = end_time - now
        days_remaining = time_difference.days
        if days_remaining < 0:
            return 0, 0

        return days_remaining, (days_remaining / total_day) * 100

    def get_tips(self):
        tips_dic = {
            "活动": self.get_time_difference(ACTIVITY_END_TIME, start_time_str=ACTIVITY_START_TIME),
            "上半卡池": self.get_time_difference(UPPER_END_TIME, start_time_str=UPPER_START_TIME),
            "下半卡池": self.get_time_difference(BOTTOM_END_TIME, start_time_str=BOTTOM_START_TIME),
            "趣味关": self.get_time_difference(INTEREST_END_TIME, start_time_str=INTEREST_START_TIME),
            "迷宫": self.get_time_difference(MAZES_END_TIME, start_time_str=MAZES_START_TIME),
            "联机挑战": self.get_time_difference(ONLINE_CHALLENGE_END_TIME, start_time_str=ONLINE_CHALLENGE_START_TIME),
            "boss挑战": self.get_time_difference(BOSS_CHALLENGE_END_TIME, start_time_str=BOSS_CHALLENGE_START_TIME),
            "积分周常": self.get_time_difference(ONLINE_CHALLENGE_END_TIME, start_time_str=ONLINE_CHALLENGE_START_TIME),
            "勇者游戏": self.get_time_difference(GAME_END_TIME, start_time_str=GAME_START_TIME),
            "永续联战": self.get_time_difference(BOSS_CHALLENGE_END_TIME, start_time_str=BOSS_CHALLENGE_START_TIME),
        }
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
                    sorted_label_widgets[index].setText(f"{key}剩余：{value[0]}天")
                sorted_progress_widgets[index].setValue(value[1])
                index += 1
        except Exception as e:
            logger.error(e)

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
