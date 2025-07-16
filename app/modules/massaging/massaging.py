import time

import cv2

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class MassagingModule:
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        self.enter_massaging()

    def enter_massaging(self):
        timeout = Timer(30).start()
        # 凯茜娅点击位置
        wife_pos = (175, 527)
        while True:
            self.auto.take_screenshot()

            if self.auto.click_element(
                "同意",
                "text",
                crop=(2275 / 2560, 1204 / 1440, 2366 / 2560, 1254 / 1440),
                is_log=self.is_log,
            ):
                break

            if self.auto.click_element(
                "调理",
                "text",
                crop=(1325 / 1920, 853 / 1080, 1517 / 1920, 903 / 1080),
                is_log=self.is_log,
            ):
                continue

            if self.auto.find_element(
                "管理本",
                "text",
                crop=(86 / 2560, 50 / 1440, 410 / 2560, 110 / 1440),
                is_log=self.is_log,
            ):
                wife_num = config.ComboBox_wife.value
                click_pos = (
                    int((wife_pos[0] + 370 * wife_num) / self.auto.scale_x),
                    int(wife_pos[1] / self.auto.scale_y),
                )
                self.auto.click_element_with_pos(click_pos)
                continue

            if self.auto.find_element(
                ["F", "管理本"],
                "text",
                crop=(1341 / 2560, 884 / 1440, 1682 / 2560, 953 / 1440),
                is_log=self.is_log,
            ):
                self.auto.press_key("f")
                # time.sleep(1)
                continue

            if timeout.reached():
                self.logger.error("进入按摩超时")
                break
