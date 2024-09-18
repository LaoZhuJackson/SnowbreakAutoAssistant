import time

import pyautogui

from config.config import config
from utilities.operation import move_to_then_click, match_all_by_x, is_exist_image, back_to_home, wait_then_click


class get_reward_module:
    def __init__(self):
        self.reward_root = "images/reward/"

    def receive_work(self):
        wait_then_click(self.reward_root + "work.png", 5)
        if is_exist_image(self.reward_root + "get.png"):
            move_to_then_click(self.reward_root + "get.png")
            move_to_then_click(self.reward_root + "click.png")
        if is_exist_image(self.reward_root + "execution.png"):
            move_to_then_click(self.reward_root + "execution.png")
            move_to_then_click(self.reward_root + "click.png")
        wait_then_click(self.reward_root + "periodic.png", 3)
        if is_exist_image(self.reward_root + "get.png"):
            move_to_then_click(self.reward_root + "get.png")
            move_to_then_click(self.reward_root + "click.png")
        back_to_home()

    def receive_credential(self):
        wait_then_click(self.reward_root + "credential.png", 5)
        move_to_then_click(self.reward_root + "daily_work.png")
        if is_exist_image(self.reward_root + "get_2.png"):
            move_to_then_click(self.reward_root + "get_2.png")
            move_to_then_click(self.reward_root + "click.png")
        move_to_then_click(self.reward_root + "reward.png")
        if is_exist_image(self.reward_root + "get_2.png"):
            move_to_then_click(self.reward_root + "get_2.png")
            move_to_then_click(self.reward_root + "click.png")
        back_to_home()

    def receive_mail(self):
        move_to_then_click(self.reward_root + "mail.png", confidence=0.9)
        move_to_then_click(self.reward_root + "get_3.png")
        if is_exist_image(self.reward_root + "click.png"):
            move_to_then_click(self.reward_root + "click.png")
        back_to_home()


if __name__ == '__main__':
    module = get_reward_module()
    module.receive_work()
    module.receive_credential()
    config.load_config()
    if config.get_value("CheckBox_mail"):
        module.receive_mail()
