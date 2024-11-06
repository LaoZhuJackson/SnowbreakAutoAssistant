import re
import sys
import time
import traceback
from functools import partial
from typing import Union

import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal, QRect
from PyQt5.QtGui import QColor, QPixmap, QPainter
from PyQt5.QtWidgets import QFrame, QWidget, QTextBrowser
from qfluentwidgets import SpinBox, CheckBox, ComboBox, LineEdit, InfoBar

from app.common.config import config
from app.common.logger import logger, stdout_stream, stderr_stream, original_stdout, original_stderr
from app.common.ppOCR import ocr
from app.common.signal_bus import signalBus
from app.common.style_sheet import StyleSheet
from app.modules.automation import auto
from app.modules.automation.screenshot import Screenshot
from app.modules.fishing.fishing import FishingModule
from app.modules.jigsaw.jigsaw import JigsawModule
from app.modules.routine_action.routine_action import ActionModule
from app.ui.additional_features_interface import Ui_additional_features


class SubTask(QThread):
    is_running = pyqtSignal(bool)

    def __init__(self, module):
        super().__init__()
        self.module = module()

    def run(self):
        self.is_running.emit(True)
        logger.info("请确保游戏窗口分辨率是1920*1080，三秒后将自动激活窗口")
        time.sleep(3)
        auto.activate_window(config.LineEdit_game_name.value)
        try:
            self.sub_task()
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
        finally:
            self.is_running.emit(False)

    def sub_task(self):
        pass


class RunFishing(SubTask):
    def __init__(self):
        super().__init__(FishingModule)

    def sub_task(self):
        for i in range(config.SpinBox_fish_times.value):
            # print(f"is_running_fishing:{fish_running}")
            if not fish_running:
                break
            logger.info(f"开始第 {i + 1} 次钓鱼")
            if config.ComboBox_fishing_mode.value == 0:
                self.module.run()
            else:
                self.module.run_low_performance()


class RunAction(SubTask):

    def __init__(self):
        super().__init__(ActionModule)

    def sub_task(self):
        # 进入训练界面
        self.module.enter_train()
        # 开始循环
        for i in range(config.SpinBox_action_times.value):
            # print(f"is_running_action:{fish_running}")
            if not action_running:
                break
            logger.info(f"开始第 {i + 1} 次行动")
            self.module.run()
        # 返回主页面
        auto.back_to_home()


class RunJigsaw(SubTask):
    def __init__(self):
        super().__init__(JigsawModule)
        self.config_data = config.toDict()
        self.piece_counts = self.config_data["pieces_num"]

    def update_pieces_num(self):
        def get_window(title):
            """
            获取窗口
            :param title: 窗口名
            :return:
            """
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                return window
            return False

        def find_num(pos):
            window = get_window(config.LineEdit_game_name.value)
            left, top, _, _ = Screenshot.get_window_region(window)
            offset = (-36, 40)
            pos = (pos[0] - left + offset[0], pos[1] - top + offset[1])
            width = 40
            height = 50
            crop = ((pos[0] - width) / 1920, pos[1] / 1080, width / 1920, height / 1080)
            num = None
            try:
                screenshot, screenshot_pos, screenshot_scale_factor = Screenshot.take_screenshot(
                    config.LineEdit_game_name.value, crop=crop)
                ocr_result = ocr.recognize_multi_lines(np.array(screenshot))
                # print(f"{ocr_result=}")
                if not ocr_result:
                    logger.debug(f"未识别出任何文字")
                    # screenshot.show()
                    # input("回车继续")
                else:
                    num = int(ocr_result[0][1][0])
            except Exception as e:
                logger.error(f"OCR识别失败：{e}")
            return num

        for i in range(1, 12):
            key_name = "LineEdit_jigsaw_piece_" + str(i)
            if i == 1:
                # 只有第一次需要ocr截图
                source = auto.click_element(f"app/resource/images/jigsaw/piece_{i}_0.png", "image", threshold=0.7,
                                            crop=(76 / 1920, 128 / 1080, 338 / 1920, 855 / 1080), action="move")
            else:
                source = auto.click_element(f"app/resource/images/jigsaw/piece_{i}_0.png", "image", threshold=0.7,
                                            crop=(76 / 1920, 128 / 1080, 338 / 1920, 855 / 1080), action="move",
                                            need_ocr=False)
            if source:
                mouse_position = pyautogui.position()
                source_pos = (mouse_position.x, mouse_position.y)
                # print(f"{source_pos=}")
                piece_num = find_num(source_pos)
                # print(f"{text=}")
                if piece_num:
                    self.piece_counts[key_name] = int(piece_num)
                else:
                    self.piece_counts[key_name] = -1
                    InfoBar.error(
                        'OCR未正确识别',
                        f'{key_name}号碎片数量未正确识别，请手动输入并取消自动识别后再点击‘开始拼图’',
                        isClosable=True,
                        duration=-1,
                        parent=self
                    )
            else:
                self.piece_counts[key_name] = 0
        # print(self.piece_counts)
        signalBus.updatePiecesNum.emit(self.piece_counts)

    def sub_task(self):
        if config.CheckBox_auto_update_pieces_num.value:
            try:
                self.update_pieces_num()
            except Exception as e:
                traceback.print_exc()
        self.module.run()


