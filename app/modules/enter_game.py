import time

from app.common.operation import is_exist_image, wait_for_image, exist_then_click, wait_then_click, move_to_then_click


class enter_game_module:
    def __init__(self):
        self.start_game = "app/resource/images/start_game/"
        self.in_game = "app/resource/images/in_game/"
        self.start_button_root = False

    def enter_game(self):
        if is_exist_image(self.start_game + 'start.png'):
            print("已检测到黄色 开始游戏 按钮")
            self.start_button_root = self.start_game + 'start.png'

        elif is_exist_image(self.start_game + 'start_blue.png'):
            print("已检测到蓝色 开始游戏 按钮")
            self.start_button_root = self.start_game + 'start_blue.png'
        else:
            print("未检测到开始游戏按钮,跳过自动登录")
            return
        if not is_exist_image(self.start_game + "already_in_game.png"):
            if wait_for_image(self.start_game + "update_game.png", time_out=5) or self.start_button_root:
                if exist_then_click(self.start_game + "update_game.png"):
                    print("需要更新")
                    wait_then_click(self.start_game + "update_yes.png")
                    while is_exist_image(self.start_game + "updating.png"):
                        time.sleep(1)
                print(self.start_button_root)
                wait_then_click(self.start_button_root, 5, 0.7)
                if wait_for_image(self.start_game + "age.png"):
                    wait_then_click(self.start_game + "start_2.png", 5)
                # 首次登录与非首次登录进入主界面
                while True:
                    if exist_then_click(self.in_game + "qiandao.png", wait_time=2):
                        move_to_then_click(self.in_game + "flash_time.png")
                        print("已进入游戏")
                        break
                    else:
                        print("未检测到 星辉凭证")
                        if is_exist_image(self.start_game + "already_in_game.png", confidence=0.9):
                            break
        else:
            print("已进入游戏")


if __name__ == '__main__':
    module = enter_game_module()
    module.enter_game()
