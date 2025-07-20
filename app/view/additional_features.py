import re
import sys
from functools import partial

import cv2
import numpy as np
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QFrame, QWidget, QLabel
from fuzzywuzzy import process
from qfluentwidgets import SpinBox, CheckBox, ComboBox, LineEdit, InfoBar, Slider, BodyLabel

from app.common.config import config
from app.common.logger import original_stdout, original_stderr
from app.common.signal_bus import signalBus
from app.common.style_sheet import StyleSheet
from app.common.utils import get_all_children
from app.modules.alien_guardian.alien_guardian import AlienGuardianModule
from app.modules.drink.drink import DrinkModule
from app.modules.fishing.fishing import FishingModule
from app.modules.jigsaw.jigsaw import JigsawModule
from app.modules.massaging.massaging import MassagingModule
from app.modules.maze.maze import MazeModule
from app.modules.routine_action.routine_action import ActionModule
from app.modules.water_bomb.water_bomb import WaterBombModule
from app.ui.additional_features_interface import Ui_additional_features
from app.view.base_interface import BaseInterface
from app.view.subtask import AdjustColor, SubTask


class Additional(QFrame, Ui_additional_features, BaseInterface):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['商店', '体力', '奖励']

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self.is_running_fish = False
        self.is_running_action = False
        self.is_running_jigsaw = False
        self.is_running_water_bomb = False
        self.is_running_alien_guardian = False
        self.is_running_maze = False
        self.is_running_massaging = False
        self.is_running_drink = False
        self.color_pixmap = None
        self.hsv_value = None
        self.jigsaw_solution_pixmap = None

        self._initWidget()
        self._load_config()
        self._connect_to_slot()

    def _initWidget(self):
        # 正向链接
        self.SegmentedWidget.addItem(self.page_fishing.objectName(), '钓鱼',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_fishing))
        self.SegmentedWidget.addItem(self.page_action.objectName(), '常规行动',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_action))
        self.SegmentedWidget.addItem(self.page_jigsaw.objectName(), '信源解析',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_jigsaw))
        self.SegmentedWidget.addItem(self.page_water_bomb.objectName(), '心动水弹',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_water_bomb))
        self.SegmentedWidget.addItem(self.page_alien_guardian.objectName(), '异星守护',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_alien_guardian))
        self.SegmentedWidget.addItem(self.page_maze.objectName(), '迷宫',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_maze))
        self.SegmentedWidget.addItem(self.page_massaging.objectName(), '按摩',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_massaging))
        self.SegmentedWidget.addItem(self.page_card.objectName(), '猜心对局',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_card))
        self.SegmentedWidget.setCurrentItem(self.page_fishing.objectName())
        self.stackedWidget.setCurrentIndex(0)
        self.ComboBox_fishing_mode.addItems(
            ["高性能（消耗性能高速判断，准确率高）", "低性能（超时自动拉杆，准确率较低）"])
        self.BodyLabel_tip_fish.setText(
            "### 提示\n* 为实现纯后台，现已不支持鼠标侧键\n* 钓鱼角色选择分析员，否则无法正常工作\n* 根据游戏右下角手动设置好抛竿按键、钓鱼次数和鱼饵类型后再点开始\n* 珍奇钓鱼点每天最多钓25次\n* 稀有钓鱼点每天最多钓50次\n* 普通钓鱼点无次数限制\n* 当一个钓鱼点钓完后需要手动移动到下一个钓鱼点，进入钓鱼界面后再启动一次\n* 当黄色块数异常时尝试上面的校准HSV，钓鱼出现圆环时点`校准颜色`，然后点黄色区域\n")
        self.BodyLabel_tip_action.setText(
            "### 提示\n* 自动完成常规行动，在看板娘页面点击开始\n* 重复刷指定次数实战训练第一关，不消耗体力\n* 用于完成凭证20次常规行动周常任务")
        self.BodyLabel_tip_jigsaw.setText(
            "### 提示\n* 本功能只提供解决方案，不自动拼\n* 需要手动输入当前拥有的各个拼图数量\n* 指定最大方案数越大，耗时越长，但可能会得到一个更优的方案,建议范围10~100\n* 设置过大方案数会产生卡顿\n* 生成的方案不是全局最优，而是目前方案数中的最优\n* 可以尝试降低9,10,11号碎片数量可能得到更优解\n* 当方案数量较少时，则应增加9,10,11号碎片数量")
        self.BodyLabel_tip_water.setText(
            "### 提示\n* 进入站在水弹入口位置后再点开始\n* 当无法识别道具或者生命时，适当调低上面两个置信度参数")
        self.BodyLabel_tip_alien.setText(
            "### 提示\n* 开始战斗后再点击开始\n* 常驻伙伴推荐带钢珠和炽热投手\n* 闯关模式为半自动一关一关打。需要手动开枪，手动选择下一关")
        self.BodyLabel_tip_maze.setText(
            "### 提示\n* 本功能只适用于增益迷宫（新迷宫），而非老迷宫\n* 运行模式中单次运行适合打前3关，重复运行则是一直刷最后一关\n* 进配队界面选好增益后再点击SAA的开始迷宫\n* 增益推荐配技能-爆电和护盾-夺取\n* 配队必须要有辰星-琼弦，且把角色放在中间位\n* 辅助有豹豹上豹豹防止暴毙")
        self.BodyLabel_tip_massaging.setText(
            "### 提示\n* 此功能还没开发完，不要使用\n* 使用本功能建议按摩等级大于等于4级")
        self.BodyLabel_tip_card.setText(
            "### 提示\n* 进入站在猜心对局入口位置后再点开始\n* 两种模式均无策略，目的均是为了快速结束对局刷下一把\n* 逻辑：有质疑直接质疑，轮到自己出牌时出中间的那一张\n* 实测有赢有输，挂着刷经验就行")
        # 设置combobox选项
        lure_type_items = ['万能鱼饵', '普通鱼饵', '豪华鱼饵', '至尊鱼饵', '重量级鱼类虫饵', '巨型鱼类虫饵',
                           '重量级鱼类夜钓虫饵', '巨型鱼类夜钓虫饵']
        run_items = ["切换疾跑", "按住疾跑"]
        mode_items = ["无尽模式", "闯关模式"]
        mode_maze_items = ["单次运行", "重复运行"]
        wife_items = ["凯茜娅", "肴", "芬妮", "里芙", "安卡希雅"]
        mode_card_items = ['标准模式（速刷经验）', '秘盒奇袭（刷经验成就）']
        self.ComboBox_run.addItems(run_items)
        self.ComboBox_lure_type.addItems(lure_type_items)
        self.ComboBox_mode.addItems(mode_items)
        self.ComboBox_mode_maze.addItems(mode_maze_items)
        self.ComboBox_wife.addItems(wife_items)
        self.ComboBox_card_mode.addItems(mode_card_items)

        self.update_label_color()
        # self.color_pixmap = self.generate_pixmap_from_hsv(hsv_value)
        # self.PixmapLabel.setStyleSheet()
        # self.PixmapLabel.setPixmap(self.color_pixmap)
        StyleSheet.ADDITIONAL_FEATURES_INTERFACE.apply(self)
        # 初始化拼图结果
        self.paint_best_solution([
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ])

    def _connect_to_slot(self):
        # 反向链接
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        # 按钮信号
        self.PushButton_start_fishing.clicked.connect(self.on_fishing_button_click)
        self.PushButton_start_action.clicked.connect(self.on_action_button_click)
        self.PushButton_start_jigsaw.clicked.connect(self.on_jigsaw_button_click)
        self.PushButton_start_water_bomb.clicked.connect(self.on_water_bomb_button_click)
        self.PushButton_start_alien_guardian.clicked.connect(self.on_alien_guardian_button_click)
        self.PushButton_start_maze.clicked.connect(self.on_maze_button_click)
        self.PushButton_start_massaging.clicked.connect(self.on_massaging_button_click)
        self.PushButton_start_drink.clicked.connect(self.on_drink_button_click)

        # 链接各种需要保存修改的控件
        self._connect_to_save_changed()

        self.PrimaryPushButton_get_color.clicked.connect(self.adjust_color)
        self.PushButton_reset.clicked.connect(self.reset_color)

        self.LineEdit_fish_key.editingFinished.connect(lambda: self.update_fish_key(self.LineEdit_fish_key.text()))

        signalBus.jigsawDisplaySignal.connect(self.paint_best_solution)
        signalBus.updatePiecesNum.connect(self.update_pieces_num)
        signalBus.updateFishKey.connect(self.update_fish_key)

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
                    if widget.objectName().split('_')[2] == 'key':
                        widget.setPlaceholderText("例如空格输入‘space’，置空则自动识别")
                    elif widget.objectName().split('_')[1] == 'fish':
                        widget.setPlaceholderText("“int,int,int”")
                    widget.setText(config_item.value)
                elif isinstance(widget, SpinBox):
                    widget.setValue(config_item.value)
                elif isinstance(widget, Slider):
                    widget.setValue(config_item.value)
                    text_name = 'BodyLabel_' + widget.objectName().split('_')[1] + '_' + widget.objectName().split('_')[
                        2]
                    text_widget = self.findChild(QLabel, name=text_name)
                    text_widget.setText(str(widget.value()))

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
            elif isinstance(children, LineEdit):
                children.editingFinished.connect(partial(self.save_changed, children))
            elif isinstance(children, Slider):
                children.valueChanged.connect(partial(self.save_changed, children))

    def save_changed(self, widget):
        if isinstance(widget, SpinBox):
            config.set(getattr(config, widget.objectName(), None), widget.value())
        elif isinstance(widget, CheckBox):
            config.set(getattr(config, widget.objectName(), None), widget.isChecked())
        elif isinstance(widget, LineEdit):
            # 如果是钓鱼相关的lineEdit
            if widget.objectName().split('_')[1] == 'fish':
                # 钓鱼按键
                if widget.objectName().split('_')[2] == 'key':
                    config.set(getattr(config, widget.objectName(), None), widget.text())
                else:
                    text = widget.text()
                    if self.is_valid_format(text):
                        config.set(getattr(config, widget.objectName(), None), text)
            elif widget.objectName().split('_')[1] == 'jigsaw':
                text = widget.text()
                if text == "-1":
                    text = "0"
                config.set(getattr(config, widget.objectName(), None), text)
        elif isinstance(widget, ComboBox):
            config.set(getattr(config, widget.objectName(), None), widget.currentIndex())
        elif isinstance(widget, Slider):
            config.set(getattr(config, widget.objectName(), 70), widget.value())
            text_name = 'BodyLabel_' + widget.objectName().split('_')[1] + '_' + widget.objectName().split('_')[2]
            text_widget = self.findChild(QLabel, name=text_name)
            text_widget.setText(str(widget.value()))

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())

    def is_valid_format(self, input_string):
        # 正则表达式匹配三个整数，用逗号分隔
        pattern = r'^(\d+),(\d+),(\d+)$'
        match = re.match(pattern, input_string)

        # 如果匹配成功，则继续检查数值范围
        if match:
            # 获取匹配到的三个整数,match.group(0)代表整个匹配的字符串
            int_values = [int(match.group(1)), int(match.group(2)), int(match.group(3))]

            # 检查每个整数是否在0~255之间
            if all(0 <= value <= 255 for value in int_values):
                return True
            else:
                self.logger.error("保存失败，int范围不在0~255之间")
        else:
            self.logger.error("保存失败，输入不符合“int,int,int”的格式")
        return False

    def update_label_color(self):
        """
        通过设置style的方式将颜色呈现在label上，这样可以随label缩放
        :return:
        """
        hsv_value = [int(value) for value in config.LineEdit_fish_base.value.split(",")]
        # 使用 OpenCV 将 HSV 转换为 BGR
        hsv_array = np.uint8([[[hsv_value[0], hsv_value[1], hsv_value[2]]]])
        bgr_color = cv2.cvtColor(hsv_array, cv2.COLOR_HSV2BGR)[0][0]
        # 将 BGR 转换为 RGB 格式
        rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])  # BGR to RGB
        # 将 RGB 转换为 #RRGGBB 格式的字符串
        rgb_color_str = f"#{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"
        # 使用 setStyleSheet 设置 QLabel 的背景颜色
        self.PixmapLabel.setStyleSheet(f"background-color: {rgb_color_str};border-radius: 5px;")

    def update_pieces_num(self, pieces_num: dict):
        try:
            for key, value in pieces_num.items():
                line_edit = self.SimpleCardWidget_jigsaw.findChildren(LineEdit, key)[0]
                line_edit.setText(str(value))
                line_edit.editingFinished.emit()
        except Exception as e:
            self.logger.error(e)

    def adjust_color(self):
        self.adjust_color_thread = AdjustColor()
        self.adjust_color_thread.color_changed.connect(self.reload_color_config)
        self.adjust_color_thread.start()

    def reload_color_config(self):
        self.LineEdit_fish_base.setText(config.LineEdit_fish_base.value)
        self.LineEdit_fish_upper.setText(config.LineEdit_fish_upper.value)
        self.LineEdit_fish_lower.setText(config.LineEdit_fish_lower.value)
        self.update_label_color()

    def reset_color(self):
        config.set(config.LineEdit_fish_base, config.LineEdit_fish_base.defaultValue)
        config.set(config.LineEdit_fish_upper, config.LineEdit_fish_upper.defaultValue)
        config.set(config.LineEdit_fish_lower, config.LineEdit_fish_lower.defaultValue)
        self.LineEdit_fish_base.setText(config.LineEdit_fish_base.value)
        self.LineEdit_fish_upper.setText(config.LineEdit_fish_upper.value)
        self.LineEdit_fish_lower.setText(config.LineEdit_fish_lower.value)
        self.update_label_color()

    def paint_best_solution(self, best_solution_board: list):
        def get_color_for_value(piece_id: int):
            """根据数组中的值返回相应的颜色"""
            if piece_id == 1:
                return QColor(169, 199, 218)
            elif piece_id == 2:
                return QColor(162, 164, 216)
            elif piece_id == 3:
                return QColor(119, 159, 193)
            elif piece_id == 4:
                return QColor(145, 200, 198)
            elif piece_id == 5:
                return QColor(181, 206, 156)
            elif piece_id == 6:
                return QColor(146, 191, 146)
            elif piece_id == 7:
                return QColor(180, 165, 132)
            elif piece_id == 8:
                return QColor(214, 217, 132)
            elif piece_id == 9:
                return QColor(216, 183, 205)
            elif piece_id == 10:
                return QColor(204, 139, 159)
            elif piece_id == 11:
                return QColor(156, 162, 198)
            elif piece_id == -1:
                return QColor(215, 226, 231)  # 不可用区域
            else:
                return QColor(170, 179, 186)

        def generate_pixmap():
            spacing = 5
            rows = len(best_solution_board)
            cols = len(best_solution_board[0])
            total_height = 400

            # 根据total_height计算每个小方块的高和宽
            tile_height = tile_width = (total_height - spacing * (rows - 1)) / rows
            total_width = tile_width * cols + spacing * (cols - 1)
            pixmap = QPixmap(int(total_width), int(total_height))
            pixmap.fill(QColor(228, 237, 245))  # 设置背景色为白色

            # 在 QPixmap 上绘制
            painter = QPainter(pixmap)
            for now in range(rows * cols):
                x, y = divmod(now, cols)
                value = best_solution_board[x][y]
                # 根据值选择颜色
                color = get_color_for_value(value)

                # 计算每个单元格的位置，考虑间隔
                x_pos = y * (tile_width + spacing)
                y_pos = x * (tile_height + spacing)

                rect = QRect(int(x_pos), int(y_pos), int(tile_width), int(tile_height))
                painter.fillRect(rect, color)
            painter.end()

            self.jigsaw_solution_pixmap = pixmap
            self.PixmapLabel_best_solution.setPixmap(self.jigsaw_solution_pixmap)

        generate_pixmap()

    def update_fish_key(self, key):
        # 添加模糊查询
        choices = ["ctrl", "space", "shift"]
        best_match = process.extractOne(key, choices)
        if best_match[1] > 60:
            key = best_match[0]
        self.LineEdit_fish_key.setText(key.lower())
        self.save_changed(self.LineEdit_fish_key)

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)

    def set_simple_card_enable(self, simple_card, enable: bool):
        children = get_all_children(simple_card)
        for child in children:
            if isinstance(child, CheckBox) or isinstance(child, LineEdit) or isinstance(child, SpinBox):
                child.setEnabled(enable)

    def on_fishing_button_click(self):
        """钓鱼开始按键的信号处理"""
        if not self.is_running_fish:
            self.redirectOutput(self.textBrowser_log_fishing)
            self.fishing_task = SubTask(FishingModule)
            self.fishing_task.is_running.connect(self.handle_fishing)
            self.fishing_task.start()
        else:
            self.fishing_task.stop()

    def handle_fishing(self, is_running):
        """钓鱼线程开始与结束的信号处理"""
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_fish, False)
            self.PushButton_start_fishing.setText('停止钓鱼')
            self.is_running_fish = True
        else:
            children = get_all_children(self.SimpleCardWidget_fish)
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, SpinBox):
                    child.setEnabled(True)
                elif isinstance(child, LineEdit):
                    if not child.objectName() == 'LineEdit_fish_base':
                        child.setEnabled(True)
            self.PushButton_start_fishing.setText('开始钓鱼')
            self.is_running_fish = False

    def on_action_button_click(self):
        """周常行动开始按键的信号处理"""
        if not self.is_running_action:
            self.redirectOutput(self.textBrowser_log_action)
            self.action_task = SubTask(ActionModule)
            self.action_task.is_running.connect(self.handle_action)
            self.action_task.start()
        else:
            self.action_task.stop()

    def handle_action(self, is_running):
        """周常行动线程开始与结束的信号处理"""
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_action, False)
            self.PushButton_start_action.setText("停止行动")
            self.is_running_action = True
        else:
            children = get_all_children(self.SimpleCardWidget_action)
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, SpinBox):
                    child.setEnabled(True)
                elif isinstance(child, LineEdit):
                    pass
            self.PushButton_start_action.setText("开始行动")
            self.is_running_action = False

    def on_jigsaw_button_click(self):
        if not self.is_running_jigsaw:
            self.redirectOutput(self.textBrowser_log_jigsaw)
            self.jigsaw_task = SubTask(JigsawModule)
            self.jigsaw_task.is_running.connect(self.handle_jigsaw)
            self.jigsaw_task.start()
        else:
            self.jigsaw_task.stop()

    def handle_jigsaw(self, is_running):
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_jigsaw, False)
            self.PushButton_start_jigsaw.setText("停止拼图")
            self.is_running_jigsaw = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_jigsaw, True)
            self.PushButton_start_jigsaw.setText("开始拼图")
            self.is_running_jigsaw = False

    def on_water_bomb_button_click(self):
        if not self.is_running_water_bomb:
            self.redirectOutput(self.textBrowser_log_water_bomb)
            self.water_bomb_task = SubTask(WaterBombModule)
            self.water_bomb_task.is_running.connect(self.handle_water_bomb)
            self.water_bomb_task.start()
        else:
            self.water_bomb_task.stop()

    def handle_water_bomb(self, is_running):
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_water_bomb, False)
            self.PushButton_start_water_bomb.setText('停止心动水弹')
            self.is_running_water_bomb = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_water_bomb, True)
            self.PushButton_start_water_bomb.setText('开始心动水弹')
            self.is_running_water_bomb = False

    def on_alien_guardian_button_click(self):
        if not self.is_running_alien_guardian:
            self.redirectOutput(self.textBrowser_log_alien_guardian)
            self.alien_guardian_task = SubTask(AlienGuardianModule)
            self.alien_guardian_task.is_running.connect(self.handle_alien_guardian)
            self.alien_guardian_task.start()
        else:
            self.alien_guardian_task.stop()

    def handle_alien_guardian(self, is_running):
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_alien_guardian, False)
            self.PushButton_start_alien_guardian.setText('停止异星守护')
            self.is_running_alien_guardian = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_alien_guardian, True)
            self.PushButton_start_alien_guardian.setText('开始异星守护')
            self.is_running_alien_guardian = False

    def on_maze_button_click(self):
        if not self.is_running_maze:
            self.redirectOutput(self.textBrowser_log_maze)
            self.maze_task = SubTask(MazeModule)
            self.maze_task.is_running.connect(self.handle_maze)
            self.maze_task.start()
        else:
            self.maze_task.stop()

    def handle_maze(self, is_running):
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_maze, False)
            self.PushButton_start_maze.setText('停止迷宫')
            self.is_running_maze = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_maze, True)
            self.PushButton_start_maze.setText('开始迷宫')
            self.is_running_maze = False

    def on_massaging_button_click(self):
        """钓鱼开始按键的信号处理"""
        if not self.is_running_massaging:
            self.redirectOutput(self.textBrowser_log_massaging)
            self.massaging_task = SubTask(MassagingModule)
            self.massaging_task.is_running.connect(self.handle_massaging)
            self.massaging_task.start()
        else:
            self.massaging_task.stop()

    def handle_massaging(self, is_running):
        """按摩线程开始与结束的信号处理"""
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_massaging, False)
            self.PushButton_start_massaging.setText('停止按摩')
            self.is_running_massaging = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_massaging, True)
            self.PushButton_start_massaging.setText('开始按摩')
            self.is_running_massaging = False

    def on_drink_button_click(self):
        """酒馆开始按键的信号处理"""
        if not self.is_running_drink:
            self.redirectOutput(self.textBrowser_log_drink)
            self.drink_task = SubTask(DrinkModule)
            self.drink_task.is_running.connect(self.handle_drink)
            self.drink_task.start()
        else:
            self.drink_task.stop()

    def handle_drink(self, is_running):
        """钓鱼线程开始与结束的信号处理"""
        if is_running:
            self.set_simple_card_enable(self.SimpleCardWidget_card, False)
            self.PushButton_start_drink.setText('停止喝酒')
            self.is_running_drink = True
        else:
            self.set_simple_card_enable(self.SimpleCardWidget_card, True)
            self.PushButton_start_drink.setText('开始喝酒')
            self.is_running_drink = False
