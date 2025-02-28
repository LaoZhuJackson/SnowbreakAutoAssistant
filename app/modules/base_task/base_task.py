import time

from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import Automation
from app.modules.automation.timer import Timer


class BaseTask:
    def __init__(self):
        self.logger = logger
        self.auto = None

    def run(self):
        pass

    def stop(self):
        self.auto.stop()

    def init_auto(self, name, switch=False):
        auto_dict = {
            'game': [config.LineEdit_game_name.value, config.LineEdit_game_class.value],
            'starter': [config.LineEdit_starter_name.value, config.LineEdit_starter_class.value]
        }
        if self.auto is None:
            try:
                self.auto = Automation(auto_dict[name][0], auto_dict[name][1], self.logger)
                return True
            except Exception as e:
                self.logger.error(f'初始化auto失败：{e}')
                return False
        else:
            self.logger.debug(f'延用auto：{self.auto.hwnd}')
            return True
        # else:
        #     if switch:
        #         timeout = Timer(10).start()
        #         while True:
        #             try:
        #                 self.auto = Automation(auto_dict[name][0], auto_dict[name][1], self.logger)
        #                 self.logger.info(f'切换auto成功')
        #                 return True
        #             except Exception as e:
        #                 self.logger.warn(f'未找到{auto_dict[name][0]}，等待1秒')
        #                 time.sleep(1)
        #             if timeout.reached():
        #                 self.logger.error(f'切换auto超时')
        #                 break

    # def chose_auto(self, only_game=False):
    #     """
    #     自动选择auto，有游戏窗口时选游戏，没有游戏窗口时选启动器，都没有的时候循环，寻找频率1次/s
    #     :return:
    #     """
    #     timeout = Timer(20).start()
    #     while True:
    #         # 每次循环重新导入
    #         from app.modules.automation.automation import auto_starter, auto_game
    #         if win32gui.FindWindow(None, config.LineEdit_game_name.value) or only_game:
    #             if not auto_game:
    #                 instantiate_automation(auto_type='game')  # 尝试实例化 auto_game
    #             self.auto = auto_game
    #             flag = 'game'
    #         else:
    #             if not auto_starter:
    #                 instantiate_automation(auto_type='starter')  # 尝试实例化 auto_starter
    #             self.auto = auto_starter
    #             flag = 'starter'
    #         if self.auto:
    #             return flag
    #         if timeout.reached():
    #             logger.error("获取auto超时")
    #             break
