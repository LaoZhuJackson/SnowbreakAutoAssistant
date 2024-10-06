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
        if config.CheckBox_fish_bait.value:
            time.sleep(0.5)
            self.receive_fish_bait()

    def receive_work(self):
        auto.click_element("任务", "text", include=False, max_retries=3,
                           crop=(1445 / 1920, 321 / 1080, 107 / 1920, 77 / 1080), action="move_click")
        if not auto.find_element("目标达成", "text", include=True):
            if auto.click_element("键领取", "text", include=True, max_retries=1, action="move_click"):
                auto.press_key("esc")
            if auto.click_element("app/resource/images/reward/execution.png", "image", threshold=0.7,
                                  action="move_click"):
                auto.press_key("esc")
        auto.click_element("定期", "text", include=False, crop=(2 / 1920, 87 / 1080, 277 / 1920, 463 / 1080),
                           max_retries=3,
                           action="move_click")
        if auto.click_element("键领取", "text", include=True, action="move_click"):
            auto.press_key("esc")
        auto.press_key("esc")

    def receive_credential(self):
        auto.click_element("凭证", "text", include=True, max_retries=3, action="move_click")
        auto.click_element("每日任务", "text", include=False, max_retries=3, action="move_click")
        if auto.click_element("键领取", "text", include=True, crop=(0, 950 / 1080, 295 / 1920, 123 / 1080),
                              action="move_click"):
            auto.press_key("esc")
        auto.click_element("奖励", "text", include=False, max_retries=3, action="move_click")
        if auto.click_element("键领取", "text", include=True, action="move_click"):
            auto.press_key("esc")
        auto.back_to_home()

    def receive_mail(self):
        auto.click_element("app/resource/images/reward/mail.png", "image", threshold=0.7, max_retries=3,
                           action="move_click")
        auto.click_element("批量领取", "text", crop=(270/1920, 973/1080, 228/1920, 65/1080), include=True, max_retries=3,
                           action="move_click")
        auto.press_key("esc")
        auto.back_to_home()

    def receive_fish_bait(self):
        auto.click_element("战斗", "text", include=False, max_retries=3,
                           crop=(1541 / 1920, 468 / 1080, 90 / 1920, 48 / 1080), action="move_click")
        auto.click_element("特别派遣", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("新星开拓", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("开拓目标", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("键领取", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("获得道具", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("app/resource/images/reward/home.png", "image", threshold=0.7, action="move_click")
