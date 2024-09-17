import time

import pyautogui

from config.config import config
from utilities.logger import logger
from utilities.operation import click, wait_for_image, wait_then_click, is_exist_image, exist_then_click, \
    move_to_then_click, locate, ensure_click, back_to_home

# 临时
time.sleep(3)


# todo 回主页
# todo 使用体力,其他使用体力的方式之后补充


class use_stamina_module:
    def __init__(self):
        self.maneuver_root = "images/maneuver/jiyexingdong/"
        self.in_game = "images/in_game/"
        self.click_flag = False

    def check_power(self, day_num):
        # 检查是否有过期体力
        move_to_then_click(self.in_game + "stamina.png", confidence=0.9)
        # todo 2_day图片资源空缺
        for day in range(day_num, 0, -1):
            if is_exist_image(self.in_game + str(day) + "_day.png", confidence=0.9):
                # print("1 day")
                move_to_then_click(self.in_game + str(day) + "_day.png", 2, confidence=0.9)
                self.click_flag = True
            if day == 1:
                if is_exist_image(self.in_game + "time.png", confidence=0.5):
                    # print("times")
                    point = locate(self.in_game + "time.png", confidence=0.5)
                    if point.x < pyautogui.size()[0] / 2:
                        ensure_click(point)
                        self.click_flag = True
            if self.click_flag:
                move_to_then_click(self.in_game + "yes.png")
                time.sleep(0.5)
                move_to_then_click(self.in_game + "click.png")

        back_to_home()

    def by_maneuver(self):
        # 刷活动材料
        move_to_then_click(self.maneuver_root + "entrance.png")
        move_to_then_click(self.maneuver_root + "material_entry.png")
        move_to_then_click(self.maneuver_root + "chasm.png", confidence=0.9)
        while True:
            move_to_then_click(self.maneuver_root + "fast_fight.png")
            if is_exist_image(self.maneuver_root + "no_power.png"):
                pyautogui.press('esc')
                break
            move_to_then_click(self.maneuver_root + "max.png")
            move_to_then_click(self.maneuver_root + "start_fight.png")
            move_to_then_click(self.maneuver_root + "finish.png")

        move_to_then_click(self.maneuver_root + "back.png")
        move_to_then_click(self.maneuver_root + "reward.png")
        if is_exist_image(self.maneuver_root + "get.png"):
            move_to_then_click(self.maneuver_root + "get.png")
            move_to_then_click(self.maneuver_root + "click.png")
        back_to_home()


if __name__ == '__main__':
    module = use_stamina_module()
    time.sleep(3)
    config.load_config()
    if config.get_value("CheckBox_is_use_power"):
        module.check_power(config.get_value("ComboBox_power_day")+1)
    module.by_maneuver()
