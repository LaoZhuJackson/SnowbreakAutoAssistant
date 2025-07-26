import time

from app.common.config import config
from app.modules.automation.timer import Timer


class MazeModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        self.run_mode = None

    def run(self):
        self.is_log = config.isLog.value
        self.run_mode = config.ComboBox_mode_maze.value

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

            # 达到99次上限
            if self.auto.find_element('已达上限', 'text', crop=(697 / 1920, 507 / 1080, 1250 / 1920, 575 / 1080),
                                      is_log=self.is_log):
                self.logger.warn('今日的迷宫次数已经一滴都不剩了')
                break
            if self.auto.find_element(['击败', '目标'], 'text', crop=(43 / 1920, 114 / 1080, 330 / 1920, 180 / 1080),
                                      is_log=self.is_log):
                self.auto.press_key('e')
                if need_move_forward:
                    self.auto.press_key('w', 1.5)
                    need_move_forward = False
                continue
            # 未选增益时的确认
            if self.auto.click_element('确定', 'text', crop=(1888 / 2560, 980 / 1440, 2020 / 2560, 1059 / 1440),
                                       is_log=self.is_log):
                continue

            if self.auto.click_element(['丢', '弃', '丢弃'], 'text',
                                       crop=(260 / 1920, 953 / 1080, 374 / 1920, 1023 / 1080),
                                       is_log=self.is_log, threshold=0.5):
                time.sleep(0.3)
                continue
            if self.auto.find_element('选择增益', 'text', crop=(842 / 1920, 36 / 1080, 1073 / 1920, 115 / 1080),
                                      is_log=self.is_log):
                if self.auto.find_element('请选择一个', 'text',
                                          crop=(1131 / 2560, 690 / 1440, 1438 / 2560, 750 / 1440), is_log=self.is_log):
                    select_flag = False
                if self.auto.click_element('单体', 'text', crop=(100 / 1920, 250 / 1080, 1571 / 1920, 328 / 1080),
                                           is_log=self.is_log):
                    select_flag = True
                if not select_flag:
                    # 没出现推荐的则选中间的
                    self.auto.move_click(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y))
                if self.auto.click_element('确认', 'text', crop=(910 / 1920, 980 / 1080, 1050 / 1920, 1050 / 1080),
                                           is_log=self.is_log):
                    select_flag = False
                    time.sleep(0.3)  # 停一下等动画
                continue
            if self.auto.click_element('退出', 'text', crop=(896 / 1920, 946 / 1080, 985 / 1920, 1011 / 1080),
                                       is_log=self.is_log):
                if self.run_mode == 0:
                    break
                time.sleep(1)
                continue
            if self.auto.click_element('确认', 'text', crop=(1343 / 1920, 718 / 1080, 1536 / 1920, 818 / 1080),
                                       is_log=self.is_log):
                need_move_forward = False
                continue
            if self.auto.click_element('开始作战', 'text', crop=(1731 / 1920, 976 / 1080, 1881 / 1920, 1024 / 1080),
                                       is_log=self.is_log):
                # time.sleep(3)
                timeout.reset()
                need_move_forward = True
                continue
            if self.auto.find_element('增益', 'text', crop=(0, 0, 336 / 1920, 71 / 1080), is_log=self.is_log):
                self.auto.press_key('esc')
                time.sleep(0.5)
                continue
            # 添加固定点击，避免选不到难度
            if self.auto.find_element(['难度', '选择'], 'text',
                                       crop=(0, 0, 330 / 1920, 90 / 1080), is_log=self.is_log):
                self.auto.click_element_with_pos((int(1536 / self.auto.scale_x), int(486 / self.auto.scale_y)))
                time.sleep(1.5)
                continue
            if self.auto.click_element(['增益', '厄险'], 'text',
                                       crop=(1430 / 1920, 240 / 1080, 1650 / 1920, 320 / 1080), is_log=self.is_log):
                time.sleep(1.5)
                continue

            if timeout.reached():
                self.logger.error("迷宫超时")
                break
