import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import win32gui
from app.common.config import config
from app.common.logger import logger
from app.modules.base_task.base_task import BaseTask
from app.modules.ocr import ocr


class SubTask(QThread, BaseTask):
    is_running = pyqtSignal(bool)

    def __init__(self, module):
        super().__init__()
        self.run = False  # 用于判断是否正常结束
        if not self.init_auto('game'):
            return
        self.logger = logger
        self.module = module(self.auto, self.logger)

    def run(self):
        if self.auto:
            self.auto.reset()
            self.is_running.emit(True)
            self.run = True
            try:
                self.module.run()
            except Exception as e:
                # print(traceback.format_exc())
                # 停止时清除ocr缓存
                ocr.stop_ocr()
                self.logger.warn(f"SubTask：{e}")
            self.is_running.emit(False)
        else:
            # 传输信号关闭开关
            self.is_running.emit(False)


class AdjustColor(QThread, BaseTask):
    color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.hsv_value = None
        self.logger = logger

    def run(self):
        if not self.init_auto('game'):
            self.logger.error("AdjustColor获取auto失败")
            return
        self.auto.take_screenshot()
        img_np = self.auto.get_crop_form_first_screenshot(crop=(1130 / 1920, 240 / 1080, 1500 / 1920, 570 / 1080),
                                                          is_resize=False)
        # 显示图像并让用户点击选择一个点
        cv2.imshow("Select yellow area", img_np)
        self.logger.info("请点击图像上的黄色完美收杆区域，选择后按任意键关闭。")
        cv2.setMouseCallback("Select yellow area", self.pick_color, img_np)
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
