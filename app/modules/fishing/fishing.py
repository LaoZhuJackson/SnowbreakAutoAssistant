import os
import time
from datetime import datetime

import cv2
import numpy as np
from fuzzywuzzy import process

from app.common.config import config
from app.common.image_utils import ImageUtils
from app.common.signal_bus import signalBus
from app.common.utils import count_color_blocks
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class FishingModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.bite_time = None
        self.start_time = None
        self.is_use_time_judge = None
        self.previous_yellow_block_count = 0
        self.previous_pixels = 0
        self.save_path = os.path.abspath("./fish")
        self.press_key = None
        self.upper_yellow = None
        self.lower_yellow = None
        self.no_key = False
        self.is_select_fish = False

        self.is_log = False

    def run(self):
        # 每次钓鱼前更新各种设置参数
        self.upper_yellow = np.array([int(value) for value in config.LineEdit_fish_upper.value.split(',')])
        self.lower_yellow = np.array([int(value) for value in config.LineEdit_fish_lower.value.split(',')])
        self.press_key = config.LineEdit_fish_key.value
        self.is_log = config.isLog.value
        self.is_use_time_judge = config.CheckBox_is_limit_time.value
        self.start_time = time.time()

        if np.any(self.upper_yellow < self.lower_yellow):
            self.logger.error("运行错误，存在上限的值小于下限")
            return

        self.is_select_fish = False
        for i in range(config.SpinBox_fish_times.value):
            self.logger.info(f"开始第 {i + 1} 次钓鱼")
            try:
                self.enter_fish()
                self.start_fish()
                self.after_fish()
            except Exception as e:
                self.logger.warn(e)
                break

    def enter_fish(self):
        """
        进入钓鱼界面并选好鱼饵
        :return:
        """
        timeout = Timer(15).start()
        enter_flag = False
        lure_type_index = config.ComboBox_lure_type.value
        lure_type_list = ['万能', '普通', '豪华', '至尊', '重量级', '巨型', '重量级', '巨型']
        while True:
            self.auto.take_screenshot()

            # ImageUtils.show_ndarray(self.auto.first_screenshot)

            if self.auto.find_element(['饵', '重量级', '巨型', '万能', '普通', '豪华', '至尊'], 'text',
                                      crop=(1658 / 1920, 770 / 1080, 1892 / 1920, 829 / 1080), is_log=self.is_log):
                enter_flag = True
            if enter_flag:
                if not self.press_key and not self.get_press_key():
                    raise Exception(f'钓鱼抛竿按键未设置')
                # 还没甩竿
                if not self.is_spin_rod():
                    if self.auto.find_element('鱼饵不足', 'text',
                                              crop=(1200 / 2560, 686 / 1440, 1374 / 2560, 746 / 1440),
                                              is_log=self.is_log):
                        raise Exception(f'{lure_type_list[lure_type_index]}鱼饵不足')
                    if lure_type_index != 0 and not self.is_select_fish:
                        if self.select_lure():
                            self.is_select_fish = True
                            self.auto.press_key(self.press_key)
                            time.sleep(2)
                            continue
                    else:
                        self.auto.press_key(self.press_key)
                        time.sleep(2)
                        continue

                # 甩杆后
                if self.auto.find_element('上钩', 'text', crop=(787 / 1920, 234 / 1080, 1109 / 1920, 420 / 1080),
                                          is_log=self.is_log):
                    self.auto.press_key(self.press_key)
                    self.bite_time = time.time()
                    time.sleep(0.2)
                    break
            if self.auto.find_element(['目标', '今日'], 'text', crop=(0, 957 / 1080, 460 / 1920, 1),
                                      is_log=self.is_log):
                self.auto.press_key('esc')
                time.sleep(1)
                continue
            if self.auto.find_element('使用', 'text', crop=(1405 / 1920, 654 / 1080, 1503 / 1920, 747 / 1080),
                                      is_log=self.is_log):
                self.auto.press_key('f')
                time.sleep(1)
                continue

            if timeout.reached():
                self.logger.error("进入钓鱼超时")
                break

    def select_lure(self):
        open_lure = False
        lure_type_list = ['万能', '普通', '豪华', '至尊', '重量级', '巨型', '重量级', '巨型']
        lure_type_index = config.ComboBox_lure_type.value
        timeout = Timer(20).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element(lure_type_list[lure_type_index], 'text',
                                      crop=(1650 / 1920, 780 / 1080, 1850 / 1920, 837 / 1080), is_log=self.is_log):
                return True
            if self.auto.find_element('饵', 'text',
                                      crop=(1663 / 1920, 604 / 1080, 1898 / 1920, 773 / 1080), is_log=self.is_log):
                open_lure = True
            # 选取鱼饵
            if not open_lure:
                self.auto.click_element('app/resource/images/fishing/select_lure.png', 'image',
                                        crop=(1563 / 1920, 787 / 1080, 1598 / 1920, 823 / 1080), is_log=self.is_log,
                                        match_method=cv2.TM_CCOEFF_NORMED)
                time.sleep(0.3)
                continue
            else:
                self.auto.click_element(lure_type_list[lure_type_index], 'text',
                                        crop=(1663 / 1920, 604 / 1080, 1898 / 1920, 773 / 1080), is_log=self.is_log)
                time.sleep(0.3)

            if timeout.reached():
                self.logger.error("选择鱼饵超时超时")
                return False

    def start_fish(self):
        """
        qte收杆钓鱼
        :return:
        """
        timeout = Timer(60).start()
        while True:
            self.auto.take_screenshot(crop=(1130 / 1920, 240 / 1080, 1500 / 1920, 570 / 1080), is_interval=False)

            if config.ComboBox_fishing_mode.value == 0:
                # blocks_num = self.count_yellow_blocks(self.auto.current_screenshot)
                blocks_num = count_color_blocks(self.auto.current_screenshot, self.lower_yellow, self.upper_yellow)
                if blocks_num >= 2:
                    self.logger.info("到点，收杆!")
                    if self.is_use_time_judge:
                        self.start_time = time.time()
                    self.auto.press_key(self.press_key)
                elif blocks_num == 0:
                    time.sleep(0.3)
                    self.auto.take_screenshot(crop=(1130 / 1920, 240 / 1080, 1500 / 1920, 570 / 1080))
                    # blocks_num = self.count_yellow_blocks(self.auto.current_screenshot)
                    blocks_num = count_color_blocks(self.auto.current_screenshot, self.lower_yellow, self.upper_yellow)
                    # 连续两次都是0才返回false,避免误判
                    if blocks_num == 0:
                        # print("退出")
                        break
                else:
                    if self.is_use_time_judge:
                        # 识别出未进入黄色区域，则进行时间判断、
                        if time.time() - self.start_time > 2.2:
                            self.logger.warn("咋回事？强制收杆一次")
                            self.start_time = time.time()
                            self.auto.press_key(self.press_key)
            # 低性能模式判断方案
            else:
                if time.time() - self.bite_time > 1.8:
                    self.logger.info("到点，收杆!")
                    self.bite_time = time.time()
                    self.auto.press_key(self.press_key)

            if timeout.reached():
                self.logger.error("钓鱼环节超时")
                break

    def after_fish(self):
        timeout = Timer(10).start()
        save_flag = False
        while True:
            self.auto.take_screenshot()
            # if save_flag:
            #     if self.auto.find_element("新纪录", "text") or self.auto.find_element(
            #             "app/resource/images/fishing/new_record.png", "image", threshold=0.5,
            #             crop=(1245 / 1920, 500 / 1080, 1366 / 1920, 578 / 1080), is_log=self.is_log):
            #         self.save_picture()
            #     break
            if self.auto.find_element('本次获得', 'text', crop=(835 / 1920, 288 / 1080, 1076 / 1920, 377 / 1080),
                                      is_log=self.is_log):
                self.logger.info("钓鱼佬永不空军！")
                if config.CheckBox_is_save_fish.value:
                    save_flag = True
                    time.sleep(1)
                    continue
                self.auto.press_key('esc')
                time.sleep(1)
                break
            if self.auto.find_element('鱼跑掉了', 'text', crop=(858 / 1920, 151 / 1080, 1054 / 1920, 280 / 1080),
                                      is_log=self.is_log):
                self.logger.warn("鱼跑了，空军！")
                break
            # 如果回到了未甩杆状态，也退出
            if not self.is_spin_rod():
                break

            if timeout.reached():
                self.logger.error("钓鱼结束环节超时")
                break

    def save_picture(self):
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_path, f"{current_date}.png")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.auto.take_screenshot()
        self.auto.crrent_screenshot.save(file_path)
        self.logger.info(f"出了条大的！截图已保存至：{file_path}")

    # def count_yellow_blocks(self, image):
    #     # 黄色的确切HSV值
    #     """计算图像中黄色像素的数量"""
    #     # 将图像转换为HSV颜色空间
    #     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #
    #     # 创建黄色掩膜
    #     mask_yellow = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
    #
    #     # 查找轮廓
    #     contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #     # self.logger.debug(f"黄色块数为：{len(contours_yellow)}")
    #     # print(f"黄色块数为：{len(contours_yellow)}")
    #     #
    #     return len(contours_yellow)

    def is_spin_rod(self):
        """
        判断是否已经甩杆，看不到图标后表示已甩杆
        :return:
        """
        # self.auto.take_screenshot()
        if self.auto.find_element('app/resource/images/fishing/fish.png', 'image', threshold=0.6,
                                  crop=(29 / 1920, 212 / 1080, 116 / 1920, 292 / 1080), is_log=self.is_log,
                                  match_method=cv2.TM_CCOEFF_NORMED):
            return False
        return True

    def get_press_key(self):
        """
        自动获取钓鱼按键
        """
        text_results = self.auto.read_text_from_crop((1706 / 1920, 1024 / 1080, 1820 / 1920, 1066 / 1080),
                                                     is_log=self.is_log,
                                                     is_screenshot=True, extract=[(222, 230, 236), 128])
        # 根据文本内容模糊匹配键盘按键
        key_list = config.fish_key_list.value
        try:
            text = text_results[0][0]
            best_match = process.extractOne(text, key_list)
            self.logger.info(f"钓鱼按键识别最佳匹配为：{best_match}")
            key = best_match[0]
            self.press_key = key
            signalBus.updateFishKey.emit(key)
            config.set(config.LineEdit_fish_key, key)
        except Exception as e:
            self.logger.error(f"未识别出按键文字，请手动设置{e}")
            return False
        return True
