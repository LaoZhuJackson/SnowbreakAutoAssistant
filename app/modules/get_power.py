import time

from app.common.operation import wait_then_click, is_exist_image, move_to_then_click, back_to_home


class get_power_module:
    def __init__(self):
        self.in_game = "app/resource/images/in_game/"

    def friends_power(self):
        # 收赠好友体力
        wait_then_click(self.in_game + "friends.png", time_out=5, confidence=0.9)
        if is_exist_image(self.in_game + "power.png"):
            move_to_then_click(self.in_game + "power.png")
        back_to_home()

    def station_power(self):
        # 收取供应站体力
        move_to_then_click(self.in_game + "supply_station.png")
        move_to_then_click(self.in_game + "supply_station_yes.png", 2)
        if is_exist_image(self.in_game + "daily_resources.png"):
            move_to_then_click(self.in_game + "daily_resources.png", 2)
            time.sleep(0.3)
            move_to_then_click(self.in_game + "buy.png", 2)
            wait_then_click(self.in_game + "click.png", 2)
        back_to_home()


if __name__ == '__main__':
    module = get_power_module()
    module.friends_power()
    module.station_power()