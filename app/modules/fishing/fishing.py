import os
import time
from datetime import datetime

import cv2
import numpy as np

from app.common.config import config
from app.modules.automation import auto


class FishingModule:
    def __init__(self):
        self.previous_yellow_block_count = 0
        self.previous_pixels = 0
        self.save_path = os.path.abspath("./fish")

    def run(self):
        if auto.click_element("app/resource/images/fishing/fishing_rod.png", "image", max_retries=2,
                              action="move_click"):
            if auto.find_element("有鱼儿上钩了", "text", include=True, max_retries=10):
                auto.press_key("space", wait_time=0)
                start_time = time.time()
                while True:
                    rgb_image, _, _ = auto.take_screenshot(crop=(1130 / 1920, 240 / 1080, 1500 / 1920, 570 / 1080))
                    # 将Pillow图像转换为NumPy数组
                    img_np = np.array(rgb_image)
                    # 将图像从RGB格式转换为BGR格式（OpenCV使用BGR）
                    bgr_image = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    is_in = self.count_yellow_blocks(bgr_image)
                    if is_in:
                        print("到点，收杆!")
                        auto.press_key("space", wait_time=0)
                        start_time = time.time()
                    else:
                        # 识别出未进入黄色区域，则进行时间判断、
                        if time.time() - start_time > 2.2:
                            print("咋回事？强制收杆一次")
                            auto.press_key("space", wait_time=0)
                            start_time = time.time()
                    if not auto.find_element("app/resource/images/fishing/fishing.png", "image",
                                             crop=(1645 / 1920, 845 / 1080, 1, 1), threshold=0.8):
                        break
                if auto.find_element("本次获得", "text", max_retries=2):
                    print("钓鱼佬永不空军！")
                    if config.CheckBox_is_save_fish.value:
                        if auto.find_element("新纪录", "text", include=True, max_retries=2) or auto.find_element(
                                "app/resource/images/fishing/new_record.png", "image", threshold=0.5,
                                crop=(1240 / 1920, 521 / 1080, 1368 / 1920, 561 / 1080), max_retries=2):
                            self.save_picture()
                    auto.press_key("esc")
                elif auto.find_element("鱼跑掉了", "text", max_retries=2):
                    print("鱼跑了，空军！")
        else:
            print("放过这窝吧，已经没鱼了")

    def count_yellow_blocks(self, image):
        # 黄色的确切HSV值
        yellow_hsv = np.array([98, 255, 255])
        """计算图像中黄色像素的数量"""
        # 将图像转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 设定一个小范围以确保捕捉到所有的黄色像素
        # lower_yellow = np.array([yellow_hsv[0] - 2, 200, 220])
        # upper_yellow = np.array([yellow_hsv[0] + 2, 255, 255])
        lower_yellow = np.array([20, 255, 255])
        upper_yellow = np.array([23, 255, 255])
        # lower_yellow = np.array([yellow_hsv[0], 255, 255])
        # upper_yellow = np.array([yellow_hsv[0], 255, 255])

        # 创建黄色掩膜
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours) >= 2

    def save_picture(self):
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_path, f"{current_date}.png")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        screenshot, _, _ = auto.take_screenshot()
        screenshot.save(file_path)
        print(f"出了条大的！已保存截图至：{file_path}")
