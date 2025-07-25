# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()

YEAR = 2025
AUTHOR = "LaoZhu"

APP_NAME = "SnowbreakAutoAssistant"
HELP_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
REPO_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
FEEDBACK_URL = "https://space.bilibili.com/3546763489184642?spm_id_from=333.1007.0.0"
GITHUB_FEEDBACK_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant/issues"
DOC_URL = "https://qfluentwidgets.com/"
QQ = "996710620"

ACTIVITY = [
    ["活动", "2024-11-7", "2024-12-19"],
    ["上半卡池", "2024-11-7", "2024-12-19"],
    ["下半卡池", "2024-11-28", "2024-12-19"],
    ["肉鸽挑战", "2024-11-7", "2024-12-16"],
    ["趣味关", "2024-12-5", "2024-12-19"],
    ["boss挑战", "2024-11-11", "2024-11-25"],
    ["火线突击", "2024-11-11", "2024-11-25"],
    ["积分周常", "2024-11-18", "2024-12-2"],
    ["绝地防线", "2024-11-25", "2024-12-9"],
    ["勇者游戏", "2024-12-2", "2024-12-16"],
]

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
