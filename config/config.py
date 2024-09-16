import json
import os

CONFIG_FILE = "config/user_config.json"  # 配置文件路径


class Config:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config_data = {}

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as file:
                self.config_data = json.load(file)
        else:
            # 如果配置文件不存在，初始化默认设置
            self.config_data = {
                "CheckBox_entry": False,
                "CheckBox_stamina": False,
                "CheckBox_shop": False,
                "CheckBox_use_power": False,
                "CheckBox_person": False,
                "CheckBox_chasm": False,
                "CheckBox_reward": False,
                "CheckBox_buy_1": False,
                "CheckBox_buy_2": False,
                "CheckBox_buy_3": False,
                "CheckBox_buy_4": False,
                "CheckBox_buy_5": False,
                "CheckBox_buy_6": False,
                "CheckBox_buy_7": False,
                "CheckBox_buy_8": False,
                "CheckBox_buy_9": False,
                "CheckBox_buy_10": False,
                "CheckBox_buy_11": False,
                "CheckBox_buy_12": False,
                "use_2_day_power": False,
                "power_usage": -1,
                "ComboBox_after_use": -1,
                "CheckBox_entry_1": False,
                "CheckBox_shop_3": False,
                "CheckBox_person_5": False,
                "CheckBox_stamina_2": False,
                "CheckBox_use_power_4": False,
                "CheckBox_buy_14": False,
                "CheckBox_buy_13": False,
                "CheckBox_buy_15": False
            }
            self.save_config()
        return self.config_data

    def save_config(self):
        """保存配置到文件"""
        with open(self.filepath, 'w') as file:
            json.dump(self.config_data, file, indent=4)

    def set_value(self, key, value):
        """更新配置并保存"""
        self.config_data[key] = value
        self.save_config()

    def get_value(self, key):
        """获取配置中的值"""
        return self.config_data.get(key, None)

    def reset(self):
        self.config_data = {
            "CheckBox_entry": False,
            "CheckBox_stamina": False,
            "CheckBox_shop": False,
            "CheckBox_use_power": False,
            "CheckBox_person": False,
            "CheckBox_chasm": False,
            "CheckBox_reward": False,
            "CheckBox_buy_1": False,
            "CheckBox_buy_2": False,
            "CheckBox_buy_3": False,
            "CheckBox_buy_4": False,
            "CheckBox_buy_5": False,
            "CheckBox_buy_6": False,
            "CheckBox_buy_7": False,
            "CheckBox_buy_8": False,
            "CheckBox_buy_9": False,
            "CheckBox_buy_10": False,
            "CheckBox_buy_11": False,
            "CheckBox_buy_12": False,
            "use_2_day_power": False,
            "power_usage": -1,
            "ComboBox_after_use": -1,
            "CheckBox_entry_1": False,
            "CheckBox_shop_3": False,
            "CheckBox_person_5": False,
            "CheckBox_stamina_2": False,
            "CheckBox_use_power_4": False,
            "CheckBox_buy_14": False,
            "CheckBox_buy_13": False,
            "CheckBox_buy_15": False
        }
        self.save_config()


config = Config(CONFIG_FILE)
