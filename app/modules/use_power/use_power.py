import time

from app.common.config import config
from app.modules.automation.timer import Timer


class UsePowerModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.day_num = 0
        self.is_log = False

    def run(self):
        self.is_log = config.isLog.value

        self.auto.back_to_home()
        if config.CheckBox_is_use_power.value:
            self.day_num = config.ComboBox_power_day.value + 1
            self.check_power()
        if config.ComboBox_power_usage.value == 0:
            self.by_maneuver()

    def check_power(self):
        timeout = Timer(30).start()
        current_check = 1  # 当前检查的体力剩余天数
        confirm_flag = False  # 是否选择好了体力
        enter_power_select = False  # 是否进入选择体力界面，用户禁止对体力图标的判断
        has_colon = False  # 是否存在冒号
        while True:
            self.auto.take_screenshot()

            if current_check > self.day_num:
                break

            if self.auto.find_element("恢复感知", "text", crop=(1044 / 1920, 295 / 1080, 1487 / 1920, 402 / 1080),
                                      is_log=self.is_log):
                enter_power_select = True
            else:
                enter_power_select = False

            if confirm_flag:
                if self.auto.find_element('获得道具', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                          is_log=self.is_log):
                    self.auto.press_key('esc')
                    confirm_flag = False
                    enter_power_select = False

            if enter_power_select:
                # 选择好了体力
                if confirm_flag:
                    if self.auto.click_element("确定", "text", crop=(1259 / 1920, 808 / 1080, 1422 / 1920, 864 / 1080)):
                        time.sleep(0.2)
                        continue
                # 执行ocr更新self.auto.ocr_result
                crop_image = self.auto.get_crop_form_first_screenshot(
                    crop=(387 / 2560, 409 / 1440, 1023 / 2560, 495 / 1440))
                self.auto.perform_ocr(image=crop_image, is_log=self.is_log)
                # 更新colon
                has_colon = any(':' in item[0] for item in self.auto.ocr_result)
                # print(f"{has_colon=}")
                has_day = any('天' in item[0] for item in self.auto.ocr_result)
                # 没有能使用的体力
                if not has_day and not has_colon:
                    break
                # 存在低于一天的体力药,并且进入了选择体力界面
                if has_colon:
                    if self.auto.click_element([':', '：'], 'text',
                                               crop=(387 / 2560, 409 / 1440, 1023 / 2560, 495 / 1440)):
                        confirm_flag = True
                        continue
                    confirm_flag = False
                # 存在大于一天但是小于day_num的体力药,并且进入了选择体力界面
                if current_check <= self.day_num:
                    if self.auto.click_element(f"{current_check}天", "text",
                                               crop=(387 / 2560, 409 / 1440, 1023 / 2560, 495 / 1440)):
                        confirm_flag = True
                        continue
                    # 低于day_num，没colon，没点击选择x_day.png->加一进行下一天的判断
                    else:
                        current_check += 1
                        # print("current_check", current_check)
                        confirm_flag = False
                        continue
            if not confirm_flag and not enter_power_select:
                if self.auto.click_element('app/resource/images/use_power/stamina.png', 'image',
                                           crop=(833 / 1920, 0, 917 / 1920, 68 / 1080)):
                    time.sleep(0.5)
                    continue
            if timeout.reached():
                self.logger.error("检查体力超时")
                break
        self.auto.back_to_home()

    def by_maneuver(self):
        """通过活动使用体力"""
        timeout = Timer(50).start()
        confirm_flag = False  # 是否进入确认界面
        finish_flag = False  # 是否完成体力刷取
        enter_task = False  # 是否进入任务界面
        enter_maneuver_flag = False  # 是否进入活动页面
        stuff_pos = config.stuff_pos.value
        chasm_pos = config.chasm_pos.value
        while True:
            self.auto.take_screenshot()

            if not enter_maneuver_flag:
                if self.auto.click_element('材料', 'text', crop=stuff_pos, n=50,
                                           is_log=self.is_log) or self.auto.click_element(
                        'app/resource/images/use_power/stuff.png', 'image', crop=stuff_pos, is_log=self.is_log):
                    time.sleep(0.3)
                    continue
                if self.auto.find_element('深渊', 'text', crop=chasm_pos, is_log=self.is_log) or self.auto.find_element(
                        'app/resource/images/use_power/chasm.png', 'image', crop=chasm_pos, is_log=self.is_log):
                    enter_maneuver_flag = True
                    continue
                if self.auto.click_element("app/resource/images/use_power/entrance.png", "image",
                                           crop=(1361 / 1920, 411 / 1080, 1562 / 1920, 554 / 1080), is_log=self.is_log):
                    time.sleep(1.5)
                    continue
            else:
                if finish_flag:
                    if self.auto.find_element(['剩余', '刷新', '天'], 'text',
                                              crop=(682 / 2560, 272 / 1440, 956 / 2560, 550 / 1440),
                                              is_log=self.is_log) or self.auto.find_element('领取', 'text', crop=(
                    0, 937 / 1080, 266 / 1920, 1), is_log=self.is_log):
                        enter_task = True
                    if enter_task:
                        if self.auto.click_element('领取', 'text', crop=(0, 937 / 1080, 266 / 1920, 1),
                                                   is_log=self.is_log):
                            break
                        if not self.auto.find_element('领取', 'text', crop=(0, 937 / 1080, 266 / 1920, 1),
                                                      is_log=self.is_log):
                            break
                    if self.auto.click_element('任务', 'text', crop=(0, 1280 / 1440, 1, 1),
                                               is_log=self.is_log):
                        time.sleep(0.2)
                        continue
                else:
                    # 关卡未解锁
                    if self.auto.find_element('解锁', 'text', crop=(717 / 1920, 441 / 1080, 1211 / 1920, 621 / 1080),
                                              is_log=self.is_log):
                        finish_flag = True
                        self.auto.press_key('esc')
                        time.sleep(0.5)
                        continue
                    if self.auto.find_element("恢复感知", "text",
                                              crop=(1044 / 1920, 295 / 1080, 1487 / 1920, 402 / 1080),
                                              is_log=self.is_log):
                        self.auto.press_key('esc')
                        finish_flag = True
                        time.sleep(0.3)
                        self.auto.press_key('esc')
                        time.sleep(0.5)
                        continue
                    if self.auto.click_element('速战', 'text', crop=(1368 / 1920, 963 / 1080, 1592 / 1920, 1),
                                               is_log=self.is_log):
                        time.sleep(0.7)
                        continue
                    if self.auto.click_element('完成', 'text', crop=(880 / 1920, 968 / 1080, 1033 / 1920, 1024 / 1080),
                                               is_log=self.is_log):
                        continue
                    if self.auto.click_element('等级提升', 'text', crop=(824 / 1920, 0, 1089 / 1920, 129 / 1080),
                                               is_log=self.is_log):
                        continue
                    if self.auto.click_element('最大', 'text', crop=(1221 / 1920, 679 / 1080, 1354 / 1920, 756 / 1080),
                                               is_log=self.is_log):
                        pass
                    if self.auto.click_element('开始作战', 'text',
                                               crop=(868 / 1920, 808 / 1080, 1046 / 1920, 865 / 1080),
                                               is_log=self.is_log):
                        time.sleep(0.5)
                        continue
                    if not confirm_flag and self.auto.click_element('深渊', 'text', crop=chasm_pos, n=50,
                                                                    is_log=self.is_log):
                        confirm_flag = True
                        time.sleep(0.7)
                        continue

            if timeout.reached():
                self.logger.error("使用体力超时")
                break
        self.auto.back_to_home()
