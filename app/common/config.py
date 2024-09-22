# coding:utf-8
import sys
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, FolderValidator, ConfigSerializer)

from .setting import CONFIG_FILE


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # TODO: ADD YOUR CONFIG GROUP HERE
    # 主页面
    CheckBox_entry_1 = ConfigItem("home_interface_option", "CheckBox_entry", False, BoolValidator())
    CheckBox_stamina_2 = ConfigItem("home_interface_option", "CheckBox_stamina", False, BoolValidator())
    CheckBox_shop_3 = ConfigItem("home_interface_option", "CheckBox_shop", False, BoolValidator())
    CheckBox_use_power_4 = ConfigItem("home_interface_option", "CheckBox_use_power", False, BoolValidator())
    CheckBox_person_5 = ConfigItem("home_interface_option", "CheckBox_person", False, BoolValidator())
    CheckBox_chasm_6 = ConfigItem("home_interface_option", "CheckBox_chasm", False, BoolValidator())
    CheckBox_reward_7 = ConfigItem("home_interface_option", "CheckBox_reward", False, BoolValidator())

    CheckBox_buy_1 = ConfigItem("home_interface_shopping", "CheckBox_buy_1", False, BoolValidator())
    CheckBox_buy_2 = ConfigItem("home_interface_shopping", "CheckBox_buy_2", False, BoolValidator())
    CheckBox_buy_3 = ConfigItem("home_interface_shopping", "CheckBox_buy_3", False, BoolValidator())
    CheckBox_buy_4 = ConfigItem("home_interface_shopping", "CheckBox_buy_4", False, BoolValidator())
    CheckBox_buy_5 = ConfigItem("home_interface_shopping", "CheckBox_buy_5", False, BoolValidator())
    CheckBox_buy_6 = ConfigItem("home_interface_shopping", "CheckBox_buy_6", False, BoolValidator())
    CheckBox_buy_7 = ConfigItem("home_interface_shopping", "CheckBox_buy_7", False, BoolValidator())
    CheckBox_buy_8 = ConfigItem("home_interface_shopping", "CheckBox_buy_8", False, BoolValidator())
    CheckBox_buy_9 = ConfigItem("home_interface_shopping", "CheckBox_buy_9", False, BoolValidator())
    CheckBox_buy_10 = ConfigItem("home_interface_shopping", "CheckBox_buy_10", False, BoolValidator())
    CheckBox_buy_11 = ConfigItem("home_interface_shopping", "CheckBox_buy_11", False, BoolValidator())
    CheckBox_buy_12 = ConfigItem("home_interface_shopping", "CheckBox_buy_12", False, BoolValidator())
    CheckBox_buy_13 = ConfigItem("home_interface_shopping", "CheckBox_buy_13", False, BoolValidator())
    CheckBox_buy_14 = ConfigItem("home_interface_shopping", "CheckBox_buy_14", False, BoolValidator())
    CheckBox_buy_15 = ConfigItem("home_interface_shopping", "CheckBox_buy_15", False, BoolValidator())

    ComboBox_after_use = OptionsConfigItem("home_interface_after_use", "ComboBox_after_use", 0,
                                           OptionsValidator([0, 1, 2, 3]))

    ComboBox_power_day = OptionsConfigItem("home_interface_power", "ComboBox_power_day", 0,
                                           OptionsValidator([0, 1, 2, 3, 4, 5]))
    ComboBox_power_usage = OptionsConfigItem("home_interface_power", "ComboBox_power_usage", 0,
                                             OptionsValidator([0, 1, 2, 3, 4, 5]))
    CheckBox_is_use_power = ConfigItem("home_interface_power", "CheckBox_is_use_power", False, BoolValidator())

    CheckBox_mail = ConfigItem("home_interface_reward", "CheckBox_mail", False, BoolValidator())

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


config = Config()
config.themeMode.value = Theme.LIGHT
qconfig.load(str(CONFIG_FILE.absolute()), config)
