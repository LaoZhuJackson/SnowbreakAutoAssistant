import time

from app.common.config import config
from app.common.ppOCR import ocr
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
        if config.ComboBox_power_usage.value == 0:
            self.by_maneuver()

    def check_power(self):
        has_colon = None
        has_days_leq_num = None
        ocr_result = self.update_ocr_result()

        auto.click_element(self.root + "stamina.png", "image", threshold=0.8, action="move_click")
        time.sleep(0.5)
        if ocr_result:
            has_colon = any(":" in item for item in ocr_result)
            has_days_leq_num = any(int(item[:-1]) <= self.day_num for item in ocr_result if "天" in item)
        while has_days_leq_num or has_colon:
            if has_days_leq_num:
                for index, item in enumerate(ocr_result):
                    if "天" in item:
                        day = int(item[:-1])
                        if day <= self.day_num:
                            self.click_text(item)
            if has_colon:
                self.click_text(":")
            ocr_result = self.update_ocr_result()
            if ocr_result:
                has_colon = any(":" in item for item in ocr_result)
                has_days_leq_num = any(int(item[:-1]) <= self.day_num for item in ocr_result if "天" in item)
            else:
                has_colon = None
                has_days_leq_num = None
        auto.press_key("esc")

    def click_text(self, text):
        auto.click_element(text, "text", include=True, crop=(277 / 1920, 288 / 1080, 800 / 1920, 380 / 1080))
        auto.click_element("确定", "text", include=False, action="move_click")
        time.sleep(0.2)
        auto.press_key("esc")
        time.sleep(0.5)
        auto.click_element(self.root + "stamina.png", "image", threshold=0.8, action="move_click")
        time.sleep(0.5)

    def update_ocr_result(self):
        auto.take_screenshot(crop=(277 / 1920, 288 / 1080, 800 / 1920, 380 / 1080))
        auto.perform_ocr()
        original_result = auto.ocr_result
        # 提取每个子列表中的字符串部分
        result = [item[1][0] for item in original_result]

        return result

    def by_maneuver(self):
        auto.click_element("app/resource/images/use_power/entrance.png", "image", max_retries=5, action="move_click")
        # 等待动画
        time.sleep(1)
        auto.click_element("材料", "text", include=True, max_retries=5, action="move_click")
        if auto.click_element("深渊", "text", include=False, max_retries=5, action="move_click"):
            while True:
                auto.click_element("速战", "text", include=True, max_retries=5, action="move_click")
                if auto.find_element("恢复感知", "text", include=True, max_retries=2):
                    auto.press_key("esc")
                    break
                auto.click_element("最大", "text", include=True, max_retries=5, action="move_click")
                auto.click_element("开始作战", "text", include=True, max_retries=5, action="move_click")
                auto.click_element("完成", "text", include=True, max_retries=5, action="move_click")
        auto.press_key("esc")
        auto.click_element("任务", "text", include=True, max_retries=5, action="move_click")
        if auto.click_element("领取", "text", include=True, max_retries=5, action="move_click",
                              crop=(10 / 1920, 920 / 1080, 190 / 1920, 1)):
            auto.press_key("esc")
        auto.press_key("esc")
        auto.press_key("esc")
