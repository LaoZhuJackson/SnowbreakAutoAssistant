import time

from app.common.config import config
from app.modules.automation import auto


class UseStaminaModule:
    def __init__(self):
        self.day_num = None
        self.click_flag = False
        self.root = "app/resource/images/use_power/"

    def run(self):
        if config.CheckBox_is_use_power.value:
            self.day_num = config.ComboBox_power_day.value + 1
            self.check_power()
            auto.back_to_home()
        if config.ComboBox_power_usage.value == 0:
            self.by_maneuver()
            auto.back_to_home()

    def check_power(self):
        auto.click_element(self.root + "stamina.png", "image", threshold=0.8, action="move_click")
        time.sleep(0.5)
        day_num = 1
        # self.update_ocr_result()
        while True:
            if day_num == 1:
                has_colon = self.update_ocr_result()
                if has_colon:
                    self.use(":")
            if auto.click_element(f"app/resource/images/use_power/{day_num}_day.png", "image", threshold=0.9,
                                  action="move_click", crop=(282 / 1920, 294 / 1080, 517 / 1920, 93 / 1080)):
                self.use()
            else:
                day_num += 1
                if day_num > self.day_num:
                    break

    def use(self, text=None):
        if text:
            auto.click_element(text, "text", include=True, crop=(282 / 1920, 294 / 1080, 517 / 1920, 93 / 1080))
        auto.click_element("确定", "text", include=False, action="move_click")
        time.sleep(0.2)
        auto.press_key("esc")
        time.sleep(0.5)
        auto.click_element(self.root + "stamina.png", "image", threshold=0.8, action="move_click")
        time.sleep(0.5)

    def update_ocr_result(self):
        auto.take_screenshot(crop=(282 / 1920, 294 / 1080, 517 / 1920, 93 / 1080))
        auto.perform_ocr()
        original_result = auto.ocr_result
        # 提取每个子列表中的字符串部分
        result = [item[1][0] for item in original_result]
        has_colon = any(":" in item for item in result)

        return has_colon

    def by_maneuver(self):
        auto.click_element("app/resource/images/use_power/entrance.png", "image", max_retries=5, action="move_click")
        # 等待动画
        time.sleep(1)
        auto.click_element("材料", "text", include=True, max_retries=3, action="move_click")
        if auto.click_element("深渊", "text", include=False, max_retries=2, action="move_click") or auto.click_element(
                "app/resource/images/use_power/chasm.png", "image", threshold=0.7, max_retries=2, action="move_click"):
            while True:
                auto.click_element("速战", "text", include=True, max_retries=5, action="move_click")
                if auto.find_element("恢复感知", "text", include=True, max_retries=2):
                    auto.press_key("esc")
                    break
                auto.click_element("最大", "text", include=True, max_retries=5, action="move_click")
                auto.click_element("开始作战", "text", include=True, max_retries=5, action="move_click")
                # 等待是否有等级提升
                time.sleep(2)
                auto.click_element("等级提升", "text", include=False, max_retries=2, action="move_click")
                auto.click_element("完成", "text", include=True, max_retries=5, action="move_click")
        auto.press_key("esc")
        auto.click_element("任务", "text", include=True, max_retries=5, action="move_click")
        if auto.click_element("领取", "text", include=True, max_retries=2, action="move_click",
                              crop=(6 / 1920, 933 / 1080, 267 / 1920, 134 / 1080)):
            auto.press_key("esc")
