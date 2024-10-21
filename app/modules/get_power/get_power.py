import time

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
                           crop=(288 / 1920, 446 / 1080, 91 / 1920, 77 / 1080), action="move_click")
        time.sleep(0.5)
        auto.click_element("键收赠", "text", include=True, crop=(1545 / 1920, 965 / 1080, 360 / 1920, 106 / 1080),
                           max_retries=3, action="move_click")
        auto.back_to_home()

    @staticmethod
    def station_power():
        auto.click_element("供应站", "text", include=False, max_retries=3, action="move_click",
                           crop=(120 / 1920, 538 / 1080, 106 / 1920, 69 / 1080))
        auto.click_element("app/resource/images/get_power/supply_station.png", "image", threshold=0.8, max_retries=3,
                           crop=(0, 400 / 1080, 79 / 1920, 84 / 1080), action="move_click")
        if auto.click_element("每日物资配给箱", "text", include=False, max_retries=3, action="move_click",
                              crop=(153 / 1920, 527 / 1080, 431 / 1920, 157 / 1080)):
            auto.click_element("购买", "text", include=False, max_retries=3, action="move_click",
                               crop=(1034 / 1920, 679 / 1080, 425 / 1920, 165 / 1080))
        auto.back_to_home()
