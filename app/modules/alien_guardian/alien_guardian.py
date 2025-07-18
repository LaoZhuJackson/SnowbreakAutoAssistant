import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class AlienGuardianModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.priority = [
            # 优先的伙伴
            "零度射线",
            "炽热艺术",
            "灼热烈炎",

            # 优先的增益
            "拦截",
            "再次投掷",
            "扩散灼烧",
            "加量燃烧瓶",

            "多处起爆",
            "扩散爆炸",
            "高亢",

            "急速射线",
            "能量稳定",
            "持续灼烧",
        ]

    def run(self):
        # self.select_friends()
        # 无尽模式
        if config.ComboBox_mode.value == 0:
            self.fight_endless()
        # 闯关模式
        else:
            self.fight_normal()

    def select_friends(self):
        """选择常驻伙伴"""
        timeout = Timer(20).start()

        while True:
            self.auto.take_screenshot()

            if timeout.reached():
                self.logger.error("异星守护战斗超时")
                break

    def fight_normal(self):
        timeout = Timer(1800).start()
        select_flag = False
        i = 0
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('请选择一个', 'text', crop=(1131 / 2560, 690 / 1440, 1438 / 2560, 750 / 1440)):
                select_flag = False
            if self.auto.find_element('请选择', 'text', crop=(1170 / 2560, 50 / 1440, 1385 / 2560, 130 / 1440)):
                for text in self.priority:
                    if self.auto.click_element(text, 'text', crop=(482 / 2560, 727 / 1440, 2080 / 2560, 817 / 1440)):
                        select_flag = True
                        break
                if not select_flag:
                    # 没出现推荐的则选中间的
                    self.auto.move_click(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y))
                if self.auto.click_element('确定', 'text', crop=(1220 / 2560, 1295 / 1440, 1330 / 2560, 1352 / 1440)):
                    select_flag = False
                continue

            if self.auto.find_element('设置', 'text', crop=(1174 / 2560, 773 / 1440, 1348 / 2560, 847 / 1440)):
                self.auto.press_key('esc')
                time.sleep(0.5)
                continue
            if self.auto.click_element('退出', 'text', crop=(710 / 1920, 934 / 1080, 813 / 1920, 996 / 1080)):
                break
            if self.auto.click_element('准备作战', 'text', crop=(2227 / 2560, 1300 / 1440, 2418 / 2560, 1362 / 1440),
                                       extract=[(3, 3, 2), 128]):
                continue

            if timeout.reached():
                self.logger.error("异星守护战斗超时")
                break

    def fight_endless(self):
        """
        无尽模式异星守护
        参考代码：https://github.com/noobdawn/SnowMazer/blob/main/SnowGuard.py
        """
        timeout = Timer(1800).start()
        select_flag = False
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('请选择一个', 'text', crop=(1131 / 2560, 690 / 1440, 1438 / 2560, 750 / 1440)):
                select_flag = False
            if self.auto.find_element('请选择', 'text', crop=(1170 / 2560, 50 / 1440, 1385 / 2560, 130 / 1440)):
                for text in self.priority:
                    if self.auto.click_element(text, 'text', crop=(482 / 2560, 727 / 1440, 2080 / 2560, 817 / 1440)):
                        select_flag = True
                        break
                if not select_flag:
                    # 没出现推荐的则选中间的
                    self.auto.move_click(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y))
                if self.auto.click_element('确定', 'text', crop=(1220 / 2560, 1295 / 1440, 1330 / 2560, 1352 / 1440)):
                    select_flag = False
                continue
            if self.auto.find_element('设置', 'text', crop=(1174 / 2560, 773 / 1440, 1348 / 2560, 847 / 1440)):
                self.auto.press_key('esc')
                time.sleep(0.5)
                continue
            if self.auto.click_element('惊喜奖励', 'text', crop=(856 / 1920, 34 / 1080, 1069 / 1920, 110 / 1080)):
                continue
            if self.auto.click_element('退出', 'text', crop=(710 / 1920, 934 / 1080, 1365 / 1920, 1062 / 1080)):
                continue
            if self.auto.click_element('准备作战', 'text', crop=(2227 / 2560, 1300 / 1440, 2418 / 2560, 1362 / 1440),
                                       extract=[(3, 3, 2), 128]):
                continue
            if self.auto.click_element('无尽', 'text', crop=(2217 / 2560, 743 / 1440, 2395 / 2560, 804 / 1440)):
                time.sleep(0.5)
                continue

            if timeout.reached():
                self.logger.error("异星守护战斗超时")
                break
