from app.modules.automation import auto


class GetPowerModule:
    def __init__(self):
        self.flag = False

    def run(self):
        self.friends_power()
        self.station_power()

    @staticmethod
    def friends_power():
        auto.click_element("app/resource/images/get_power/friends.png", "image", threshold=0.8, max_retries=3,
                           action="move_click")
        auto.click_element("app/resource/images/get_power/add_power.png", "image", threshold=0.8, max_retries=3,
                           action="move_click")
        auto.press_key("esc")

    @staticmethod
    def station_power():
        auto.click_element("供应站", "text", include=False, max_retries=3, action="move_click")
        auto.click_element("app/resource/images/get_power/supply_station.png", "image", threshold=0.8, max_retries=3,
                           scale_range=(0.6, 1), action="move_click")
        if auto.click_element("每日物资配给箱", "text", include=False, max_retries=1, action="move_click"):
            auto.click_element("购买", "text", include=False, max_retries=3, action="move_click")
            auto.press_key("esc")
        auto.press_key("esc")
