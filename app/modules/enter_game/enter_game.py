import time

import win32gui

from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import instantiate_automation
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class EnterGameModule(BaseTask):
    def __init__(self):
        super().__init__()
        self.enter_game_flag = False
        # 对游戏和启动器的不同自动化类
        self.auto = None

    def run(self):
        auto_type = self.chose_auto()
        # 当游戏和启动器都开着的时候，auto_type="game",跳过handle_starter
        if auto_type == "starter":
            # todo 其他启动器适配
            self.handle_starter_new()
            # 切换成auto_game
            time.sleep(10)
            self.chose_auto(only_game=True)
        self.handle_game()

    def handle_starter_new(self):
        """
        处理官方新启动器启动器窗口部分
        :return:
        """
        while self.auto:
            # 截图
            self.auto.take_screenshot()
            # 对截图内容做对应处理
            if self.auto.click_element('开始游戏', 'text', crop=(0.5, 0.5, 1, 1), action='mouse_click'):
                logger.info("游戏无需更新或更新完毕")
                self.auto = None
                break
            if self.auto.find_element('游戏运行中', 'text', crop=(0.5, 0.5, 1, 1)):
                break
            if self.auto.find_element('正在更新', 'text', crop=(0.5, 0.5, 1, 1)):
                # 还在更新
                time.sleep(5)
                continue
            if self.auto.click_element('继续更新', 'text', crop=(0.5, 0.5, 1, 1), action='mouse_click'):
                time.sleep(5)
                continue
            if self.auto.click_element('更新', 'text', include=False, crop=(0.5, 0.5, 1, 1), action='mouse_click'):
                time.sleep(2)
                logger.info("需要更新")
                continue

    def handle_game(self):
        """处理游戏窗口部分"""
        while self.auto:
            # 截图
            self.auto.take_screenshot()

            # 对不同情况进行处理
            if self.auto.find_element('基地', 'text',
                                      (1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080)) and self.auto.find_element(
                '任务', 'text', (1452 / 1920, 327 / 1080, 1529 / 1920, 376 / 1080)):
                logger.info("已进入游戏")
                break
            if self.auto.click_element('开始游戏', 'text', crop=(852 / 1920, 920 / 1080, 1046 / 1920, 981 / 1080)):
                time.sleep(2)
                continue
            if self.auto.click_element(['X', 'x'], 'text', crop=(1271 / 1920, 88 / 1080, 1890 / 1920, 367 / 1080),
                                       action='move_click'):
                continue
            if self.auto.click_element("app/resource/images/start_game/newbird_cancel.png", "image",
                                       crop=(0.5, 0, 1, 0.5)):
                continue


if __name__ == '__main__':
    EnterGameModule().run()
