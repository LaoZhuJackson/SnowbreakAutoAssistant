import time

import pyautogui

from utilities.operation import move_to_then_click, match_all_by_x, back_to_home


class person_module:
    def __init__(self):
        self.in_game = "images/in_game/"

    def person(self):
        # 刷人物碎片
        move_to_then_click(self.in_game + "fight.png")
        move_to_then_click(self.in_game + "personal_story.png")
        for i in range(2):
            match_all = match_all_by_x(self.in_game + "quick_fight.png", confidence=0.7)
            print(f"检测出{len(match_all)}个符合的点位")
            if len(match_all) > 0:
                pyautogui.moveTo(match_all[0])
                pyautogui.click(match_all[0])
                move_to_then_click(self.in_game + "max.png")
                move_to_then_click(self.in_game + "start_fight.png")
                move_to_then_click(self.in_game + "finish.png")
                time.sleep(1)
        back_to_home()


if __name__ == '__main__':
    module = person_module()
    module.person()
