import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class ShoppingModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        self.config_data = config.toDict()
        self.commodity_dic = self.config_data["home_interface_shopping"]
        self.person_dic = self.config_data["home_interface_shopping_person"]
        self.weapon_dic = self.config_data["home_interface_shopping_weapon"]
        self.name_dic = {
            'CheckBox_buy_3': '通用强化套件',
            'CheckBox_buy_4': '优选强化套件',
            'CheckBox_buy_5': '精致强化套件',
            'CheckBox_buy_6': '新手战斗记录',
            'CheckBox_buy_7': '普通战斗记录',
            'CheckBox_buy_8': '优秀战斗记录',
            'CheckBox_buy_9': '初级职级认证',
            'CheckBox_buy_10': '中级职级认证',
            'CheckBox_buy_11': '高级职级认证',
            'CheckBox_buy_12': '合成颗粒',
            'CheckBox_buy_13': '芳烃塑料',
            'CheckBox_buy_14': '单极纤维',
            'CheckBox_buy_15': '光纤轴突',
        }
        self.person_dic_re = {
            "item_person_0": "人物碎片",
            "item_person_1": "肴",
            "item_person_2": "安卡希雅",
            "item_person_3": "里芙",
            "item_person_4": "晨星",
            "item_person_5": "茉莉安",
            "item_person_6": "芬妮",
            "item_person_7": "芙提雅",
            "item_person_8": "瑟瑞斯",
            "item_person_9": "琴诺",
            "item_person_10": "猫汐尔",
            "item_person_11": "晴",
            "item_person_12": "恩雅",
            "item_person_13": "妮塔",
        }
        self.weapon_dic_re = {
            "item_weapon_0": "武器",
            "item_weapon_1": "彩虹打火机",
            "item_weapon_2": "草莓蛋糕",
            "item_weapon_3": "深海呼唤",
        }

    def run(self):
        self.is_log = config.isLog.value

        self.open_store()
        self.buy()

    def open_store(self):
        timeout = Timer(10).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element("常规物资", "text", crop=(89 / 1920, 140 / 1080, 220 / 1920, 191 / 1080),
                                      is_log=self.is_log):
                break
            if self.auto.click_element("商店", "text", crop=(1759 / 1920, 1002 / 1080, 1843 / 1920, 1050 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.2)
                continue

            if timeout.reached():
                self.logger.error("打开商店超时")
                break

    def buy(self):
        timeout = Timer(30).start()
        buy_list = self.collect_item()
        # buy_list = ['通用强化套件', '精致强化套件','光纤轴突', '普通战斗记录']
        temp_list = buy_list.copy()
        finish_list = []
        is_selected = False
        if len(temp_list) != 0:
            text = temp_list.pop(0)
        else:
            text = ""

        self.scroll_to_bottom()
        while True:
            # 所有商品处理完毕
            if len(buy_list) == len(finish_list):
                break

            self.auto.take_screenshot()

            if text:
                if not is_selected:  # 当前没有选择任何商品
                    # 如果当前还有售罄动画存在
                    if self.auto.find_element('售罄', 'text', crop=(866 / 1920, 513 / 1080, 1048 / 1920, 880 / 1080),
                                              is_log=self.is_log):
                        continue
                    if self.auto.click_element(text, 'text', crop=(302 / 1920, 194 / 1080, 1, 1), is_log=self.is_log):
                        time.sleep(0.3)
                        is_selected = True
                        continue
                    else:
                        self.logger.warn(f'商店没有{text}')
                        finish_list.append(text)
                        # 更新text
                        if len(temp_list) != 0:
                            text = temp_list.pop(0)
                        else:
                            text = ""
                if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                          is_log=self.is_log):
                    self.auto.press_key('esc')
                    time.sleep(0.2)
                    self.scroll_to_bottom()
                    finish_list.append(text)
                    # 更新text
                    if len(temp_list) != 0:
                        text = temp_list.pop(0)
                    else:
                        text = ""
                    is_selected = False
                    continue
                if self.auto.find_element('不足', 'text', crop=(866 / 1920, 513 / 1080, 1048 / 1920, 880 / 1080),
                                          is_log=self.is_log):
                    self.logger.warn('买不起了，杂鱼~')
                    break
                if self.auto.click_element('最大', 'text', crop=(1713 / 1920, 822 / 1080, 1, 895 / 1080),
                                           is_log=self.is_log):
                    if self.auto.click_element('购买', 'text',
                                               crop=(1740 / 1920, 993 / 1080, 1828 / 1920, 1038 / 1080),
                                               is_log=self.is_log):
                        # 跳出去重新截图判断购买成功还是没钱
                        time.sleep(1)
                        continue
                else:  # 没选择成功或者售罄
                    is_selected = False
                    if self.auto.find_element('售罄', 'text', crop=(866 / 1920, 513 / 1080, 1048 / 1920, 880 / 1080),
                                              is_log=self.is_log):
                        finish_list.append(text)
                        # 更新text
                        if len(temp_list) != 0:
                            text = temp_list.pop(0)
                        else:
                            text = ""
                    continue
            else:
                break
            if timeout.reached():
                self.logger.error("购买商品超时")
                break
        self.auto.back_to_home()

    def collect_item(self):
        """
        收集所有要购买的商品
        :return: list
        """
        # 收集勾选的人物碎片
        first_flag = True
        result_list = []
        for key, value in self.person_dic.items():
            if first_flag:
                first_flag = False
                continue
            if value:
                result_list.append(self.person_dic_re[key])
        # 收集勾选的武器
        first_flag = True
        for key, value in self.weapon_dic.items():
            if first_flag:
                first_flag = False
                continue
            if value:
                result_list.append(self.weapon_dic_re[key])
        # 收集商品
        for key, value in self.commodity_dic.items():
            if value:
                result_list.append(self.name_dic[key])
        return result_list

    def scroll_to_bottom(self):
        timeout = Timer(20).start()
        while True:
            self.auto.mouse_scroll(int(1552 / self.auto.scale_x), int(537 / self.auto.scale_y), -1200)
            self.auto.take_screenshot()

            if self.auto.find_element("光纤轴突", "text", crop=(319 / 1920, 864 / 1080, 1861 / 1920, 1037 / 1080),
                                          is_log=self.is_log):
                break
            if timeout.reached():
                self.logger.error(
                    "滚动商店超时：未识别到“光纤轴突”，可尝试在设置中打开显示ocr识别结果，如果识别到有错别字，再去替换表添加错别字规则")
                break