class AdjustColor(QThread):
    color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.hsv_value = None

    def run(self):
        rgb_image, _, _ = auto.take_screenshot(crop=(1130 / 1920, 240 / 1080, 370 / 1920, 330 / 1080))
        # 转换为NumPy数组
        img_np = np.array(rgb_image)
        # 从RGB格式转换为BGR格式（OpenCV使用BGR）
        bgr_image = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        # 显示图像并让用户点击选择一个点
        cv2.imshow("Select yellow area", bgr_image)
        logger.info("请点击图像上的黄色完美收杆区域，选择后按任意键关闭。")
        cv2.setMouseCallback("Select yellow area", self.pick_color, bgr_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def pick_color(self, event, x, y, flags, image):
        """鼠标回调函数，用于从用户点击的位置提取颜色"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # 获取点击点的颜色
            bgr_color = image[y, x]
            # 将BGR转换为HSV
            hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)
            # 是个NumPy数组
            self.hsv_value = hsv_color[0][0]
            logger.info(f"选定的HSV值: {self.hsv_value}")
            self.save_color_to_config()
            self.color_changed.emit()

    def save_color_to_config(self):
        hue, sat, val = self.hsv_value
        lower_yellow = np.array([max(hue - 2, 0), max(sat - 35, 0), max(val - 10, 0)])
        upper_yellow = np.array([min(hue + 2, 179), min(sat + 35, 255), min(val + 10, 255)])
        base = f"{hue},{sat},{val}"
        upper = f"{upper_yellow[0]},{upper_yellow[1]},{upper_yellow[2]}"
        lower = f"{lower_yellow[0]},{lower_yellow[1]},{lower_yellow[2]}"
        config.set(config.LineEdit_fish_base, base)
        config.set(config.LineEdit_fish_upper, upper)
        config.set(config.LineEdit_fish_lower, lower)


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
        self.is_running_action = False
        self.is_running_jigsaw = False
        self.color_pixmap = None
        self.hsv_value = None
        self.jigsaw_solution_pixmap = None

        self._initWidget()
        self._load_config()
        self._connect_to_slot()
        # self._redirectOutput()

    def _initWidget(self):
        # 正向链接
        self.SegmentedWidget.addItem(self.page_fishing.objectName(), '自动钓鱼',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_fishing))
        self.SegmentedWidget.addItem(self.page_action.objectName(), '自动常规行动',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_action))
        self.SegmentedWidget.addItem(self.page_jigsaw.objectName(), '自动信源解析',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_jigsaw))
        self.SegmentedWidget.setCurrentItem(self.page_fishing.objectName())
        self.stackedWidget.setCurrentIndex(0)
        self.ComboBox_fishing_mode.addItems(
            ["高性能（cpu性能足够时使用，准确率高）", "低性能（检测频率较低时使用，准确率较低）"])
        self.BodyLabel_tip_fish.setText(
            "### 提示\n* 珍奇钓鱼点每天最多钓25次\n* 稀有钓鱼点每天最多钓50次\n* 普通钓鱼点无次数限制\n* 当一个钓鱼点钓完后需要手动移动到下一个钓鱼点，进入钓鱼界面后再启动一次\n* 当黄色块数异常时尝试上面的校准HSV，钓鱼出现圆环时点`校准颜色`，然后点黄色区域\n")
        self.BodyLabel_tip_action.setText(
            "### 提示\n自动完成常规行动\n* 不消耗体力\n* 重复刷指定次数实战训练第一关\n* 用于完成凭证20次常规行动周常任务")
        self.BodyLabel_tip_jigsaw.setText(
            "### 提示\n* 指定最大方案数越大，耗时越长，但可能会得到一个更优的方案,建议范围10~100\n* 设置过大方案数会产生卡顿\n* 生成的方案不是全局最优，而是目前方案数中的最优\n* 可以尝试降低9,10,11号碎片数量可能得到更优解\n* 当方案数量较少时，则应增加9,10,11号碎片数量\n* 使用自动获取碎片数量需要保证所有碎片没有被旋转过（如果旋转过就重新进一次信源解析界面）")

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
                    if widget.objectName().split('_')[1] == 'fish':
                        widget.setPlaceholderText("“int,int,int”")
                    widget.setText(config_item.value)
                elif isinstance(widget, SpinBox):
                    widget.setValue(config_item.value)

    def _connect_to_slot(self):
        # 反向链接
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

        self.PushButton_start_fishing.clicked.connect(self.start_fishing)
        self.PushButton_start_action.clicked.connect(self.start_action)
        self.PushButton_start_jigsaw.clicked.connect(self.start_jigsaw)

        # 链接各种需要保存修改的控件
        self._connect_to_save_changed()

        self.PrimaryPushButton_get_color.clicked.connect(self.adjust_color)
        self.PushButton_reset.clicked.connect(self.reset_color)

        signalBus.jigsawDisplaySignal.connect(self.paint_best_solution)
        signalBus.updatePiecesNum.connect(self.update_pieces_num)

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

    def _redirectOutput(self, log_widget):
        # 普通输出
        sys.stdout = stdout_stream
        # 报错输出
        sys.stderr = stderr_stream
        # 先断开可能存在的所有连接
        try:
            stdout_stream.message.disconnect()
            stderr_stream.message.disconnect()
        except TypeError:
            pass  # 没有连接存在时会抛出TypeError
        # 将新消息信号连接到对应输出位置
        stdout_stream.message.connect(lambda message: self.__updateDisplay(message, log_widget))
        stderr_stream.message.connect(lambda message: self.__updateDisplay(message, log_widget))

    def __updateDisplay(self, message, log_widget: QTextBrowser):
        # 将消息添加到 textBrowser，自动识别 HTML
        log_widget.insertHtml(message)
        log_widget.insertPlainText('\n')  # 为下一行消息留出空间
        log_widget.ensureCursorVisible()  # 滚动到最新消息

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())

    #######################钓鱼########################################
    def start_fishing(self):
        self._redirectOutput(self.textBrowser_log_fishing)
        self.run_fishing_thread = RunFishing()
        self.run_fishing_thread.is_running.connect(self.toggle_fish_button)
        self.set_fish_running()

    def toggle_fish_button(self, running):
        # logger.debug(f"执行set_is_running:{fish_running}")
        self.is_running_fish = running
        children = get_all_children(self.SimpleCardWidget_fish)
        if running:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, LineEdit) or isinstance(child, SpinBox):
                    child.setEnabled(False)
            self.PushButton_start_fishing.setText("停止钓鱼")
        else:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, SpinBox):
                    child.setEnabled(True)
                elif isinstance(child, LineEdit):
                    if not child.objectName() == 'LineEdit_fish_base':
                        child.setEnabled(True)
            self.PushButton_start_fishing.setText("开始钓鱼")

    def set_fish_running(self):
        if not self.is_running_fish:
            global fish_running
            fish_running = True
            self.run_fishing_thread.start()
        else:
            fish_running = False
            logger.info("已发生停止指令，等待当前钓鱼完成")

    #######################周常########################################
    def start_action(self):
        self._redirectOutput(self.textBrowser_log_action)
        self.run_action_thread = RunAction()
        self.run_action_thread.is_running.connect(self.toggle_action_button)
        self.set_action_running()

    def toggle_action_button(self, running):
        # logger.debug(f"执行set_is_running:{fish_running}")
        self.is_running_action = running
        children = get_all_children(self.SimpleCardWidget_action)
        if running:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, LineEdit) or isinstance(child, SpinBox):
                    child.setEnabled(False)
            self.PushButton_start_action.setText("停止行动")
        else:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, SpinBox):
                    child.setEnabled(True)
                elif isinstance(child, LineEdit):
                    pass
            self.PushButton_start_action.setText("开始行动")

    def set_action_running(self):
        if not self.is_running_action:
            global action_running
            action_running = True
            self.run_action_thread.start()
        else:
            action_running = False
            logger.info("已发生停止指令，等待当前行动完成")

    #######################拼图########################################
    def start_jigsaw(self):
        self._redirectOutput(self.textBrowser_log_jigsaw)
        self.run_jigsaw_thread = RunJigsaw()
        self.run_jigsaw_thread.is_running.connect(self.toggle_jigsaw_button)
        self.set_jigsaw_running()

    def toggle_jigsaw_button(self, running):
        # logger.debug(f"执行set_is_running:{fish_running}")
        self.is_running_jigsaw = running
        children = get_all_children(self.SimpleCardWidget_jigsaw)
        if running:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, LineEdit) or isinstance(child, SpinBox):
                    child.setEnabled(False)
            self.PushButton_start_jigsaw.setText("停止拼图")
        else:
            for child in children:
                if isinstance(child, CheckBox) or isinstance(child, LineEdit) or isinstance(child, SpinBox):
                    child.setEnabled(True)
            self.PushButton_start_jigsaw.setText("开始拼图")

    def set_jigsaw_running(self):
        if not self.is_running_jigsaw:
            global jigsaw_running
            jigsaw_running = True
            self.run_jigsaw_thread.start()
        else:
            jigsaw_running = False
            logger.info("已发生停止指令，等待当前行动完成")

    def save_changed(self, widget):
        if isinstance(widget, SpinBox):
            config.set(getattr(config, widget.objectName(), None), widget.value())
        elif isinstance(widget, CheckBox):
            config.set(getattr(config, widget.objectName(), None), widget.isChecked())
        elif isinstance(widget, LineEdit):
            # 如果是钓鱼相关的lineEdit
            if widget.objectName().split('_')[1] == 'fish':
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
                logger.error("保存失败，int范围不在0~255之间")
        else:
            logger.error("保存失败，输入不符合“int,int,int”的格式")
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
            pixmap = QPixmap(total_width, total_height)
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

                rect = QRect(x_pos, y_pos, tile_width, tile_height)
                painter.fillRect(rect, color)
            painter.end()

            self.jigsaw_solution_pixmap = pixmap
            self.PixmapLabel_best_solution.setPixmap(self.jigsaw_solution_pixmap)

        generate_pixmap()

    def update_pieces_num(self, pieces_num: dict):
        try:
            for key, value in pieces_num.items():
                line_edit = self.SimpleCardWidget_jigsaw.findChildren(LineEdit, key)[0]
                line_edit.setText(str(value))
                line_edit.editingFinished.emit()
        except Exception as e:
            logger.error(e)
            traceback.print_exc()

    def closeEvent(self, event):
        # 恢复原始标准输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        super().closeEvent(event)
