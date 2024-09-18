import time

import pyautogui

from utilities.operation import move_to_then_click, is_exist_image, locate, wait_then_click


class chasm_module:
    def __init__(self):
        self.chasm_root = "images/chasm/"
        self.continue_flag = True

    def chasm(self):
        wait_then_click(self.chasm_root + "fight.png",time_out=5)
        move_to_then_click(self.chasm_root + "special.png", time_out=3)
        move_to_then_click(self.chasm_root + "chasm.png")
        self.fast_test()
        if self.continue_flag:
            sign = locate(self.chasm_root + "sign.png")
            pyautogui.moveTo(sign[0], sign[1] + 230)
            pyautogui.click()
            self.fast_test()
        move_to_then_click(self.chasm_root + "reward.png", confidence=0.9)
        if is_exist_image(self.chasm_root + "get.png"):
            move_to_then_click(self.chasm_root + "get.png")
            move_to_then_click(self.chasm_root + "click.png", time_out=2)
            time.sleep(0.5)
        pyautogui.press('esc')
        move_to_then_click(self.chasm_root + "home.png")

    def fast_test(self):
        for i in range(4):
            if is_exist_image(self.chasm_root + "fast.png", confidence=0.9):
                move_to_then_click(self.chasm_root + "fast.png")
                move_to_then_click(self.chasm_root + "yes.png")
            if is_exist_image(self.chasm_root + "no_chance.png"):
                self.continue_flag = False
                break


if __name__ == '__main__':
    module = chasm_module()
    module.chasm()
