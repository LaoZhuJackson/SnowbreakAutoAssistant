import time

from app.common.config import config
from app.modules.automation import auto


class ActionModule:
    def __init__(self):
        pass

    def run(self):
        auto.click_element("支援技", "text", include=False, max_retries=10, action="move_click")
        time.sleep(0.5)
        auto.click_element("准备作战", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("开始作战", "text", include=False, max_retries=3, action="move_click")
        while not auto.find_element("黄色区域", "text", include=True,
                                    crop=(827 / 1920, 233 / 1080, 258 / 1920, 43 / 1080)):
            time.sleep(2)
        auto.key_down("w")
        if config.ComboBox_run.value == 0:
            # 切换疾跑
            auto.press_key("shift")
            time.sleep(6)
        else:
            for i in range(5):
                auto.press_key("shift", 1)
                time.sleep(0.3)
        auto.key_up("w")
        auto.click_element("退出", "text", include=False, max_retries=20,
                           crop=(903 / 1920, 938 / 1080, 114 / 1920, 66 / 1080), action="move_click")

    def enter_train(self):
        auto.click_element("战斗", "text", include=False, max_retries=3,
                           crop=(1541 / 1920, 468 / 1080, 90 / 1920, 48 / 1080), action="move_click")
        time.sleep(0.7)
        auto.click_element("常规行动", "text", include=False, max_retries=3, action="move_click")
        time.sleep(0.5)
        auto.mouse_scroll(1, -8500)
        auto.click_element("实战训练", "text", include=False, max_retries=3, action="move_click")
