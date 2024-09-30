import time

from app.common.config import config
from app.modules.automation import auto


class GetRewardModule:
    def __init__(self):
        pass

    def run(self):
        self.receive_work()
        time.sleep(0.5)
        self.receive_credential()
        if config.CheckBox_mail.value:
            time.sleep(0.5)
            self.receive_mail()

    def receive_work(self):
        auto.click_element("任务", "text", include=False, max_retries=3,
                           crop=(1350 / 1920, 300 / 1080, 1870 / 1920, 800 / 1080), action="move_click")
        if not auto.find_element("目标达成", "text", include=True):
            if auto.click_element("键领取", "text", include=True, max_retries=1, action="move_click"):
                auto.press_key("esc")
            if auto.click_element("app/resource/images/reward/execution.png", "image", threshold=0.7, max_retries=3,
                                  action="move_click"):
                auto.press_key("esc")
        auto.click_element("定期", "text", include=False, crop=(0, 0, 247 / 1920, 315 / 1080), max_retries=3,
                           action="move_click")
        if auto.click_element("键领取", "text", include=True, action="move_click"):
            auto.press_key("esc")
        auto.press_key("esc")

    def receive_credential(self):
        auto.click_element("凭证", "text", include=True, max_retries=3, action="move_click")
        auto.click_element("每日任务", "text", include=False, max_retries=3, action="move_click")
        if auto.click_element("键领取", "text", include=True, crop=(0, 950 / 1080, 270 / 1920, 1), action="move_click"):
            auto.press_key("esc")
        auto.click_element("奖励", "text", include=False, max_retries=3, action="move_click")
        if auto.click_element("键领取", "text", include=True, action="move_click"):
            auto.press_key("esc")
        auto.press_key("esc")

    def receive_mail(self):
        auto.click_element("app/resource/images/reward/mail.png", "image", threshold=0.7, max_retries=3,
                           action="move_click")
        auto.click_element("批量领取", "text", include=True, max_retries=3, action="move_click")
        auto.press_key("esc")
        if not auto.find_element("凭证", "text", include=True):
            auto.press_key("esc")
