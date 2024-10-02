import time

from app.common.config import config
from app.modules.automation import auto


class ShoppingModule:
    def __init__(self):
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
        self.open_store()
        self.buy()

    @staticmethod
    def open_store():
        while not auto.find_element("app/resource/images/shopping/in_store.png", "image", threshold=0.9):
            auto.click_element("商店", "text", max_retries=3)
        # 等待商店动画
        time.sleep(0.2)
        auto.click_element("提取物", "text", include=True, crop=(328 / 1920, 435 / 1080, 274 / 1920, 74 / 1080), action="move")
        # 滚动至底部
        auto.mouse_scroll(4, -150)

    def buy(self):
        if self.person_dic["item_person_0"]:
            self.buy_from_dic(self.person_dic, "person")
        if self.weapon_dic["item_weapon_0"]:
            self.buy_from_dic(self.weapon_dic, "weapon")
        for key, item in self.commodity_dic.items():
            if item:
                text = self.name_dic[key]
                if auto.click_element(text, "text", include=False, action="move_click"):
                    time.sleep(0.2)
                    auto.click_element("最大", "text", include=True, crop=(1791 / 1920, 827 / 1080, 88 / 1920, 50 / 1080),
                                       action="move_click")
                    auto.click_element("购买", "text", include=False, crop=(1703 / 1920, 965 / 1080, 165 / 1920, 85 / 1080),
                                       action="move_click")
                    auto.press_key("esc")
                    # 滚动至底部
                    auto.mouse_scroll(4, -150)
        auto.press_key("esc")

    def buy_from_dic(self, dic: dict, name: str):
        first_flag = True
        for key, value in dic.items():
            if first_flag:
                first_flag = False
                continue
            else:
                if value:
                    if name == "person":
                        text = self.person_dic_re[key]
                    else:
                        text = self.weapon_dic_re[key]
                    if auto.click_element(text, "text", include=True, action="move_click"):
                        time.sleep(0.2)
                        auto.click_element("购买", "text", include=False, crop=(1703 / 1920, 965 / 1080, 165 / 1920, 85 / 1080),
                                           action="move_click")
                        auto.press_key("esc")
