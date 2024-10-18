# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2024
AUTHOR = "LaoZhu"
VERSION = "v1.1.5"
APP_NAME = "SnowbreakAutoAssistant"
HELP_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
REPO_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
FEEDBACK_URL = "https://space.bilibili.com/3546763489184642?spm_id_from=333.1007.0.0"
GITHUB_FEEDBACK_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant/issues"
DOC_URL = "https://qfluentwidgets.com/"
QQ = "996710620"

# 活动起止时间
ACTIVITY_START_TIME = '2024-9-26'
ACTIVITY_END_TIME = '2024-11-7'

# 趣味关起止时间
INTEREST_START_TIME = '2024-9-26'
INTEREST_END_TIME = '2024-10-21'

# 悖论迷宫起止时间
MAZES_START_TIME = '2024-10-10'
MAZES_END_TIME = '2024-10-31'

# 联机挑战关、积分周常起止时间
ONLINE_CHALLENGE_START_TIME = '2024-10-14'
ONLINE_CHALLENGE_END_TIME = '2024-10-28'

# boss挑战关、永续联战起止时间
BOSS_CHALLENGE_START_TIME = '2024-9-30'
BOSS_CHALLENGE_END_TIME = '2024-10-14'

# 勇者游戏起止时间
GAME_START_TIME = '2024-10-24'
GAME_END_TIME = '2024-11-7'

# 上半卡池
UPPER_START_TIME = '2024-9-26'
UPPER_END_TIME = '2024-10-26'

# 下半卡池
BOTTOM_START_TIME = '2024-10-17'
BOTTOM_END_TIME = '2024-11-7'

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
