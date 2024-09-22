import time

from app.common.logger import logger
from app.common.operation import click, wait_for_image, wait_then_click, is_exist_image, exist_then_click, \
    move_to_then_click


class enter_game_module:
    def __init__(self):
        self.start_game = "app/resource/images/start_game/"
        self.in_game = "app/resource/images/in_game/"

    def enter_game(self):
        print(is_exist_image(self.start_game + "start.png"))
        if not is_exist_image(self.start_game + "already_in_game.png"):
            if wait_for_image(self.start_game + "update_game.png", time_out=5) or wait_for_image(
                    self.start_game + "start.png", time_out=5):
                if exist_then_click(self.start_game + "update_game.png"):
                    print("需要更新")
                    wait_then_click(self.start_game + "update_yes.png")
                    while is_exist_image(self.start_game + "updating.png"):
                        time.sleep(1)
                wait_then_click(self.start_game + "start.png", 5, 0.7)
                if wait_for_image(self.start_game + "age.png"):
                    wait_then_click(self.start_game + "start_2.png", 5)
                # 首次登录与非首次登录进入主界面
                while True:
                    if exist_then_click(self.in_game + "qiandao.png", wait_time=2):
                        click(self.in_game + "flash_time.png")
                        break
                    else:
                        move_to_then_click(self.in_game + "setting_icon.png")
                    if is_exist_image(self.in_game + "setting_icon.png", confidence=0.9):
                        break
        else:
            print("已进入游戏")


if __name__ == '__main__':
    module = enter_game_module()
    module.enter_game()
