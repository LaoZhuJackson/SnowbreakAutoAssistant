import time

import pyautogui

from config.config import config
from utilities.operation import move_to_then_click, match_all_by_x, is_exist_image, locate, click, wait_for_image, \
    back_to_home


def drag_down(x, y):
    pyautogui.moveTo(x, y + 100)
    pyautogui.scroll(-500)
    pyautogui.scroll(-500)
    pyautogui.scroll(-500)


def drag_up(x, y):
    pyautogui.moveTo(x, y + 100)
    pyautogui.scroll(500)
    pyautogui.scroll(500)
    pyautogui.scroll(500)


class shopping_module:
    def __init__(self):
        self.shopping_root = "images/shopping/"
        self.config_data = config.load_config()

    def buy(self):
        move_to_then_click(self.shopping_root + "store.png")
        time.sleep(1)
        click_list = []
        commodity_count = 0
        point = locate(self.shopping_root + "flush.png", confidence=0.9)
        start_point = (point.x, point.y)

        for key in self.config_data:
            if "CheckBox_buy_" in key:
                commodity_count += 1
        print(commodity_count)
        for i in range(1, commodity_count + 1):
            click_list.append(config.get_value("CheckBox_buy_" + str(i)))
        # print(click_list)
        for index, is_click in enumerate(click_list):
            if is_click:
                num = index + 1
                # 先重置位置
                drag_up(start_point[0], start_point[1])
                print(f"购买：{num}")
                if num == 15:
                    drag_down(start_point[0], start_point[1])
                    self.ensure_click(num)
                else:
                    if is_exist_image(self.shopping_root + f"{num}.png", 0.9, 1):
                        self.ensure_click(num)
                    else:
                        drag_down(start_point[0], start_point[1])
                        self.ensure_click(num)
                if not wait_for_image(self.shopping_root + "buy.png", 2, 0.9):
                    drag_down(start_point[0], start_point[1])
                    self.ensure_click(num)
                if is_exist_image(self.shopping_root + "buy.png", confidence=0.9):
                    move_to_then_click(self.shopping_root + "max.png", confidence=0.9)
                    # move_to_then_click(self.shopping_root + "regular.png", confidence=0.9)
                    move_to_then_click(self.shopping_root + "buy.png", confidence=0.9)
                if is_exist_image(self.shopping_root + "buy_success.png", wait_time=3):
                    pass
                    # move_to_then_click(self.shopping_root + "buy_success.png")
        back_to_home()

    def ensure_click(self, num):
        click(self.shopping_root + f"{num}.png", 3, 0.9)
        if not wait_for_image(self.shopping_root + "buy.png", 2, 0.9):
            click(self.shopping_root + f"{num}.png", 3, 0.9)


if __name__ == '__main__':
    module = shopping_module()
    time.sleep(3)
    module.buy()
