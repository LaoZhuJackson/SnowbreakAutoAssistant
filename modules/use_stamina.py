import time

import pyautogui

from utilities.logger import logger
from utilities.operation import click, wait_for_image, wait_then_click, is_exist_image, exist_then_click, \
    move_to_then_click, locate, ensure_click

# 临时
time.sleep(3)

# todo 回主页
# todo 使用体力,其他使用体力的方式之后补充


class use_stamina_module:
    def __init__(self):
        self.maneuver_root = "images/maneuver/jiyexingdong/"
        self.in_game = "images/in_game/"

    def check_power(self):
        # 检查是否有过期体力
        move_to_then_click(self.in_game + "stamina.png", confidence=0.9)
        click_flag = False
        if is_exist_image(self.in_game + "time.png", confidence=0.5):
            # print("times")
            point = locate(self.in_game + "time.png", confidence=0.5)
            if point.x < pyautogui.size()[0] / 2:
                ensure_click(point)
                click_flag = True
        if is_exist_image(self.in_game + "one_day.png", confidence=0.9):
            # print("1 day")
            move_to_then_click(self.in_game + "one_day.png", 2, confidence=0.9)
            click_flag = True
        if is_exist_image(self.in_game + "three_day.png", confidence=0.9):
            # print("3 day")
            move_to_then_click(self.in_game + "three_day.png", 2, confidence=0.9)
            click_flag = True
        if is_exist_image(self.in_game + "five_day.png", confidence=0.9):
            # print("5 day")
            move_to_then_click(self.in_game + "five_day.png", 2, confidence=0.9)
            click_flag = True
        if is_exist_image(self.in_game + "six_day.png", confidence=0.9):
            # print("6 day")
            move_to_then_click(self.in_game + "six_day.png", 2, confidence=0.9)
            click_flag = True
        if click_flag:
            move_to_then_click(self.in_game + "yes.png")
            time.sleep(0.5)
            move_to_then_click(self.in_game + "click.png")
        else:
            print("无即将过期体力")
            pyautogui.press('esc')

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
        move_to_then_click(self.maneuver_root + "home.png")


if __name__ == '__main__':
    module = use_stamina_module()
    time.sleep(3)
    module.check_power()
    module.by_maneuver()
