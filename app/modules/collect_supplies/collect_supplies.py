import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class CollectSuppliesModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        super().__init__()

    def run(self):
        # 确保在主页面
        self.auto.back_to_home()

        if config.CheckBox_mail.value:
            self.receive_mail()
        if config.CheckBox_fish_bait.value:
            self.receive_fish_bait()

        self.friends_power()
        self.station_power()

    def friends_power(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            # 正常退出
            if self.auto.find_element('感知', 'text', crop=(761 / 1920, 517 / 1080, 1175 / 1920, 563 / 1080)):
                break
            # 重复进入的情况
            if self.auto.find_element('app/resource/images/reward/home.png', 'image', threshold=0.9,
                                      crop=(1635 / 1920, 18 / 1080, 1701 / 1920, 74 / 1080)):
                if not self.auto.find_element('键收赠', 'text',
                                              crop=(1722 / 1920, 1012 / 1080, 1858 / 1920, 1055 / 1080)):
                    break
            if self.auto.click_element('键收赠', 'text', crop=(1722 / 1920, 1012 / 1080, 1858 / 1920, 1055 / 1080)):
                continue
            if self.auto.click_element("app/resource/images/collect_supplies/friends.png", "image",
                                       crop=(259 / 1920, 448 / 1080, 364 / 1920, 515 / 1080)):
                continue

            if timeout.reached():
                self.logger.error("领取好友体力超时")
                break
        self.auto.back_to_home()

    def station_power(self):
        confirm_flag = False
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            # 按正常流程走完的退出情况
            if confirm_flag:
                if self.auto.click_element('购买', 'text', crop=(1271 / 1920, 747 / 1080, 1353 / 1920, 795 / 1080)):
                    break
            # 已经领取但重复进入的情况
            if self.auto.find_element('app/resource/images/reward/home.png', 'image', threshold=0.9,
                                      crop=(1635 / 1920, 18 / 1080, 1701 / 1920, 74 / 1080)):
                if self.auto.find_element('app/resource/images/collect_supplies/supply_station_selected.png', 'image',
                                          threshold=0.9, crop=(0, 397 / 1080, 91 / 1920, 486 / 1080)):
                    if not self.auto.find_element("每日物资配给箱", "text",
                                                  crop=(223 / 1920, 625 / 1080, 500 / 1920, 677 / 1080)):
                        break
            if self.auto.click_element("app/resource/images/collect_supplies/supply_station.png", "image",
                                       threshold=0.9, crop=(0, 397 / 1080, 91 / 1920, 486 / 1080)):
                pass
            if self.auto.click_element("每日物资配给箱", "text", crop=(223 / 1920, 625 / 1080, 500 / 1920, 677 / 1080)):
                confirm_flag = True
                time.sleep(1)
                continue
            if self.auto.click_element('供应站', 'text', crop=(141 / 1920, 553 / 1080, 229 / 1920, 596 / 1080)):
                continue
            if timeout.reached():
                self.logger.error("购买每日物资配给箱超时")
                break
        self.auto.back_to_home()

    def receive_mail(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080)):
                break
            if self.auto.find_element('app/resource/images/reward/home.png', 'image', threshold=0.9,
                                      crop=(1635 / 1920, 18 / 1080, 1701 / 1920, 74 / 1080)):
                if not self.auto.find_element('领取', 'text', crop=(1236 / 1920, 931 / 1080, 1, 1)):
                    break
            if self.auto.click_element('批量领取', 'text', crop=(303 / 1920, 982 / 1080, 462 / 1920, 1028 / 1080)):
                continue
            if self.auto.click_element('app/resource/images/collect_supplies/mail.png', 'image',
                                       crop=(76 / 1920, 437 / 1080, 151 / 1920, 491 / 1080)):
                continue

            if timeout.reached():
                self.logger.error("领取邮箱资源超时")
                break
        self.auto.back_to_home()

    def receive_fish_bait(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080)):
                break
            if self.auto.find_element('开拓任务', 'text', crop=(36 / 1920, 103 / 1080, 163 / 1920, 155 / 1080)):
                if not self.auto.click_element('键领取', 'text', crop=(22 / 1920, 965 / 1080, 227 / 1920, 1030 / 1080),
                                               extract=[(241, 240, 241), 128]):
                    break
                else:
                    break
            if self.auto.click_element("开拓目标", "text", crop=(1611 / 1920, 879 / 1080, 1716 / 1920, 919 / 1080)):
                time.sleep(0.5)
                continue
            if self.auto.click_element("新星开拓", "text", crop=(0, 758 / 1080, 1, 828 / 1080)):
                continue
            if self.auto.click_element("特别派遣", "text", crop=(181 / 1920, 468 / 1080, 422 / 1920, 541 / 1080)):
                time.sleep(0.3)
                continue
            if self.auto.click_element("战斗", "text", crop=(1536 / 1920, 470 / 1080, 1632 / 1920, 516 / 1080)):
                time.sleep(0.3)
                continue

            if timeout.reached():
                self.logger.error("领取鱼饵超时")
                break
        self.auto.back_to_home()
