import math
import re
import time
import traceback

import pyautogui

from app.common.config import config
from app.modules.automation import auto
from app.modules.automation.screenshot import Screenshot


class PersonModule:
    def __init__(self):
        self.config_data = config.toDict()
        self.select_person_dic = self.config_data["home_interface_person"]
        self.break_flag = False
        self.pages = math.ceil(34 / 4) + 1
        self.power_times = 0

        window = self.get_window(config.LineEdit_game_name.value)
        self.left, self.top, _, _ = Screenshot.get_window_region(window)

    def run(self):
        try:
            character_list = [self.select_person_dic["LineEdit_c1"], self.select_person_dic["LineEdit_c2"],
                              self.select_person_dic["LineEdit_c3"], self.select_person_dic["LineEdit_c4"]]
            is_all_none = all(value == "" for value in character_list)
            if is_all_none:
                print("未输入任何需要刷碎片的角色")
                auto.back_to_home()
                return
            else:
                self.enter_person()
                # 等待动画
                time.sleep(0.7)
                for value in character_list:
                    # 当选项为“不选择”时
                    if value == "":
                        continue
                    if self.break_flag:
                        break
                    self.update_power_times()
                    if not config.CheckBox_is_use_chip.value and self.power_times == 0:
                        break
                    self.next_page("back")
                    self.fight(value)
                auto.back_to_home()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def enter_person(self):
        auto.click_element("战斗", "text", include=False, max_retries=3,
                           crop=(1541 / 1920, 468 / 1080, 90 / 1920, 48 / 1080), action="move_click")
        time.sleep(0.7)
        auto.click_element("个人故事", "text", include=False, max_retries=3, action="move_click")

    def fight(self, value):
        if self.power_times == 0:
            if config.CheckBox_is_use_chip.value:
                self.use_chip()
            else:
                return
        # 找name
        if self.quick_fight_by_name(value):
            print(f"{value}刷取成功")
        else:
            print(f"{value}速战未成功")

    def use_chip(self):
        print("尝试使用2个记忆嵌片")
        auto.click_element("app/resource/images/person/add_power.png", "image", action="move_click", max_retries=1)
        time.sleep(0.5)
        if not auto.find_element("没有该类道具", "text", include=True, max_retries=1,
                                 crop=(821 / 1920, 511 / 1080, 271 / 1920, 57 / 1080)):
            auto.click_element("app/resource/images/person/add_num.png", "image", action="move_click", max_retries=2)
            auto.click_element("确定", "text", include=True, max_retries=3, action="move_click")
            auto.press_key("esc")
        else:
            print("无可用记忆嵌片")
            self.break_flag = True

    def get_window(self, title):
        """
        获取窗口
        :param title: 窗口名
        :return:
        """
        windows = pyautogui.getWindowsWithTitle(title)
        if windows:
            window = windows[0]
            return window
        return False

    def quick_fight_by_name(self, name):
        for _ in range(self.pages):
            name_pos = auto.find_element(name, "text", include=True, relative=True)
            if name_pos:
                quick_fight_pos = self.corresponding_quick_fight(name_pos[0])
                # print(quick_fight_pos)
                if quick_fight_pos:
                    self.quick_fight(quick_fight_pos)
                    return True
                else:
                    print(f"{name}未达成速战条件或无刷取次数")
                    return False
            else:
                self.next_page()
        return False

    def next_page(self, next_type="next"):
        """
        翻页
        :param next_type: 可选“next”或者“back”
        :return:
        """
        # 鼠标移动到可以翻页的位置
        auto.click_element("超元链接", "text", include=False, offset=(0, -200), action="move")
        if next_type == "next":
            # 未找到对应名字，则翻页
            auto.mouse_scroll(1, -7100)
        else:
            auto.mouse_scroll(self.pages, 7100)

    def quick_fight(self, click_pos):
        """
        :param click_pos: 格式（（x1,y1），（x2,y2））
        :return:
        """
        # print(f"传入的click_pos:{click_pos}")
        auto.click_element_with_pos(click_pos, action='move_click')
        if auto.click_element("最大", "text", include=False, max_retries=3,
                              action="move_click"):
            auto.click_element("开始作战", "text", include=False, max_retries=3,
                               action="move_click")
            auto.click_element("完成", "text", include=False, max_retries=3,
                               action="move_click")

    def corresponding_quick_fight(self, source_pos):
        """
        找到对应角色的速战
        :param source_pos: 格式（x,y），是相对位置
        :return:如果pos存在且在对应距离内则返回对应位置((x1,y1),(x2,y2))，否则返回None
        """
        pos = auto.find_target_near_source("速战", include=False, source_pos=source_pos, position="bottom_right")
        top_left, bottom_right = pos
        if top_left and bottom_right:
            x, y = auto.calculate_click_position((top_left, bottom_right))
            # 此时x,y是绝对位置，source_pos是相对游戏窗口左上角的位置，并非屏幕的绝对位置，所以需要转换成绝对位置，将坐标加上窗口左上角坐标做偏移
            source_pos = (source_pos[0] + self.left, source_pos[1] + self.top)
            # print(f"{(x, y)},{source_pos}")
            distance = math.sqrt((x - source_pos[0]) ** 2 + (y - source_pos[1]) ** 2)
            if distance > 250:
                print(f"“速战”距离大于350：{distance}")
                return None
            else:
                print(f"找到对应的“速战”：{distance}")
                return top_left, bottom_right
        else:
            print(f"没找到速战position：{pos}")
            return None

    # def find_text_in_area(self, pos):
    #     """
    #     通过位置找对应的文本内容
    #     :param pos: 查找区域格式：（（x1,y1），（x2,y2））
    #     :return: 对应区域内的文本列表
    #     """
    #     crop = (
    #         pos[0][0] / 1920, pos[0][1] / 1080, (pos[1][0] - pos[0][0]) / 1920, (pos[1][1] - pos[0][1]) / 1080)
    #     auto.take_screenshot(crop=crop)
    #     auto.perform_ocr()
    #     original_result = auto.ocr_result
    #     # 提取每个子列表中的字符串部分
    #     result = [item[1][0] for item in original_result]
    #
    #     return result

    def update_power_times(self):
        pos = ((1421, 27), (1538, 76))
        text_list = auto.find_text_in_area(pos)
        text = text_list[0]
        times = self.detect_times(text)
        if times is not None:
            print(f"记忆嵌片更新成功：{times}")
            self.power_times = times
        else:
            print(f"记忆嵌片更新失败：{text}")

    def detect_times(self, text: str):
        """
        通过文本检查还有多少次刷取次数
        :param text:格式为“**/**”,str
        :return:
        """
        # 正则表达式模式，匹配任意以数字开头并有"/"的部分
        pattern = r"(\d+)/"
        match = re.search(pattern, text)
        if match:
            # 获取匹配到的第一个组，也就是“/”前的数字
            times = match.group(1)
            return int(times)
        else:
            return None
