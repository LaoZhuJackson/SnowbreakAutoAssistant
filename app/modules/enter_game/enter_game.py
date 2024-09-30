import time

from app.modules.automation import auto


class EnterGameModule:
    def __init__(self):
        self.enter_game_flag = False

    def run(self):
        self.check_update()
        if not self.enter_game_flag:
            self.enter_game()

    def check_update(self):
        if auto.find_element("凭证", "text", include=True) is None:
            print("开始检查是否需要更新")
            if auto.find_element("开始游戏", "text", include=False) is not None:
                print("无需更新")
                return
            print("需要更新")
            auto.click_element("获取更新", "text", max_retries=3)
            auto.click_element("确定", "text", max_retries=3)
            while auto.find_element("更新中", "text", include=True):
                time.sleep(5)
            print("更新完成")
        else:
            print("已进入游戏")
            self.enter_game_flag = True

    @staticmethod
    def enter_game():
        auto.click_element("开始游戏", "text", max_retries=3)
        time.sleep(10)
        while auto.find_element("app/resource/images/start_game/age.png", "image", threshold=0.9,
                                scale_range=(0.6, 1)) is None:
            time.sleep(1)
        auto.click_element("开始游戏", "text", max_retries=10, threshold=0.6,
                           crop=(650 / 1920, 800 / 1080, 1300 / 1920, 1))
        while auto.find_element("活动", "text", include=False) is None:
            if auto.find_element("养生专家", "text", include=True):
                auto.click_element("app/resource/images/start_game/newbird_cancel.png", "image", threshold=0.8,
                                   scale_range=(0.6, 1))
            auto.press_key("esc")
            time.sleep(2)
        print("已进入游戏")