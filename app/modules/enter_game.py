import time

import pyautogui

from app.common.operation import is_exist_image, wait_for_image, exist_then_click, wait_then_click, move_to_then_click, \
    back_to_home, locate


class enter_game_module:
    def __init__(self):
        self.start_game = "app/resource/images/start_game/"
        self.in_game = "app/resource/images/in_game/"
        self.start_button_root = False

    def enter_game(self):
        if not is_exist_image(self.start_game + "already_in_game.png"):
            if is_exist_image(self.start_game + 'start.png', wait_time=5):
                print("已检测到黄色 开始游戏 按钮")
                self.start_button_root = self.start_game + 'start.png'

            elif is_exist_image(self.start_game + 'start_blue.png', wait_time=5):
                print("已检测到蓝色 开始游戏 按钮")
                self.start_button_root = self.start_game + 'start_blue.png'
            else:
                print("未检测到开始游戏按钮,跳过自动登录")
                return

            wait_then_click(self.start_button_root, 5, 0.7)
            if wait_for_image(self.start_game + "age.png"):
                sign = locate(self.start_game + "age.png")
                pyautogui.moveTo(sign[0]+100, sign[1])
                pyautogui.click()
            # 首次登录与非首次登录进入主界面
            while True:
                if exist_then_click(self.in_game + "qiandao.png", wait_time=2):
                    move_to_then_click(self.in_game + "flash_time.png")
                    print("已进入游戏")
                    break
                else:
                    print("未检测到 星辉凭证")
                    back_to_home()
                    if is_exist_image(self.start_game + "already_in_game.png", confidence=0.9):
                        break
        else:
            print("已进入游戏")

    def check_update(self):
        print("开始检查是否需要更新")
        if exist_then_click(self.start_game + "update_game.png",wait_time=2):
            print("需要更新")
            wait_then_click(self.start_game + "update_yes.png")
            # todo 改为识别是否存在开始游戏按钮
            while is_exist_image(self.start_game + "updating.png"):
                time.sleep(5)
        elif is_exist_image(self.start_game + "updating.png"):
            print("正在更新")
            while is_exist_image(self.start_game + "updating.png"):
                time.sleep(5)
        else:
            print("无需更新")


if __name__ == '__main__':
    module = enter_game_module()
    module.check_update()
    module.enter_game()
