import time

from app.common.config import config
from app.modules.automation.timer import Timer


class MassagingModule:
    def __init__(self, auto, logger):
        super().__init__()
        self.auto = auto
        self.logger = logger

        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value
        # self.enter_massaging()
        self.start_massaging()

    def enter_massaging(self):
        timeout = Timer(30).start()
        # 凯茜娅点击位置
        wife_pos = (175, 527)
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element(['Space', 'pace'], 'text', crop=(1700 / 1920, 1027 / 1080, 1, 1),
                                      is_log=self.is_log):
                break
            if self.auto.click_element('同意', 'text', crop=(2275 / 2560, 1204 / 1440, 2366 / 2560, 1254 / 1440),
                                       is_log=self.is_log):
                break

            if self.auto.click_element('调理', 'text', crop=(1325 / 1920, 853 / 1080, 1517 / 1920, 903 / 1080),
                                       is_log=self.is_log):
                continue

            if self.auto.find_element('管理本', 'text', crop=(86 / 2560, 50 / 1440, 410 / 2560, 110 / 1440),
                                      is_log=self.is_log):
                wife_num = config.ComboBox_wife.value
                click_pos = (
                    int((wife_pos[0] + 370 * wife_num) / self.auto.scale_x), int(wife_pos[1] / self.auto.scale_y))
                self.auto.click_element_with_pos(click_pos)
                continue

            if self.auto.find_element(['F', '管理本'], 'text', crop=(1341 / 2560, 884 / 1440, 1682 / 2560, 953 / 1440),
                                      is_log=self.is_log):
                self.auto.press_key("f")
                # time.sleep(1)
                continue

            if timeout.reached():
                self.logger.error("进入按摩超时")
                break

    def start_massaging(self):
        timeout = Timer(300).start()
        is_x = False

        while True:
            self.auto.take_screenshot()

            if not is_x:
                self.auto.press_key("x")
                is_x = True

            if self.auto.click_element("再来一次", "text", crop=(1658 / 1920, 869 / 1080, 1833 / 1920, 939 / 1080),
                                       is_log=self.is_log):
                pass
            if self.auto.click_element("退出调理", "text", crop=(1658 / 1920, 984 / 1080, 1833 / 1920, 1053 / 1080),
                                       is_log=self.is_log):
                pass

            if self.auto.click_element("app/resource/images/massaging/yellow_dot.png", "image",
                                       crop=(700 / 1920, 335 / 1080, 1688 / 1920, 832 / 1080), is_log=self.is_log,
                                       threshold=0.7):
                self.auto.key_down("space")
                time.sleep(6)
                self.auto.key_up("space")
                continue

            if self.auto.click_element("app/resource/images/massaging/red_dot.png", 'image',
                                       crop=(700 / 1920, 335 / 1080, 1688 / 1920, 832 / 1080), is_log=self.is_log,
                                       threshold=0.7):
                self.auto.key_down("space")
                time.sleep(8)
                self.auto.key_up("space")
                continue

            if timeout.reached():
                self.logger.error("按摩超时")
                break
