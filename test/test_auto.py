import cv2

from app.common.config import config
from app.common.logger import logger
from app.modules.automation.automation import Automation, auto_starter, auto_game

if __name__ == '__main__':
    # 启动器调用的自动类
    # 游戏窗口调用的自动类
    # auto_game = Automation(config.LineEdit_game_name.value, config.LineEdit_game_class.value, logger)
    # auto_starter.click_element('./test_auto.png', 'image', take_screenshot=True, threshold=0.7, crop=(0.5, 0.5, 1, 1),
    #                            action='mouse_click')
    # auto_starter.click_element('开始游戏','text',include=True,threshold=0.7,crop=(0.5,0.5,1,1),action='mouse_click')
    # result = auto_game.find_element(['心动水弹', 'F'], 'text', crop=(1025 / 1920, 663 / 1080, 1267 / 1920, 717 / 1080),
    #                                 take_screenshot=True)
    # print(result)
    # result = auto_game.find_element('../app/resource/images/water_bomb/shoot_self.png', 'image',
    #                                 crop=(1487 / 1920, 815 / 1080, 1723 / 1920, 900 / 1080),
    #                                 match_method=cv2.TM_CCOEFF_NORMED, take_screenshot=True)
    auto_game.click_element('../app/resource/images/water_bomb/hand_of_kaito_steal.png', 'image',
                            crop=(440 / 1920, 332 / 1080, 1510 / 1920, 878 / 1080), take_screenshot=True)
    # print(result)
