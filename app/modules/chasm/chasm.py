import time
from datetime import datetime, timedelta

from app.common.config import config
from app.modules.automation.timer import Timer


class ChasmModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False

    def run(self):
        if not self.is_in_time_range():
            self.logger.warn('当前未开放拟境')
        else:
            self.is_log = config.isLog.value
            self.auto.back_to_home()
            self.chasm()
            self.receive_reward()

    def chasm(self):
        timeout = Timer(50).start()
        first_finish_flag = False
        second_finish_flag = False
        enter_second = False
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('测评次数不足', 'text', crop=(1141 / 2560, 684 / 1440, 1420 / 2560, 747 / 1440),
                                      is_log=self.is_log):
                break
            if self.auto.click_element('确定', 'text', crop=(1888 / 2560, 980 / 1440, 2020 / 2560, 1059 / 1440),
                                       is_log=self.is_log):
                second_finish_flag = False
                time.sleep(2)
                continue
            if first_finish_flag and second_finish_flag:
                break
            if first_finish_flag and not self.is_after_wednesday_4am():
                break
            if not first_finish_flag and self.auto.find_element("准备作战", "text", crop=(
                    1675 / 1920, 988 / 1080, 1833 / 1920, 1051 / 1080), is_log=self.is_log):
                if not self.auto.find_element("快速测评", "text", crop=(1236 / 1920, 943 / 1080, 1552 / 1920, 1),
                                              is_log=self.is_log):
                    first_finish_flag = True
            if first_finish_flag and self.is_after_wednesday_4am() and not enter_second:
                if self.auto.click_element("稳定值", "text", crop=(220 / 2560, 410 / 1440, 430 / 2560, 480 / 1440),
                                           is_log=self.is_log,
                                           extract=[(176, 175, 179), 128]):
                    enter_second = True
                    time.sleep(1)
                    continue
            if enter_second and first_finish_flag and not self.auto.find_element("快速测评", "text",
                                                                                 crop=(
                                                                                         1236 / 1920, 943 / 1080,
                                                                                         1552 / 1920,
                                                                                         1), is_log=self.is_log):
                second_finish_flag = True
                continue
            if self.auto.click_element("快速测评", "text", crop=(1236 / 1920, 943 / 1080, 1552 / 1920, 1),
                                       is_log=self.is_log):
                # 等确定按钮出现，防止提前second_finish_flag = True
                time.sleep(1)
                continue
            if self.auto.click_element("精神", "text", crop=(0, 758 / 1080, 1, 828 / 1080), is_log=self.is_log):
                continue
            if self.auto.click_element("特别派遣", "text", crop=(181 / 1920, 468 / 1080, 422 / 1920, 541 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue
            if self.auto.click_element("战斗", "text", crop=(1510 / 1920, 450 / 1080, 1650 / 1920, 530 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue

            if timeout.reached():
                self.logger.error("精神拟境超时")
                break

    def receive_reward(self):
        timeout = Timer(10).start()
        enter_flag = False
        while True:
            self.auto.take_screenshot()

            if enter_flag:
                if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                          is_log=self.is_log):
                    break
                if self.auto.click_element('键领取', 'text', crop=(2226 / 2560, 1300 / 1440, 2430 / 2560, 1362 / 1440),
                                           is_log=self.is_log):
                    continue
                else:
                    break
            if self.auto.find_element('排行奖励', 'text', crop=(0, 0, 233 / 1920, 118 / 1080), is_log=self.is_log):
                enter_flag = True
                continue
            if not enter_flag:
                if self.auto.find_element(['拟境', '精神'], 'text',
                                          crop=(73 / 1920, 56 / 1080, 218 / 1920, 112 / 1080), is_log=self.is_log):
                    self.auto.click_element_with_pos((int(143 / self.auto.scale_x), int(911 / self.auto.scale_y)))
                    time.sleep(1)
                    continue

            if timeout.reached():
                self.logger.error("领取拟境奖励超时")
                break
        self.auto.back_to_home()

    @staticmethod
    def is_after_wednesday_4am():
        now = datetime.now()  # 获取当前时间
        current_weekday = now.weekday()  # 获取当前是周几 (周一为0，周日为6)
        wednesday_4am = now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(
            days=2 - current_weekday)
        # 判断当前时间是否在本周三凌晨4点之后
        return now > wednesday_4am

    @staticmethod
    def is_in_time_range():
        now = datetime.now()  # 获取当前时间
        current_weekday = now.weekday()  # 获取当前是周几 (周一为0，周日为6)
        # print(current_weekday)
        # 周二上午10点
        tuesday_10am = now.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(
            days=1 - current_weekday)
        # 下周一凌晨4点
        next_monday_4am = now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(
            days=(0 - current_weekday) + 7)
        # print(tuesday_10am, now, next_monday_4am)
        return tuesday_10am <= now < next_monday_4am
