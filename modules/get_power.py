import time

from utilities.operation import wait_then_click, is_exist_image, move_to_then_click


class get_power_module:
    def __init__(self):
        self.in_game = "images/in_game/"

    def friends_power(self):
        # 收赠体力
        move_to_then_click(self.in_game + "friends.png")
        if is_exist_image(self.in_game + "power.png"):
            move_to_then_click(self.in_game + "power.png")
        move_to_then_click(self.in_game + "back.png")

    def station_power(self):
        # 收取供应站体力
        move_to_then_click(self.in_game + "supply_station.png")
        move_to_then_click(self.in_game + "supply_station_yes.png", 2)
        if is_exist_image(self.in_game + "daily_resources.png"):
            move_to_then_click(self.in_game + "daily_resources.png", 2)
            time.sleep(0.3)
            move_to_then_click(self.in_game + "buy.png", 2)
            wait_then_click(self.in_game + "click.png", 2)
        move_to_then_click(self.in_game + "back.png")


if __name__ == '__main__':
    module = get_power_module()
    time.sleep(3)
    module.friends_power()
    module.station_power()
