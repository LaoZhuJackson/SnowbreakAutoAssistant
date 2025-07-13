import time

import cv2

from app.common.config import config
from app.common.utils import random_rectangle_point
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class DrinkModule:
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        self.enter_drink()

    def enter_drink(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element("奖励", 'text', crop=(2014 / 2560, 1327 / 1440, 2099 / 2560, 1379 / 1440),
                                      is_log=self.is_log):
                mode = config.ComboBox_card_mode.value
                if mode == 0:
                    pos = random_rectangle_point(((int(1379 / self.auto.scale_x), int(753 / self.auto.scale_y)),
                                                  (int(1576 / self.auto.scale_x), int(824 / self.auto.scale_y))), n=3)
                elif mode == 1:
                    pos = random_rectangle_point(((int(1175 / self.auto.scale_x), int(506 / self.auto.scale_y)),
                                                  (int(1376 / self.auto.scale_x), int(563 / self.auto.scale_y))), n=3)
                self.auto.click_element_with_pos(pos)

            if self.auto.find_element(['猜心对局', 'F'], 'text',
                                      crop=(1025 / 1920, 663 / 1080, 1267 / 1920, 717 / 1080), is_log=self.is_log):
                self.auto.press_key('f')
                continue

            if timeout.reached():
                self.logger.error("进入酒馆超时")
                break
