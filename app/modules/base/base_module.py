from abc import ABC, abstractmethod

class BaseModule(ABC):
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.enter_game_flag = False
        self.is_log = True

    @abstractmethod
    def run(self):
        pass

    @property
    def at_home(self) -> bool:
        """
        检查是否在主界面
        :return: bool
        """
        return (
                self.auto.find_element(
                    '基地', 'text',
                    crop=(1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080)
                )
                and
                self.auto.find_element(
                    '任务', 'text',
                    crop=(1452 / 1920, 327 / 1080, 1529 / 1920, 376 / 1080),
                    is_log=self.is_log
                )
        )
