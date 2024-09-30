import math
import re
import time
import traceback

from app.common.config import config
from app.modules.automation import auto


class PersonModule:
    def __init__(self):
        self.config_data = config.toDict()
        self.select_person_dic = self.config_data["home_interface_person"]
        self.count = 0  # 记录使用了多少次速战
        self.name_dic = {
            0: '不选择',
            1: '朝翼',
            2: '瞬刻',
            3: '龙舌兰',
            4: '悖谬',
            5: '无限之视',
            6: '蓝闪',
            7: '冬至',
            8: '辉耀',
            9: '辉夜',
            10: '狂猎',
            11: '雨燕',
            12: '缄默',
            13: '咎冠',
            14: '羽蜕',
            15: '豹豹',
            16: '魔术师',
            17: '幽潮',
            18: '藏锋',
            19: '溯影',
            20: '云篆',
        }

    def run(self):
        try:
            self.enter_person()
            is_all_zero = all(value == 0 for _, value in self.select_person_dic.items())
            if is_all_zero:
                print("未选择任何需要刷碎片的角色")
                auto.press_key("esc")
                auto.press_key("esc")
                return
            else:
                # 等待动画
                time.sleep(1)
                self.fight()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def enter_person(self):
        auto.click_element("战斗", "text", include=False, max_retries=3,
                           crop=(1350 / 1920, 300 / 1080, 1870 / 1920, 800 / 1080), action="move_click")
        time.sleep(0.7)
        auto.click_element("个人故事", "text", include=False, max_retries=3, action="move_click")

    def fight(self):
        for key, value in self.select_person_dic.items():
            if value == 0:
                continue
            else:
                name = self.name_dic[value]
                times = math.ceil(len(self.name_dic) / 4) + 1
                for i in range(times):
                    result = auto.find_element(name, "text", include=True)
                    # 如果找到了对应名字
                    if result:
                        top_left, bottom_right = result
                        pos = auto.calculate_click_position((top_left, bottom_right))
                        print(f"pos:{pos}")
                        click_pos = self.corresponding_quick_fight(pos)
                        if click_pos:
                            self.quick_fight(click_pos)
                        else:
                            print(f"找到了{name},但未检测到{name}的“速战”")
                            if self.is_exist_power():
                                print(f"{name}已完成刷取")
                                # 跳出循环
                                break
                            else:
                                # 没体力了
                                print("尝试使用记忆嵌片包")
                                # 使用嵌片
                                auto.click_element("app/resource/images/person/add_power.png", "image",
                                                   action="move_click", max_retries=3)
                                auto.click_element("最大", "text", include=False, max_retries=3, action="move_click")
                                time.sleep(0.2)
                                auto.click_element("确定", "text", include=False, max_retries=3, action="move_click")
                                auto.press_key("esc")
                                click_pos = self.corresponding_quick_fight(pos)
                                if click_pos:
                                    # 可以完成速战,完成后退出循环
                                    self.quick_fight(click_pos)
                                    break
                                else:
                                    print(f"角色 {name} 未达成速战条件")
                                    # 退出翻页循环
                                    break
                    else:
                        print(f"未找到对应角色：{name}")
                        # 鼠标移动到可以翻页的位置
                        auto.click_element("超元链接", "text", include=False, offset=(0, -200), action="move")
                        # 未找到对应名字，则翻页
                        auto.mouse_scroll(1, -7100)
                key_num = int(re.search(r"\d+$", key).group())
                if key_num != 4:
                    # 翻完所有页之后，回到最开头
                    print("开始返回最开头位置")
                    auto.click_element("超元链接", "text", include=False, offset=(0, -200), action="move")
                    auto.mouse_scroll(times, 7100)
        # 结束所有循环，返回主页面
        auto.press_key("esc")
        auto.press_key("esc")

    def quick_fight(self, click_pos):
        """

        :param click_pos: 格式（（x1,y1），（x2,y2））
        :return:
        """
        print(f"传入的click_pos:{click_pos}")
        auto.click_element_with_pos(click_pos, action='move_click')
        if auto.click_element("最大", "text", include=False, max_retries=3,
                              action="move_click"):
            auto.click_element("开始作战", "text", include=False, max_retries=3,
                               action="move_click")
            auto.click_element("完成", "text", include=False, max_retries=3,
                               action="move_click")
            self.count += 1

    def corresponding_quick_fight(self, source_pos):
        """
        找到对应觉得速战
        :param source_pos: 格式（x,y）
        :return:如果pos存在且在对应距离内则返回对应位置((x1,y1),(x2,y2))，否则返回None
        """
        pos = auto.find_target_near_source("速战", include=False, source_pos=source_pos, position="bottom_right")
        top_left, bottom_right = pos
        if top_left and bottom_right:
            x, y = auto.calculate_click_position((top_left, bottom_right))
            distance = math.sqrt((x - source_pos[0]) ** 2 + (y - source_pos[1]) ** 2)
            if distance > 300:
                return None
            else:
                return top_left, bottom_right
        else:
            return None

    def is_exist_power(self):
        text = self.update_ocr_result()
        target = None
        is_exist = False
        # print(text)
        for item in text:
            if "/12" in item:
                target = item
                is_exist = True
                break
        # print(target)
        if is_exist:
            power = int(target.split('/')[0])
            if power != 0:
                return True
            else:
                return False
        else:
            print("未检测到/12")
            return False

    def update_ocr_result(self):
        auto.take_screenshot(crop=(1360 / 1920, 0, 1600 / 1920, 76 / 1080))
        auto.perform_ocr()
        original_result = auto.ocr_result
        # 提取每个子列表中的字符串部分
        result = [item[1][0] for item in original_result]
        return result
