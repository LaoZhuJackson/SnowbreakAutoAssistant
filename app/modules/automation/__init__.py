from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import Automation

auto = Automation(config.get_value('game_title_name'), logger)