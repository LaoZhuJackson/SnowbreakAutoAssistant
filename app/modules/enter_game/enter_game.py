import time

from app.common.config import config
from app.modules.automation import auto


class EnterGameModule:
    def __init__(self):
        self.enter_game_flag = False

    def run(self):
        auto.window_title = config.LineEdit_starter_name.value
        # 激活登录器窗口
        auto.activate_window(auto.window_title)
        self.check_update()
        if not self.enter_game_flag:
            # 结束启动器的进入游戏操作后将窗口名改回来
            auto.window_title = config.LineEdit_game_name.value
            time.sleep(10)
            self.enter_game()

    def check_update(self):
        if not self.find_bases():
            print("开始检查是否需要更新")
            if auto.click_element("开始游戏", "text", include=True, action="move_click", max_retries=3):
                print("无需更新")
                return
            print("需要更新")
            auto.click_element("获取更新", "text", max_retries=3)
            auto.click_element("确定", "text", max_retries=3)
            while auto.find_element("更新中", "text", include=True):
                time.sleep(5)
            auto.click_element("开始游戏", "text", include=True, action="move_click", max_retries=3)
            print("更新完成")
        else:
            print("已进入游戏")
            self.enter_game_flag = True

    def enter_game(self):
        while not auto.find_element("app/resource/images/start_game/network.png", "image",
                                    crop=(1787 / 1920, 10 / 1080, 129 / 1920, 334 / 1080), threshold=0.7):
            time.sleep(1)
        auto.click_element("开始游戏", "text", include=True, max_retries=3, action="move_click")
        # 检查是否真的进入了
        self.ensure_enter()

    def ensure_enter(self):
        time.sleep(5)
        is_enter = self.find_bases()
        first_charm_flag = True
        while not is_enter:
            # 新手签到
            if auto.find_element("养生专家", "text", include=True):
                auto.click_element("app/resource/images/start_game/newbird_cancel.png", "image", threshold=0.8,
                                   max_retries=3, scale_range=(0.6, 1), action="move_click")
            else:
                auto.press_key("esc")
                time.sleep(0.5)
                # 如果触发退出游戏
                if auto.click_element("取消", "text", action="move_click"):
                    time.sleep(1)
            is_enter_2 = self.find_bases()
            if is_enter_2 and first_charm_flag:
                # 勾引皮肤公告
                auto.click_element("活动", "text", include=False, max_retries=3, action="move_click")
                time.sleep(1)
                auto.press_key("esc")
                first_charm_flag = False
                time.sleep(1)
            is_enter = self.find_bases()
        print("已进入游戏")

    def find_bases(self):
        is_enter = auto.find_element("基地", "text", include=False,
                                     crop=(1598 / 1920, 688 / 1080, 64 / 1920, 46 / 1080))
        if is_enter:
            time.sleep(1)
            if auto.find_element("基地", "text", include=False, crop=(1598 / 1920, 688 / 1080, 64 / 1920, 46 / 1080)):
                return True
        return False
