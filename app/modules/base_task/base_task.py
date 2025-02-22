import time

import win32gui

from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import instantiate_automation
from app.modules.automation.timer import Timer


class BaseTask:
    def __init__(self):
        self.logger = logger
        self.auto = None
        self.chose_auto()

    def run(self):
        pass

    def stop(self):
        self.auto.stop()

    def back_to_home(self):
        from app.modules.automation.automation import auto_game
        self.auto = auto_game
        timeout = Timer(10).start()
        while True:
            self.auto.take_screenshot()
            if self.auto.find_element('基地', 'text', crop=(
                    1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080)) and self.auto.find_element('任务', 'text', crop=(
                    1452 / 1920, 327 / 1080, 1529 / 1920, 376 / 1080)):
                break
            elif self.auto.click_element('app/resource/images/reward/home.png', 'image',
                                         crop=(1635 / 1920, 18 / 1080, 1701 / 1920, 74 / 1080)):
                time.sleep(0.5)
                continue
            elif self.auto.click_element("取消", "text", crop=(463 / 1920, 728 / 1080, 560 / 1920, 790 / 1080)):
                break
            else:
                self.auto.press_key('esc')
                time.sleep(0.5)

            if timeout.reached():
                self.logger.error("返回主页面超时")
                break

    def chose_auto(self, only_game=False):
        """
        自动选择auto，有游戏窗口时选游戏，没有游戏窗口时选启动器，都没有的时候循环，寻找频率1次/s
        :return:
        """
        timeout = Timer(20).start()
        while True:
            # 每次循环重新导入
            from app.modules.automation.automation import auto_starter, auto_game
            if win32gui.FindWindow(None, config.LineEdit_game_name.value) or only_game:
                if not auto_game:
                    instantiate_automation(auto_type='game')  # 尝试实例化 auto_game
                self.auto = auto_game
                flag = 'game'
            else:
                if not auto_starter:
                    instantiate_automation(auto_type='starter')  # 尝试实例化 auto_starter
                self.auto = auto_starter
                flag = 'starter'
            if self.auto:
                return flag
            if timeout.reached():
                logger.error("获取auto超时")
                break
