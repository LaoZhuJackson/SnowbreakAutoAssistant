import cv2

from app.common.config import config
from app.modules.base_task.base_task import BaseTask


class AutoFModule(BaseTask):
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        while True:
            self.auto.take_screenshot()
            if self.auto.find_element("app/resource/images/fishing/collect.png", "image",
                                      crop=(1506 / 1920, 684 / 1080, 1547 / 1920, 731 / 1080), is_log=self.is_log,
                                      match_method=cv2.TM_CCOEFF_NORMED):
                self.auto.press_key("f")
