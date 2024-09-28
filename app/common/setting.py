# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2024
AUTHOR = "LaoZhu"
VERSION = "v0.0.1"
APP_NAME = "auto_chenbai"
HELP_URL = "https://github.com/LaoZhuJackson/auto_chenbai"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
FEEDBACK_URL = "https://space.bilibili.com/3546763489184642?spm_id_from=333.1007.0.0"
DOC_URL = "https://qfluentwidgets.com/"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
