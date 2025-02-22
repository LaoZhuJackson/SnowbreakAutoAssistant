import random
import time

from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class MazeModule(BaseTask):
    def __init__(self):
        super().__init__()

    def run(self):
        self.fight()

    def fight(self):
        """
        代码参考：https://github.com/noobdawn/SnowMazer/blob/main/SnowMazer.py
        """
        timeout = Timer(600).start()
        need_move_forward = True
        select_flag = False

        while True:
            self.auto.take_screenshot()

            if self.auto.find_element(['击败', '目标'], 'text', crop=(43 / 1920, 114 / 1080, 330 / 1920, 180 / 1080)):
                self.auto.press_key('e', 2)
                if need_move_forward:
                    self.auto.press_key('w', 1.5)
                    need_move_forward = False
                # 30%概率尝试放个大招
                if random.random() < 0.3:
                    self.auto.press_key('q')
                continue

            if self.auto.click_element('确定', 'text', crop=(1888 / 2560, 980 / 1440, 2020 / 2560, 1059 / 1440)):
                continue
            if self.auto.click_element('丢弃', 'text', crop=(274 / 1920, 970 / 1080, 361 / 1920, 1016 / 1080)):
                time.sleep(0.3)
                continue
            if self.auto.find_element('选择增益', 'text', crop=(842 / 1920, 36 / 1080, 1073 / 1920, 115 / 1080)):
                if self.auto.find_element('请选择一个', 'text',
                                          crop=(1131 / 2560, 690 / 1440, 1438 / 2560, 750 / 1440)):
                    select_flag = False
                if self.auto.click_element('单体', 'text', crop=(126 / 1920, 258 / 1080, 1571 / 1920, 328 / 1080)):
                    select_flag = True
                if not select_flag:
                    # 没出现推荐的则选中间的
                    self.auto.move_click(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y))
                if self.auto.click_element('确认', 'text', crop=(910 / 1920, 980 / 1080, 1012 / 1920, 1027 / 1080)):
                    select_flag = False
                continue
            if self.auto.click_element('退出', 'text', crop=(896 / 1920, 946 / 1080, 985 / 1920, 1011 / 1080)):
                time.sleep(1)
                continue
            if self.auto.click_element('开始作战', 'text', crop=(1731 / 1920, 976 / 1080, 1881 / 1920, 1024 / 1080)):
                time.sleep(3)
                timeout.reset()
                need_move_forward = True
                continue
            if self.auto.find_element('增益', 'text', crop=(0, 0, 336 / 1920, 71 / 1080)):
                self.auto.press_key('esc')
                time.sleep(0.5)
                continue
            if self.auto.click_element(['增益', '厄险'], 'text',
                                       crop=(1455 / 1920, 257 / 1080, 1630 / 1920, 300 / 1080)):
                time.sleep(1)
                continue

            if timeout.reached():
                self.logger.error("迷宫超时")
                break
