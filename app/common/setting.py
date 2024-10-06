# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2024
AUTHOR = "LaoZhu"
VERSION = "v1.1.3"
APP_NAME = "SnowbreakAutoAssistant"
HELP_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
REPO_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
FEEDBACK_URL = "https://space.bilibili.com/3546763489184642?spm_id_from=333.1007.0.0"
GITHUB_FEEDBACK_URL = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant/issues"
DOC_URL = "https://qfluentwidgets.com/"
QQ = "996710620"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
