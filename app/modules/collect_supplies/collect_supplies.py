import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class CollectSuppliesModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        super().__init__()

    def run(self):
        self.is_log = config.isLog.value
        # 确保在主页面
        self.auto.back_to_home()

        if config.CheckBox_mail.value:
            self.receive_mail()
        if config.CheckBox_fish_bait.value:
            self.receive_fish_bait()
        if config.CheckBox_dormitory.value:
            self.receive_dormitory()

        self.friends_power()
        self.station_power()

    def friends_power(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            # 正常退出
            if self.auto.find_element('感知', 'text', crop=(761 / 1920, 517 / 1080, 1175 / 1920, 563 / 1080),
                                      is_log=self.is_log):
                break
            # 收过体力再进入的情况
            if self.auto.find_element('好友', 'text',
                                      crop=(59 / 1920, 112 / 1080, 187 / 1920, 162 / 1080), is_log=self.is_log):
                if not self.auto.find_element('键收赠', 'text',
                                              crop=(1722 / 1920, 1012 / 1080, 1858 / 1920, 1055 / 1080),
                                              is_log=self.is_log):
                    break
            if self.auto.click_element('键收赠', 'text', crop=(1722 / 1920, 1012 / 1080, 1858 / 1920, 1055 / 1080),
                                       is_log=self.is_log):
                continue
            # if self.auto.click_element("app/resource/images/collect_supplies/friends.png", "image",
            #                            crop=(259 / 1920, 448 / 1080, 364 / 1920, 515 / 1080), is_log=self.is_log):
            #     continue
            if self.auto.find_element('基地', 'text', crop=(
                    1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080), is_log=self.is_log) and self.auto.find_element(
                '任务', 'text', crop=(
                        1452 / 1920, 327 / 1080, 1529 / 1920, 376 / 1080), is_log=self.is_log):
                self.auto.click_element_with_pos((int(330 / self.auto.scale_x), int(486 / self.auto.scale_y)))
                time.sleep(0.3)
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
                if self.auto.click_element('购买', 'text', crop=(1741 / 2560, 1004 / 1440, 1831 / 2560, 1060 / 1440),
                                           is_log=self.is_log):
                    break
            # 已经领取但重复进入的情况
            if self.auto.find_element(['限时', '补给箱'], 'text',
                                      crop=(195 / 1920, 113 / 1080, 325 / 1920, 160 / 1080), is_log=self.is_log):
                if not self.auto.find_element(["每日", "物资配给箱"], "text",
                                              crop=(223 / 1920, 625 / 1080, 500 / 1920, 677 / 1080),
                                              is_log=self.is_log):
                    break
            if self.auto.click_element(["每日", "物资配给箱"], "text",
                                       crop=(223 / 1920, 625 / 1080, 500 / 1920, 677 / 1080),
                                       is_log=self.is_log):
                confirm_flag = True
                time.sleep(1)
                continue
            if self.auto.click_element('供应站', 'text', crop=(141 / 1920, 553 / 1080, 229 / 1920, 596 / 1080),
                                       is_log=self.is_log):
                continue

            if not self.auto.find_element(["补给"], 'text', crop=(133 / 1920, 44 / 1080, 376 / 1920, 91 / 1080),
                                          is_log=self.is_log):
                self.auto.click_element_with_pos((int(47 / self.auto.scale_x), int(448 / self.auto.scale_y)))
                time.sleep(0.3)
                continue
            if timeout.reached():
                self.logger.error("购买每日物资配给箱超时")
                break
        self.auto.back_to_home()

    def receive_mail(self):
        timeout = Timer(30).start()
        click_flag = False
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                      is_log=self.is_log):
                break
            else:
                if click_flag:
                    break
            if self.auto.click_element('批量领取', 'text', crop=(303 / 1920, 982 / 1080, 462 / 1920, 1028 / 1080),
                                       is_log=self.is_log):
                click_flag = True
                continue
            # if self.auto.click_element('app/resource/images/collect_supplies/mail.png', 'image',
            #                            crop=(76 / 1920, 437 / 1080, 151 / 1920, 491 / 1080), is_log=self.is_log):
            #     continue
            if self.auto.find_element('基地', 'text', crop=(
                    1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080), is_log=self.is_log) and self.auto.find_element(
                '任务', 'text', crop=(
                        1452 / 1920, 327 / 1080, 1529 / 1920, 376 / 1080), is_log=self.is_log):
                self.auto.click_element_with_pos((int(115 / self.auto.scale_x), int(468 / self.auto.scale_y)))
                time.sleep(0.3)
                continue

            if timeout.reached():
                self.logger.error("领取邮箱资源超时")
                break
        self.auto.back_to_home()

    def receive_fish_bait(self):
        timeout = Timer(30).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                      is_log=self.is_log):
                break
            if self.auto.find_element('开拓任务', 'text', crop=(36 / 1920, 103 / 1080, 163 / 1920, 155 / 1080),
                                      is_log=self.is_log):
                if not self.auto.click_element('键领取', 'text', crop=(22 / 1920, 965 / 1080, 227 / 1920, 1030 / 1080),
                                               is_log=self.is_log,
                                               extract=[(241, 240, 241), 128]):
                    break
                else:
                    break
            if self.auto.click_element("开拓目标", "text", crop=(1611 / 1920, 879 / 1080, 1716 / 1920, 919 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.5)
                continue
            if self.auto.click_element("新星开拓", "text", crop=(0, 758 / 1080, 1, 828 / 1080), is_log=self.is_log):
                continue
            if self.auto.click_element("特别派遣", "text", crop=(181 / 1920, 468 / 1080, 422 / 1920, 541 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue
            if self.auto.click_element("战斗", "text", crop=(1536 / 1920, 470 / 1080, 1632 / 1920, 516 / 1080),
                                       is_log=self.is_log):
                time.sleep(0.3)
                continue

            if timeout.reached():
                self.logger.error("领取鱼饵超时")
                break
        self.auto.back_to_home()

    def receive_dormitory(self):
        """领取宿舍碎片"""
        timeout = Timer(30).start()
        finish_flag = False
        while True:
            self.auto.take_screenshot()

            if finish_flag and self.auto.click_element('退出', 'text',
                                                       crop=(2161 / 2560, 32 / 1440, 2250 / 2560, 94 / 1440),
                                                       is_log=self.is_log):
                while self.auto.click_element('退出', 'text',
                                              crop=(2161 / 2560, 32 / 1440, 2250 / 2560, 94 / 1440),
                                              is_log=self.is_log):
                    self.auto.take_screenshot()
                    time.sleep(1)
                break
            if self.auto.click_element('谢谢', 'text', crop=(1138 / 2560, 1075 / 1440, 1418 / 2560, 1153 / 1440),
                                       is_log=self.is_log):
                time.sleep(0.3)
                finish_flag = True
                self.auto.press_key('esc')
                continue
            if self.auto.click_element('键收取', 'text', crop=(1845 / 2560, 983 / 1440, 2073 / 2560, 1061 / 1440),
                                       is_log=self.is_log):
                time.sleep(1.5)
                self.auto.take_screenshot()
                # 无法获取时
                if self.auto.find_element(['已经', '上线', '断片'], 'text',
                                          crop=(979 / 2560, 687 / 1440, 1592 / 2560, 750 / 1440),
                                          is_log=self.is_log):
                    finish_flag = True
                    continue
                time.sleep(3)
                continue
            if self.auto.click_element('基地', 'text', crop=(2130 / 2560, 913 / 1440, 2217 / 2560, 977 / 1440),
                                       is_log=self.is_log):
                time.sleep(3)
                continue
            if self.auto.find_element('Esc', 'text', crop=(57 / 2560, 117 / 1440, 127 / 2560, 157 / 1440),
                                      is_log=self.is_log) or self.auto.find_element('Enter', 'text', crop=(
            9 / 2560, 1377 / 1440, 130 / 2560, 1431 / 1440), is_log=self.is_log):
                self.auto.press_key('esc')
                continue
            if self.auto.click_element(['剩', '剩余'], 'text',
                                       crop=(2072 / 2560, 1372 / 1440, 2150 / 2560, 1418 / 1440),
                                       is_log=self.is_log):
                time.sleep(1)
                continue
            if timeout.reached():
                self.logger.error("领取宿舍拼图超时")
                break

            self.auto.back_to_home()
