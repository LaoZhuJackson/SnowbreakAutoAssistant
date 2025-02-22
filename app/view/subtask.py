import sys

import cv2
import numpy as np
import win32gui
from PyQt5.QtCore import QThread, pyqtSignal

from app.common.config import config
from app.common.logger import logger, original_stdout, original_stderr
from app.modules.automation.automation import instantiate_automation
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class SubTask(QThread, BaseTask):
    is_running = pyqtSignal(bool)

    def __init__(self, module):
        super().__init__()
        self.module = module()
        self.logger = logger
        self.chose_auto()

    def run(self):
        self.auto.reset()
        self.is_running.emit(True)
        try:
            self.module.run()
        except Exception as e:
            self.logger.warn(e)
        self.is_running.emit(False)


class AdjustColor(QThread):
    color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.hsv_value = None
        self.logger = logger
        self.auto = None
        self.chose_auto()

    def run(self):
        self.auto.take_screenshot()
        img_np = self.auto.get_crop_form_first_screenshot(crop=(1130 / 1920, 240 / 1080, 1500 / 1920, 570 / 1080),
                                                          is_resize=False)
        # 显示图像并让用户点击选择一个点
        cv2.imshow("Select yellow area", img_np)
        self.logger.info("请点击图像上的黄色完美收杆区域，选择后按任意键关闭。")
        cv2.setMouseCallback("Select yellow area", self.pick_color, img_np)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def chose_auto(self, only_game=False):
        """
        自动选择auto，有游戏窗口时选游戏，没有游戏窗口时选启动器，都没有的时候循环，寻找频率1次/s
        :return:
        """
        timeout = Timer(20).start()
        while True:
            # 每次循环重新导入
            from app.modules.automation.automation import auto_starter, auto_game
            if win32gui.FindWindow(None, config.LineEdit_game_name.value) or only_game:
                if not auto_game:
                    instantiate_automation(auto_type='game')  # 尝试实例化 auto_game
                self.auto = auto_game
                flag = 'game'
            else:
                if not auto_starter:
                    instantiate_automation(auto_type='starter')  # 尝试实例化 auto_starter
                self.auto = auto_starter
                flag = 'starter'
            if self.auto:
                return flag
            if timeout.reached():
                logger.error("获取auto超时")
                break

    def pick_color(self, event, x, y, flags, image):
        """鼠标回调函数，用于从用户点击的位置提取颜色"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # 获取点击点的颜色
            bgr_color = image[y, x]
            # 将BGR转换为HSV
            hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)
            # 是个NumPy数组
            self.hsv_value = hsv_color[0][0]
            self.logger.info(f"选定的HSV值: {self.hsv_value}")
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
