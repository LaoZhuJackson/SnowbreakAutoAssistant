import time

import cv2
import numpy as np
import pyautogui

from app.common.operation import is_exist_image, move_to_then_click, wait_for_image


def exist_then_space(image_path, time_out=5, confidence=0.7):
    start_time = time.time()
    while time.time() - start_time < time_out:
        try:
            # 尝试定位界面中的特定图像
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location is None:
                time.sleep(0.2)
            else:
                print("成功识别")
                pyautogui.press('space')
                break
        except pyautogui.ImageNotFoundException:
            # 如果跳过没有检测到图片就跳过
            pass


def count_yellow_blocks(image):
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


def is_pointer_in_yellow(image, previous_yellow_count):
    """通过比较黄色像素数量的变化，判断指针是否进入黄色区域"""
    current_yellow_count = count_yellow_blocks(image)
    if previous_yellow_count == 0:
        print(f"current_yellow:{current_yellow_count}")
        return False, current_yellow_count
    # 如果黄色像素数量发生显著变化，说明指针进入或离开了黄色区域
    # 可以根据变化的阈值来判断（这里的阈值可以根据需要调整）
    change_threshold = 3  # 黄色像素变化的阈值
    print(abs(current_yellow_count - previous_yellow_count))
    if abs(current_yellow_count - previous_yellow_count) > change_threshold:
        return True, current_yellow_count
    return False, current_yellow_count


def capture_screen():
    """使用pyautogui截取当前屏幕并转换为OpenCV格式的图像"""
    # 使用pyautogui截取屏幕
    screenshot = pyautogui.screenshot()

    # 将Pillow图像转换为NumPy数组
    img_np = np.array(screenshot)

    # 将图像从RGB格式转换为BGR格式（OpenCV使用BGR）
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    return img_bgr


class fishing_module:
    def __init__(self):
        self.fishing_root = "app/resource/images/fishing/"
        self.previous_yellow_block_count = 0
        self.previous_pixels = 0

    def fishing(self):
        move_to_then_click(self.fishing_root + "fishing_rod.png")
        exist_then_space(self.fishing_root + "bite.png", time_out=7)
        start_time = time.time()
        while time.time() - start_time < 30:
            image = capture_screen()
            is_in = count_yellow_blocks(image)
            if is_in:
                print("指针进入了黄色区域!")
                pyautogui.press('space')
            if is_exist_image(self.fishing_root + "fish_run.png", wait_time=0):
                print("鱼跑了，空军！")
                break
            if is_exist_image(self.fishing_root + "get.png", wait_time=0):
                print("大丰收！")
                break
        print("退出钓鱼")

    def stop_fishing(self):
        pass


if __name__ == '__main__':
    # # 定义黄色的RGB值
    # yellow_rgb = np.uint8([[[255, 191, 0]]])# 黄色的HSV值: [[[ 98 255 255]]]
    # yellow_rgb = np.uint8([[[255, 214, 68]]]) # 黄色的HSV值: [[[ 97 187 255]]]
    #
    # # 将RGB转换为HSV
    # yellow_hsv = cv2.cvtColor(yellow_rgb, cv2.COLOR_BGR2HSV)
    # print("黄色的HSV值:", yellow_hsv)
    module = fishing_module()
    module.fishing()
    # previous_yellow_count = 0
    # while True:
    #     image = capture_screen()
    #     # 判断指针是否进入黄色区域
    #     in_yellow, previous_yellow_count = is_pointer_in_yellow(image, previous_yellow_count)
    #     print(f"previous_yellow_count:{previous_yellow_count}")
    #     previous_yellow_count = previous_yellow_count
