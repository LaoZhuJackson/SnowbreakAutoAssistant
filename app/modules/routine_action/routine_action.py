import time

from app.common.config import config
from app.modules.base_task.base_task import BaseTask


class ActionModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        pass

    def run(self):
        pass


    def enter_train(self):
        pass
