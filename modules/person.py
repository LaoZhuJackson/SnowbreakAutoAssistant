import time

import pyautogui

from utilities.operation import move_to_then_click, match_all_by_x




class person_module:
    def __init__(self):
        self.in_game = "images/in_game/"

    def person(self):
        # 刷人物碎片
        move_to_then_click(self.in_game + "fight.png")
        move_to_then_click(self.in_game + "personal_story.png")
        match_all = match_all_by_x(self.in_game + "quick_fight.png", confidence=0.7)
        # match_all = match_all_by_x(in_game + "test.png", confidence=0.7)
        print(match_all)
        print(f"检测出{len(match_all)}个符合的点位")
        if len(match_all) > 0:
            for match in match_all[:2]:
                # 限制不点击第三个匹配点
                if match.left < 600:
                    pyautogui.moveTo(match)
                    pyautogui.click(match)
                    move_to_then_click(self.in_game + "max.png")
                    move_to_then_click(self.in_game + "start_fight.png")
                    move_to_then_click(self.in_game + "finish.png")
                    time.sleep(1)
        move_to_then_click(self.in_game + "home.png")


if __name__ == '__main__':
    module = person_module()
    time.sleep(3)
    module.person()
