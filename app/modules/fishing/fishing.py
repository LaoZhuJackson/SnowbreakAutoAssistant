import os
import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui

from app.common.config import config
from app.common.logger import logger
from app.modules.automation import auto


class FishingModule:
    def __init__(self):
        self.previous_yellow_block_count = 0
        self.previous_pixels = 0
        self.save_path = os.path.abspath("./fish")
        self.is_use_time_judge = config.CheckBox_is_limit_time.value
        self.upper_yellow = np.array([int(value) for value in config.LineEdit_fish_upper.value.split(',')])
        self.lower_yellow = np.array([int(value) for value in config.LineEdit_fish_lower.value.split(',')])
        self.start_time = time.time()

    def run(self):
        if np.any(self.upper_yellow < self.lower_yellow):
            logger.error("运行错误，存在上限的值小于下限")
            return
        if auto.click_element("app/resource/images/fishing/fishing_rod.png", "image", max_retries=2,
                              action="move_click"):
            # 如果点击了还没反应则尝试用空格激活钓鱼
            if not auto.find_element("app/resource/images/fishing/wait_fish.png", "image", threshold=0.6):
                auto.press_key("space")
            if auto.find_element("app/resource/images/fishing/bite.png", "image", threshold=0.7,scale_range=(0.6,1.5), max_retries=10):
                auto.press_key("space", wait_time=0)
                if self.is_use_time_judge:
                    self.start_time = time.time()
                while True:
                    rgb_image, _, _ = auto.take_screenshot(crop=(1130 / 1920, 240 / 1080, 370 / 1920, 330 / 1080))
                    # 将Pillow图像转换为NumPy数组
                    img_np = np.array(rgb_image)
                    # 将图像从RGB格式转换为BGR格式（OpenCV使用BGR）
                    bgr_image = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    is_in = self.count_yellow_blocks(bgr_image)
                    if is_in:
                        print("到点，收杆!")
                        auto.press_key("space", wait_time=0)
                        if self.is_use_time_judge:
                            self.start_time = time.time()
                    else:
                        if self.is_use_time_judge:
                            # 识别出未进入黄色区域，则进行时间判断、
                            if time.time() - self.start_time > 2.2:
                                print("咋回事？强制收杆一次")
                                auto.press_key("space", wait_time=0)
                                self.start_time = time.time()
                    if not auto.find_element("app/resource/images/fishing/fishing.png", "image", threshold=0.8):
                        break
                if auto.find_element("本次获得", "text", max_retries=2):
                    print("钓鱼佬永不空军！")
                    if config.CheckBox_is_save_fish.value:
                        if auto.find_element("新纪录", "text", include=True, max_retries=2) or auto.find_element(
                                "app/resource/images/fishing/new_record.png", "image", threshold=0.5,
                                crop=(1245 / 1920, 500 / 1080, 121 / 1920, 78 / 1080), max_retries=2):
                            self.save_picture()
                    auto.press_key("esc")
                elif auto.find_element("鱼跑掉了", "text", max_retries=2):
                    print("鱼跑了，空军！")
            else:
                print("未识别到咬钩")
        else:
            print("放过这窝吧，已经没鱼了")

    def count_yellow_blocks(self, image):
        # 黄色的确切HSV值
        """计算图像中黄色像素的数量"""
        # 将图像转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 创建黄色掩膜
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        print(f"黄色块数为：{len(contours)}")
        return len(contours) >= 2

    def save_picture(self):
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_path, f"{current_date}.png")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        screenshot, _, _ = auto.take_screenshot()
        screenshot.save(file_path)
        print(f"出了条大的！已保存截图至：{file_path}")
