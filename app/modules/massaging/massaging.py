import cv2

from app.common.config import config
from app.modules.base_task.base_task import BaseTask


class MassagingModule:
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False

    def run(self):
        pass
