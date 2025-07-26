import time

import win32gui

from app.common.config import config
from app.common.utils import random_rectangle_point
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

    def get_click_pos(self, name: str, n=3):
        """
        获取固定点击位置
        :param n: 密集度
        :param name: "stuff" or "chasm"
        :return: (x,y)
        """
        update_data = config.update_data.value
        data = update_data.split("_")
        online_width = float(data[0])  # 2560
        online_height = float(data[0]) * 9 / 16  # 1440
        client_rect = win32gui.GetClientRect(self.auto.hwnd)
        client_width = client_rect[2] - client_rect[0]  # 1920
        client_height = client_rect[3] - client_rect[1]  # 1080
        scale_x = client_width / online_width
        scale_y = client_height / online_height
        if name == "stuff":
            x1 = int(float(data[1]) * scale_x)
            y1 = int(float(data[2]) * scale_y)
            x2 = int(float(data[3]) * scale_x)
            y2 = int(float(data[4]) * scale_y)
        else:
            x1 = int(float(data[5]) * scale_x)
            y1 = int(float(data[6]) * scale_y)
            x2 = int(float(data[7]) * scale_x)
            y2 = int(float(data[8]) * scale_y)
        return random_rectangle_point(((x1, y1), (x2, y2)), n=n)

    def check_power(self):
        timeout = Timer(50).start()
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
                # if self.auto.click_element('app/resource/images/use_power/stamina.png', 'image',
                #                            crop=(833 / 1920, 0, 917 / 1920, 68 / 1080)):
                self.auto.click_element_with_pos(pos=(int(910 / self.auto.scale_x), int(35 / self.auto.scale_y)))
                time.sleep(0.5)
                continue
            if timeout.reached():
                self.logger.error("检查体力超时")
                break
        self.auto.back_to_home()

    def by_maneuver(self):
        """通过活动使用体力"""
        timeout = Timer(50).start()
        finish_flag = False  # 是否完成体力刷取
        enter_task = False  # 是否进入任务界面
        enter_maneuver_flag = False  # 是否进入活动页面

        update_data = config.update_data.value
        print(update_data)
        data = update_data.split("_")
        online_width = float(data[0])
        online_height = float(data[0]) * 9 / 16

        stuff_pos = (float(data[1]) / online_width, float(data[2]) / online_height, float(data[3]) / online_width,
                     float(data[4]) / online_height)
        chasm_pos = (float(data[5]) / online_width, float(data[6]) / online_height, float(data[7]) / online_width,
                     float(data[8]) / online_height)
        while True:
            self.auto.take_screenshot()

            if not enter_maneuver_flag:
                # 关卡未解锁
                if self.auto.find_element('解锁', 'text', crop=(717 / 1920, 441 / 1080, 1211 / 1920, 621 / 1080),
                                          is_log=self.is_log):
                    finish_flag = True
                    enter_maneuver_flag = True
                    self.auto.press_key('esc')
                    self.logger.warn("材料本未解锁“深渊”难度")
                    time.sleep(0.5)
                    continue
                if self.auto.click_element('速战', 'text', crop=(1368 / 1920, 963 / 1080, 1592 / 1920, 1),
                                           is_log=self.is_log):
                    time.sleep(0.7)
                    enter_maneuver_flag = True
                    continue
                # 在区域内找材料，没找到就固定点击
                if self.auto.click_element(['材料', '材', '料'], 'text', crop=stuff_pos, n=50, is_log=self.is_log):
                    time.sleep(0.3)
                    continue
                else:
                    if not (self.auto.find_element('基地', 'text', crop=(
                            1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080)) and self.auto.find_element('任务',
                                                                                                          'text',
                                                                                                          crop=(
                                                                                                                  1452 / 1920,
                                                                                                                  327 / 1080,
                                                                                                                  1529 / 1920,
                                                                                                                  376 / 1080))):
                        pos = self.get_click_pos("stuff")  # 获取点击位置
                        self.auto.click_element_with_pos(pos)
                        time.sleep(0.3)
                if self.auto.click_element(['深渊', '深', '渊'], 'text', crop=chasm_pos,
                                           is_log=self.is_log):

                    time.sleep(1)
                    continue
                else:
                    if not (self.auto.find_element('基地', 'text', crop=(
                            1598 / 1920, 678 / 1080, 1661 / 1920, 736 / 1080)) and self.auto.find_element('任务',
                                                                                                          'text',
                                                                                                          crop=(
                                                                                                                  1452 / 1920,
                                                                                                                  327 / 1080,
                                                                                                                  1529 / 1920,
                                                                                                                  376 / 1080))):
                        pos = self.get_click_pos("chasm")
                        self.auto.click_element_with_pos(pos)
                        time.sleep(1)
                # 需要用偏移的方式实现，这样有一个对“任务”的判断，说明还在主页面
                if self.auto.click_element("任务", "text", crop=(1445 / 1920, 321 / 1080, 1552 / 1920, 398 / 1080),
                                           offset=(-34 / self.auto.scale_x, 140 / self.auto.scale_y),
                                           is_log=self.is_log):
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
                        task_name = config.task_name.value
                        if task_name:
                            self.auto.click_element(task_name, 'text', crop=(0, 1280 / 1440, 1, 1), is_log=self.is_log)
                            time.sleep(0.2)
                else:
                    if self.auto.find_element("恢复感知", "text",
                                              crop=(1044 / 1920, 295 / 1080, 1487 / 1920, 402 / 1080),
                                              is_log=self.is_log):
                        self.auto.press_key('esc')
                        finish_flag = True
                        time.sleep(0.3)
                        self.auto.press_key('esc')
                        time.sleep(0.5)
                        continue
                    if self.auto.click_element(['开始', '作战'], 'text',
                                               crop=(848 / 1920, 800 / 1080, 1066 / 1920, 885 / 1080),
                                               is_log=self.is_log):
                        time.sleep(0.5)
                        continue
                    if self.auto.click_element('速战', 'text', crop=(1368 / 1920, 963 / 1080, 1592 / 1920, 1),
                                               is_log=self.is_log):
                        time.sleep(1)
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

            if timeout.reached():
                self.logger.error("使用体力超时")
                break
        self.auto.back_to_home()
