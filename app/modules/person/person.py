import math
import re
import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class PersonModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.power_times = None
        self.config_data = config.toDict()
        self.select_person_dic = self.config_data["home_interface_person"]
        self.character_list = [self.select_person_dic["LineEdit_c1"], self.select_person_dic["LineEdit_c2"],
                               self.select_person_dic["LineEdit_c3"], self.select_person_dic["LineEdit_c4"]]
        all_characters = config.all_characters.value
        self.pages = math.ceil(all_characters / 4) + 1
        self.no_chip = False
        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        self.auto.back_to_home()
        self.enter_person()
        for character in self.character_list:
            self.scroll_page(-1, self.pages)
            if character == '':
                continue
            self.find_person_and_quick_fight(character)
            if self.no_chip:
                break
        self.auto.back_to_home()

    def enter_person(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()
            # 已进入
            if self.auto.find_element("故事", "text", crop=(0, 0, 212 / 1920, 61 / 1080), is_log=self.is_log):
                break
            if self.auto.click_element("个人故事", "text", crop=(673 / 1920, 806 / 1080, 953 / 1920, 889 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue
            if self.auto.click_element("战斗", "text", crop=(1536 / 1920, 470 / 1080, 1632 / 1920, 516 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue

            if timeout.reached():
                self.logger.error("进入任务碎片界面超时")
                break

    def find_person_and_quick_fight(self, person_name):
        timeout = Timer(50).start()
        finish_flag = False
        fight_flag = False
        pos = None
        while True:
            self.auto.take_screenshot()

            if timeout.reached():
                self.logger.error("刷取角色碎片超时")
                break

            if fight_flag and self.auto.find_element('完成', 'text',
                                                     crop=(880 / 1920, 968 / 1080, 1033 / 1920, 1024 / 1080),
                                                     is_log=self.is_log):
                finish_flag = True
            if finish_flag:
                if self.auto.click_element('完成', 'text', crop=(880 / 1920, 968 / 1080, 1033 / 1920, 1024 / 1080),
                                           is_log=self.is_log):
                    time.sleep(0.5)
                    if not self.auto.find_element('完成', 'text',
                                                  crop=(880 / 1920, 968 / 1080, 1033 / 1920, 1024 / 1080),
                                                  is_log=self.is_log,
                                                  take_screenshot=True):
                        break
                else:
                    self.update_power_times()
                    if self.auto.find_element("故事", "text", crop=(0, 0, 212 / 1920, 61 / 1080)) and (
                            self.power_times == 0 or self.power_times == 6):
                        break
                continue
            if self.auto.find_element("快速作战", "text", crop=(856 / 1920, 229 / 1080, 1056 / 1920, 295 / 1080),
                                      is_log=self.is_log):
                self.auto.click_element('最大', 'text', crop=(1225 / 1920, 683 / 1080, 1341 / 1920, 750 / 1080),
                                        is_log=self.is_log)
                self.auto.click_element('开始作战', 'text', crop=(873 / 1920, 807 / 1080, 1047 / 1920, 864 / 1080),
                                        is_log=self.is_log)
                fight_flag = True
                time.sleep(1.5)
                continue
            # 先尝试使用记忆嵌片
            self.update_power_times()
            # 如果没有嵌片，则尝试使用
            if self.power_times == 0 and config.CheckBox_is_use_chip.value:
                if not self.use_chip():
                    # 没有记忆嵌片
                    if self.no_chip:
                        break
                    continue
                else:
                    self.auto.take_screenshot()
            pos = self.auto.find_element(person_name, "text", crop=(0, 738 / 1080, 1, 838 / 1080), is_log=self.is_log)
            # 找到对应角色
            if pos:
                top_left, bottom_right = pos
                # 传入bottom_right更准确一点
                quick_fight_pos = self.find_quick_fight(bottom_right, person_name)
                if quick_fight_pos:
                    self.auto.click_element_with_pos(quick_fight_pos, is_calculate=False)
                    time.sleep(0.5)
                    continue
                else:
                    self.logger.warn(f"未找到对应速战，检查是否已刷取或是否解锁{person_name}的速战")
                    break
            else:
                self.scroll_page()
                time.sleep(0.5)

    def find_quick_fight(self, name_pos, person_name):
        """
        根据角色名位置寻找最佳的速战
        :param person_name: 角色名
        :param name_pos: (x,y)
        :return: (x,y)|none
        """
        pos, min_distance = self.auto.find_target_near_source('速战', name_pos, crop=(0, 868 / 1080, 1, 940 / 1080),
                                                              is_log=False)
        if pos:
            # 适配屏幕缩放
            if min_distance < 250 / self.auto.scale_x:
                self.logger.info(f"找到对应的“速战”：({pos},{min_distance})")
                return pos
            else:
                self.logger.warn(
                    f"“速战”距离大于{250 / self.auto.scale_x}：({pos},{min_distance})，不是{person_name}的速战")
                return None
        return pos

    def use_chip(self):
        """
        使用记忆嵌片
        :return:
        """
        timeout = Timer(20).start()
        confirm_flag = False
        while True:
            self.auto.take_screenshot()

            # 道具不足，返回false
            if self.auto.find_element('没有该类道具', 'text', crop=(821 / 1920, 511 / 1080, 1092 / 1920, 568 / 1080),
                                      is_log=self.is_log):
                self.no_chip = True
                return False
            if self.auto.find_element("是否", "text", crop=(588 / 1920, 309 / 1080, 1324 / 1920, 384 / 1080),
                                      is_log=self.is_log):
                confirm_flag = True
            if confirm_flag:
                if self.auto.click_element('最大', 'text', crop=(1722 / 2560, 797 / 1440, 1848 / 2560, 867 / 1440),
                                           is_log=self.is_log):
                    self.auto.click_element('确定', 'text', crop=(1353 / 1920, 729 / 1080, 1528 / 1920, 800 / 1080),
                                            is_log=self.is_log)
                    self.auto.press_key('esc')
                    time.sleep(1)
                    return True
            if self.auto.click_element("app/resource/images/person/add_power.png", "image",
                                       crop=(1533 / 1920, 23 / 1080, 1599 / 1920, 81 / 1080), is_log=self.is_log):
                time.sleep(0.5)
                continue
            if timeout.reached():
                self.logger.error("使用记忆嵌片超时")
                if confirm_flag:
                    self.auto.press_key('esc')
                return False

    def scroll_page(self, direction: int = 1, page=1):
        """
        前后翻页
        :param page: 默认翻一页
        :param direction: 输入 -1（上一页） 或 1（下一页）
        :return:
        """
        direction = -1 if direction >= 0 else 1
        self.auto.mouse_scroll(int(904 / self.auto.scale_x), int(538 / self.auto.scale_y), 7000 * direction * page)

    def update_power_times(self):
        """更新嵌片数量"""
        # result=[['12/12', 1.0, [[58.0, 16.0], [112.0, 40.0]]]]
        result = self.auto.read_text_from_crop(crop=(1421 / 1920, 27 / 1080, 1538 / 1920, 76 / 1080))
        # 取出文字送去正则匹配
        times = self.detect_times(result[0][0])
        if times is not None:
            self.logger.info(f"记忆嵌片更新成功：{times}")
        else:
            self.logger.info(f"记忆嵌片更新失败：{result}")
        self.power_times = times

    @staticmethod
    def detect_times(text: str):
        """
        通过文本检查还有多少次刷取次数
        :param text:格式为“**/**”,str
        :return: '/'前面的嵌片数量
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
