import cv2

from app.modules.base_task.base_task import BaseTask


class AutoFModule(BaseTask):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            self.auto.take_screenshot()
            if self.auto.find_element("app/resource/images/fishing/collect.png", "image",
                                      crop=(1506 / 1920, 684 / 1080, 1547 / 1920, 731 / 1080),
                                      match_method=cv2.TM_CCOEFF_NORMED):
                self.auto.press_key("f")
