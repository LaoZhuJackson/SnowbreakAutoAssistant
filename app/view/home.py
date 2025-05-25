import re
import sys
from datetime import datetime
from functools import partial

import pyautogui
import win32con
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFrame, QWidget, QTreeWidgetItemIterator, QFileDialog
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition, CheckBox, ComboBox, ToolButton, LineEdit, \
    BodyLabel, ProgressBar

from app.common.config import config
from app.common.logger import original_stdout, original_stderr, logger
from app.common.signal_bus import signalBus
from app.common.style_sheet import StyleSheet
from app.common.utils import get_all_children, get_hwnd, get_date
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
    is_running_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()  # 添加停止信号

    def __init__(self, checkbox_dic):
        super().__init__()
        self.checkbox_dic = checkbox_dic
        self._is_running = True
        self.name_list_zh = ['自动登录', '领取物资', '商店购买', '刷体力', '人物碎片', '精神拟境', '领取奖励']

    def run(self):
        self.is_running_signal.emit('start')
        normal_stop_flag = True
        try:
            for key, value in self.checkbox_dic.items():
                if value:
                    index = int(re.search(r'\d+', key).group()) - 1
                    self.logger.info(f"当前任务：{self.name_list_zh[index]}")
                    if not self.init_auto('game'):
                        normal_stop_flag = False
                        break
                    self.auto.reset()
                    if index == 0:
                        module = EnterGameModule(self.auto, self.logger)
                        module.run()
                    elif index == 1:
                        module = CollectSuppliesModule(self.auto, self.logger)
                        module.run()
                    elif index == 2:
                        module = ShoppingModule(self.auto, self.logger)
                        module.run()
                    elif index == 3:
                        module = UsePowerModule(self.auto, self.logger)
                        module.run()
                    elif index == 4:
                        module = PersonModule(self.auto, self.logger)
                        module.run()
                    elif index == 5:
                        module = ChasmModule(self.auto, self.logger)
                        module.run()
                    elif index == 6:
                        module = GetRewardModule(self.auto, self.logger)
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
            if normal_stop_flag:
                self.is_running_signal.emit('end')
            else:
                # 未创建auto，没开游戏，提前结束
                self.is_running_signal.emit('no_auto')


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

        self.game_hwnd = None

        self._initWidget()
        self._connect_to_slot()
        self.redirectOutput(self.textBrowser_log)

        self.get_tips()

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
            "### 提示\n* 目前不支持从启动器开始，出现游戏窗口后再点助手的开始\n* 如果不是官服，先去设置那选服\n* 遇到版本更新，先更新活动公告链接，然后再去“刷体力”设置那更新“材料”和“深渊”位置后再运行")
        self.BodyLabel_person_tip.setText(
            "### 提示\n* 输入代号而非全名，比如想要刷“凯茜娅-朝翼”，就输入“朝翼”")
        self.PopUpAniStackedWidget.setCurrentIndex(0)
        self.TitleLabel_setting.setText("设置-" + self.setting_name_list[self.PopUpAniStackedWidget.currentIndex()])
        self.PushButton_start.setShortcut("F1")
        self.PushButton_start.setToolTip("快捷键：F1")

        self.gridLayout.addWidget(self.select_person, 1, 0)
        self.gridLayout.addWidget(self.select_weapon, 2, 0)

        self._load_config()
        # 和其他控件有相关状态判断的，要放在load_config后
        self.ComboBox_power_day.setEnabled(self.CheckBox_is_use_power.isChecked())
        self.PushButton_select_directory.setEnabled(self.CheckBox_auto_open_starter.isChecked())

        StyleSheet.HOME_INTERFACE.apply(self)
        # 使背景透明，适应主题
        self.ScrollArea.enableTransparentBackground()
        self.ScrollArea_tips.enableTransparentBackground()

    def _connect_to_slot(self):
        self.PushButton_start.clicked.connect(self.on_start_button_click)
        self.PushButton_select_all.clicked.connect(lambda: select_all(self.SimpleCardWidget_option))
        self.PushButton_no_select.clicked.connect(lambda: no_select(self.SimpleCardWidget_option))
        self.PushButton_select_directory.clicked.connect(self.on_select_directory_click)
        # 版本适配更新
        self.PushButton_update_stuff.clicked.connect(lambda: self.on_update_click('stuff'))
        self.PushButton_update_chasm.clicked.connect(lambda: self.on_update_click('chasm'))

        self.ToolButton_entry.clicked.connect(lambda: self.set_current_index(0))
        self.ToolButton_collect.clicked.connect(lambda: self.set_current_index(1))
        self.ToolButton_shop.clicked.connect(lambda: self.set_current_index(2))
        self.ToolButton_use_power.clicked.connect(lambda: self.set_current_index(3))
        self.ToolButton_person.clicked.connect(lambda: self.set_current_index(4))

        signalBus.sendHwnd.connect(self.set_hwnd)

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
                    widget.setText(str(config_item.value))
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

    def set_hwnd(self, hwnd):
        self.game_hwnd = hwnd

    def on_select_directory_click(self):
        """ 选择启动器路径 """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择启动器", config.LineEdit_starter_directory.value,
                                                   "Executable Files (*.exe);;All Files (*)")
        if not file_path or config.LineEdit_starter_directory.value == file_path:
            return
        self.LineEdit_starter_directory.setText(file_path)
        self.LineEdit_starter_directory.editingFinished.emit()

    def on_update_click(self, button_type):
        """
        版本更新适配
        :param button_type: 'stuff', 'chasm'
        :return:
        """
        if button_type == "stuff":
            x1 = config.LineEdit_stuff_x1.value
            y1 = config.LineEdit_stuff_y1.value
            x2 = config.LineEdit_stuff_x2.value
            y2 = config.LineEdit_stuff_y2.value
        else:
            x1 = config.LineEdit_chasm_x1.value
            y1 = config.LineEdit_chasm_y1.value
            x2 = config.LineEdit_chasm_x2.value
            y2 = config.LineEdit_chasm_y2.value
        if x2 < 0 or y2 < 0 or x1 < 0 or y1 < 0:
            InfoBar.error(
                title='更新位置出错',
                content="坐标位置需要大于等于0",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            return
        if x2 <= x1 or y2 <= y1:
            InfoBar.error(
                title='更新位置出错',
                content="右下角坐标数值需要大于左上角坐标数值",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            return
        # 获取屏幕分辨率
        screen_width, screen_height = pyautogui.size()
        if x1 > screen_width or x2 > screen_width or y1 > screen_height or y2 > screen_height:
            InfoBar.error(
                title='更新位置出错',
                content="坐标位置不能大于屏幕分辨率",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            return
        if button_type == "stuff":
            config.set(config.stuff_pos, (x1 / screen_width, y1 / screen_height, x2 / screen_width, y2 / screen_height))
        else:
            config.set(config.chasm_pos, (x1 / screen_width, y1 / screen_height, x2 / screen_width, y2 / screen_height))
        text = "材料" if button_type == "stuff" else "深渊"
        pos = config.stuff_pos.value if button_type == "stuff" else config.chasm_pos.value
        InfoBar.info(
            title=f'更新{text}位置成功',
            content=f"坐标更新为{pos}",
            orient=Qt.Horizontal,
            isClosable=True,  # disable close button
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

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
                self.redirectOutput(self.textBrowser_log)
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
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )

    def handle_start(self, str_flag):
        """设置按钮"""
        if str_flag == 'start':
            self.is_running = True
            self.set_checkbox_enable(False)
            self.PushButton_start.setText("停止")
        elif str_flag == 'end':
            self.is_running = False
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            # 后处理
            self.after_finish()
        elif str_flag == 'no_auto':
            self.is_running = False
            self.set_checkbox_enable(True)
            self.PushButton_start.setText("开始")
            InfoBar.error(
                title='未打开游戏',
                content="先打开游戏（不是启动器），再点击开始",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self
            )

    def after_finish(self):
        # 任务结束后的后处理
        if self.ComboBox_after_use.currentIndex() == 0:
            return
        elif self.ComboBox_after_use.currentIndex() == 1:
            if self.game_hwnd:
                win32gui.SendMessage(self.game_hwnd, win32con.WM_CLOSE, 0, 0)
            else:
                self.logger.warn('home未获取窗口句柄，无法关闭游戏')
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 2:
            self.parent.close()
        elif self.ComboBox_after_use.currentIndex() == 3:
            if self.game_hwnd:
                win32gui.SendMessage(self.game_hwnd, win32con.WM_CLOSE, 0, 0)
            else:
                self.logger.warn('home未获取窗口句柄，无法关闭游戏')

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
            # 对坐标进行数据转换处理
            if 'x1' in widget.objectName() or 'x2' in widget.objectName() or 'y1' in widget.objectName() or 'y2' in widget.objectName():
                config.set(getattr(config, widget.objectName(), None), int(widget.text()))
            else:
                config.set(getattr(config, widget.objectName(), None), widget.text())
            if widget.objectName() == 'LineEdit_link':
                self.get_tips()

    def save_item_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_person_{index}", None), False if check_state == 0 else True)

    def save_item2_changed(self, index, check_state):
        # print(index, check_state)
        config.set(getattr(config, f"item_weapon_{index}", None), False if check_state == 0 else True)

    def get_time_difference(self, date_due: str):
        """
        通过给入终止时间获取剩余时间差和时间百分比
        :param date_due: 持续时间，格式'03.06-04.17'
        :return:如果活动过期，则返回None,否则返回时间差，剩余百分比
        """
        current_year = datetime.now().year
        start_time = datetime.strptime(f"{current_year}.{date_due.split('-')[0]}", "%Y.%m.%d")
        end_time = datetime.strptime(f"{current_year}.{date_due.split('-')[1]}", "%Y.%m.%d")
        if end_time.month < start_time.month:
            end_time = datetime.strptime(f"{current_year + 1}.{date_due.split('-')[1]}", "%Y.%m.%d")
        # 获取当前日期和时间
        now = datetime.now()

        total_difference = end_time - start_time
        total_day = total_difference.days + 1
        if now < start_time:
            # 将当前日期替换成开始日期
            now = start_time
        time_difference = end_time - now
        days_remaining = time_difference.days + 1
        if days_remaining < 0:
            return 0, 0

        return days_remaining, (days_remaining / total_day) * 100, days_remaining == total_day

    def get_tips(self):
        tips_dic = get_date(config.LineEdit_link.value)
        if "error" in tips_dic.keys():
            logger.error("获取活动时间失败：" + tips_dic["error"])
            return
        for key, value in tips_dic.items():
            tips_dic[key] = self.get_time_difference(value)

        index = 0
        items_list = []
        try:
            for key, value in tips_dic.items():
                # 创建label
                BodyLabel_tip = BodyLabel(self.scrollAreaWidgetContents_tips)
                BodyLabel_tip.setObjectName(f"BodyLabel_tip_{index + 1}")
                # 创建进度条
                ProgressBar_tip = ProgressBar(self.scrollAreaWidgetContents_tips)
                ProgressBar_tip.setObjectName(f"ProgressBar_tip{index + 1}")
                if value[0] == 0:
                    BodyLabel_tip.setText(f"{key}已结束")
                else:
                    if value[2]:
                        BodyLabel_tip.setText(f"{key}未开始")
                    else:
                        BodyLabel_tip.setText(f"{key}剩余：{value[0]}天")
                ProgressBar_tip.setValue(int(value[1]))
                items_list.append([BodyLabel_tip, ProgressBar_tip, value[1]])

                index += 1
            items_list.sort(key=lambda x: x[2])
            for i in range(len(items_list)):
                self.gridLayout_tips.addWidget(items_list[i][0], i + 1, 0, 1, 1)
                self.gridLayout_tips.addWidget(items_list[i][1], i + 1, 1, 1, 1)

        except Exception as e:
            logger.error(f"更新控件出错：{e}")
            # self.logger.error(e)

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
