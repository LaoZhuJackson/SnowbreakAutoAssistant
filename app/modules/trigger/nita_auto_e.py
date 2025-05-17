import time

import cv2
import numpy as np

from app.common.config import config
from app.common.utils import count_color_blocks
from app.modules.base_task.base_task import BaseTask


class NitaAutoEModule(BaseTask):
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False
        self.upper_blue = np.array([109, 170, 255])
        self.lower_blue = np.array([104, 85, 200])

    def run(self):
        self.is_log = config.isLog.value

        if not self.init_auto('game'):
            return
        while True:
            self.auto.take_screenshot()
            if self.auto.find_element("12", "text", is_log=self.is_log,
                                      crop=(1100 / 2560, 931 / 1440, 1458 / 2560, 1044 / 1440)):
                # 进一步裁剪图片
                crop_image = self.auto.get_crop_form_first_screenshot(
                    crop=(1130 / 2560, 1000 / 1440, 1428 / 2560, 1029 / 1440))
                blue_blocks = count_color_blocks(crop_image, self.lower_blue, self.upper_blue, False)
                print(f"当前blue_block:{blue_blocks}")
                if blue_blocks > 1:
                    self.auto.press_key("e")
                    time.sleep(0.3)
