from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import Automation

auto = Automation(config.game_title_name.value, logger)
