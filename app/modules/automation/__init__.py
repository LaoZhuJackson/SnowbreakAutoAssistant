from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import Automation

auto = Automation(config.LineEdit_game_name.value, logger)
