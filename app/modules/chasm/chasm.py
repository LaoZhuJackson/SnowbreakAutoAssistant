import time
from datetime import datetime, timedelta

from app.modules.automation import auto


class ChasmModule:
    def __init__(self):
        self.continue_flag = True

    def run(self):
        if not self.is_in_time_range():
            print("当前未开放精神拟境")
            return
        else:
            self.chasm()

    def chasm(self):
        auto.click_element("战斗", "text", include=False, max_retries=3,
                           crop=(1541 / 1920, 468 / 1080, 90 / 1920, 48 / 1080), action="move_click")
        time.sleep(0.7)
        auto.click_element("特别派遣", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("精神拟境", "text", include=False, max_retries=3, action="move_click")
        self.fast_test()
        if self.continue_flag and self.is_after_thursday_4am():
            auto.click_element("精神拟境", "text", include=False, max_retries=3, offset=(0, 290), action="move_click")
            self.fast_test()
        time.sleep(0.2)
        auto.click_element("app/resource/images/chasm/reward.png", "image", max_retries=3, action="move_click")
        if auto.click_element("键领取", "text", include=True, max_retries=3, action="move_click"):
            auto.press_key("esc")
            time.sleep(0.2)
        auto.press_key("esc")
        # 返回主页面
        auto.click_element("app/resource/images/reward/home.png", "image", max_retries=3, action="move_click")

    def is_in_time_range(self):
        now = datetime.now()  # 获取当前时间
        current_weekday = now.weekday()  # 获取当前是周几 (周一为0，周日为6)
        print(current_weekday)
        # 周二上午10点
        tuesday_10am = now.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(
            days=1 - current_weekday)
        # 下周日凌晨4点
        next_sunday_4am = now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(
            days=6 - current_weekday)
        # print(tuesday_10am, now, next_sunday_4am)
        return tuesday_10am <= now < next_sunday_4am

    def is_after_thursday_4am(self):
        now = datetime.now()  # 获取当前时间
        current_weekday = now.weekday()  # 获取当前是周几 (周一为0，周日为6)
        wednesday_4am = now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(
            days=3 - current_weekday)

        # 判断当前时间是否在本周三凌晨4点之后
        return now > wednesday_4am

    def fast_test(self):
        for i in range(4):
            if auto.click_element("快速测评", "text", include=False, max_retries=3, action="move_click"):
                auto.click_element("确定", "text", include=True, max_retries=3, action="move_click")
                time.sleep(0.5)
            if auto.find_element("测评次数不足", "text", include=False):
                self.continue_flag = False
                break
