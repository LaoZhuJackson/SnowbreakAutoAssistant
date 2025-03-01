import re
import time

import cv2

from app.common.config import config
from app.common.image_utils import ImageUtils
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask
from app.modules.water_bomb.decision import Round, Status


class WaterBombModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        self.end_win = 1
        self.current_win = 0
        self.max_hp = 2  # 最大生命上限
        self.current_player_hp = 2  # 我方hp
        self.current_enemy_hp = 2  # 敌方hp
        self.remaining_live_bullet = 0  # 剩余实弹数
        self.remaining_blank_bullet = 0  # 剩余虚弹数
        self.player_items = []
        self.enemy_items = []
        self.bullet_list = []
        self.current_power = 1
        self.bullet_type = -1
        self.is_reversal = False
        self.sustain = False
        self.is_now_computer = False
        self.have_extra_shoot = False
        self.is_speed_up = False

        self.items_dict = {
            '活力宝石': 'gem_of_life',
            '看破墨镜': 'insight_sunglasses',
            '拘束手铐': 'handcuffs',
            '进阶枪管': 'advanced_barrel',
            '怪盗之手': 'hand_of_kaito',
            '逆转魔术': 'reverse_magic',
            '退弹布偶': 'unload_puppet',
            '重置之锤': 'reset_hammer',
        }
        self.normal_items = ['advanced_barrel', 'gem_of_life', 'handcuffs', 'reverse_magic', 'insight_sunglasses',
                             'unload_puppet']
        self.special_items = ['reset_hammer', 'hand_of_kaito']
        self.shoot_action = ['shoot_enemy', 'shoot_self']

        self.count_threshold = 0.7
        self.template_threshold = 0.7

        self.round_fight = Round()

    def run(self):
        self.count_threshold = config.Slider_count_threshold.value / 100
        self.template_threshold = config.Slider_template_threshold.value / 100
        self.end_win = config.SpinBox_water_win_times.value
        self.is_log = config.isLog.value

        self.enter_and_start()
        self.fight()

    def enter_and_start(self):
        """进水弹界面并选择心动嘉宾开始"""
        timeout = Timer(20).start()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element(['重新开始', '翻倍连战'], 'text',
                                      crop=(1670 / 1920, 954 / 1080, 1800 / 1920, 1000 / 1080), is_log=self.is_log,
                                      threshold=self.template_threshold):
                self.current_win = 0
                break
            if self.auto.find_element('本局对战少女', 'text', crop=(796 / 1920, 187 / 1080, 1103 / 1920, 261 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                self.current_win = 0
                break
            if self.auto.find_element('查看道具', 'text', crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                self.current_win = 0
                break
            if self.auto.click_element('点击屏幕继续', 'text', crop=(839 / 1920, 835 / 1080, 1075 / 1920, 900 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                self.current_win = 0
                break
            if self.auto.click_element('最佳记录', 'text', crop=(1279 / 1920, 619 / 1080, 1382 / 1920, 658 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                continue
            if self.auto.find_element(['心动水弹', 'F'], 'text',
                                      crop=(1025 / 1920, 663 / 1080, 1267 / 1920, 717 / 1080), is_log=self.is_log,
                                      threshold=self.template_threshold):
                self.auto.press_key('f')
                continue
            if timeout.reached():
                self.logger.error('进入心动水弹界面超时')
                break

    def fight(self):
        """对战阶段"""
        timeout = Timer(1200).start()
        self.is_speed_up = False
        is_open_items = False
        is_player_round = False
        current_strategy = ''

        while True:
            self.auto.take_screenshot()

            # todo 重开逻辑根据用户设置选择
            if self.auto.click_element('确定', 'text', crop=(1418 / 1920, 740 / 1080, 1509 / 1920, 791 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                continue
            if self.auto.click_element('重新开始', 'text', crop=(1670 / 1920, 954 / 1080, 1800 / 1920, 1000 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                self.logger.warn(f"对战失败，连胜中断")
                self.is_speed_up = False
                self.current_win = 0
                # 新一轮，重置计时器
                timeout.reset()
                self.round_fight = Round()
                time.sleep(1)
                continue
            if self.auto.click_element('翻倍连战', 'text', crop=(1670 / 1920, 954 / 1080, 1800 / 1920, 1000 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                self.current_win += 1
                self.logger.warn(f"对战胜利，当前连胜为：{self.current_win}")
                if self.current_win >= self.end_win:
                    self.logger.info(f'已达成{self.end_win}连胜')
                    self.auto.press_key('esc')
                    break
                self.is_speed_up = False
                # 新一轮，重置计时器
                timeout.reset()
                self.round_fight = Round()
                time.sleep(1)
                continue

            if self.auto.click_element('继续', 'text', crop=(839 / 1920, 835 / 1080, 1075 / 1920, 900 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                # self.update_items_list(is_player=True)
                continue
            if not self.is_speed_up:
                if not self.auto.find_element('app/resource/images/water_bomb/speed.png', 'image',
                                              crop=(1700 / 1920, 30 / 1080, 1800 / 1920, 130 / 1080),
                                              is_log=self.is_log, threshold=0.6,
                                              match_method=cv2.TM_CCOEFF_NORMED):
                    self.auto.move_click(1742 / self.auto.scale_x, 80 / self.auto.scale_y, press_time=0.1)
                    time.sleep(0.5)
                    continue
                else:
                    self.is_speed_up = True
            # 确认加速后进入主循环
            else:
                # 检查是否进入自己的回合
                if self.auto.find_element('查看道具', 'text', crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                          is_log=self.is_log, threshold=self.template_threshold):
                    is_player_round = True
                else:
                    is_player_round = False
                if is_player_round:
                    if current_strategy == '':
                        if self.auto.find_element('app/resource/images/water_bomb/head.png', 'image',
                                                  crop=(18 / 1920, 758 / 1080, 127 / 1920, 857 / 1080),
                                                  is_log=self.is_log, threshold=self.template_threshold):
                            is_open_items = True
                        else:
                            is_open_items = False
                        if not is_open_items:
                            self.auto.click_element('查看道具', 'text',
                                                    crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                                    is_log=self.is_log, threshold=self.template_threshold)
                            time.sleep(0.5)
                            continue
                        # 更新状态
                        self.update_items_list()
                        self.update_hp_and_bullet()
                        self.update_extra_status()
                        win_prob, current_strategy = self.get_action_and_probability()
                        self.logger.warn(self.get_status_dic())
                        self.logger.info(f'当前最佳操作为：{current_strategy}, 胜率为：{win_prob}')
                        if win_prob == 0:
                            self.restart()
                            continue
                        # if win_prob < 0.4 and 'reset_hammer' in self.player_items and len(self.player_items) > 1:
                        #     current_strategy = 'reset_hammer'
                        # print(self.get_status_dic())
                        continue
                    # 当前已经得到对应策略
                    else:
                        # 策略为使用普通道具
                        if current_strategy in self.normal_items:
                            if self.use_normal_item(current_strategy):
                                # 根据道具类型做对应的后处理
                                if current_strategy == 'gem_of_life':
                                    time.sleep(0.2)
                                elif current_strategy == 'insight_sunglasses':
                                    self.handle_insight_sunglasses()
                                elif current_strategy == 'handcuffs':
                                    time.sleep(0.5)
                                    if self.auto.find_element('不可继续', 'text',
                                                              crop=(1200 / 2560, 650 / 1440, 1600 / 2560, 800 / 1440),
                                                              take_screenshot=True):
                                        self.sustain = True
                                    self.have_extra_shoot = True
                                elif current_strategy == 'advanced_barrel':
                                    self.current_power = 2
                                elif current_strategy == 'reverse_magic':
                                    self.is_reversal = False if self.is_reversal else True
                                elif current_strategy == 'unload_puppet':
                                    time.sleep(0.2)
                            else:
                                current_strategy = ''
                                continue  # 使用道具失败，进入一轮新循环，重新判断检测
                        elif current_strategy == 'reset_hammer':
                            if self.handle_hammer():
                                pass
                            else:
                                self.logger.error('重置之锤使用失败')
                        # 策略为使用偷
                        elif '.' in current_strategy:
                            if self.handle_steal(current_strategy):
                                pass
                            else:
                                self.logger.error('偷道具失败')
                        # 策略为开枪
                        elif current_strategy in self.shoot_action:
                            if self.handle_shooting(current_strategy):
                                # 射击完成后子弹状态必为-1
                                self.bullet_type = -1
                            else:
                                self.logger.error('开枪失败')
                    # 不管上一个操作有没有处理成功，都需要清空策略后再继续
                    current_strategy = ''
                # npc回合
                else:
                    current_strategy = ''
                    continue
            if timeout.reached():
                self.logger.error('心动水弹对战超时')
                break

    def restart(self):
        timeout = Timer(20).start()
        end_flag = False
        while True:
            self.auto.take_screenshot()

            if self.auto.click_element('确定', 'text', crop=(1418 / 1920, 740 / 1080, 1509 / 1920, 791 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                end_flag = True
                time.sleep(2)
                continue
            if not end_flag:
                self.auto.press_key('esc')
                time.sleep(1)
            else:
                if self.auto.find_element('本局对战少女', 'text',
                                          crop=(796 / 1920, 187 / 1080, 1103 / 1920, 261 / 1080), is_log=self.is_log,
                                          threshold=self.template_threshold):
                    break
                if self.auto.find_element('查看道具', 'text', crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                          is_log=self.is_log, threshold=self.template_threshold):
                    break
                if self.auto.click_element('继续', 'text',
                                           crop=(839 / 1920, 835 / 1080, 1075 / 1920, 900 / 1080)):
                    break
                if self.auto.click_element('最佳记录', 'text', crop=(1279 / 1920, 619 / 1080, 1382 / 1920, 658 / 1080),
                                           is_log=self.is_log, threshold=self.template_threshold):
                    continue

            if timeout.reached():
                self.logger.error('重开超时')
                break
        self.is_speed_up = False
        self.logger.warn('胜率为0，选择重开')

    def handle_shooting(self, person):
        """处理开枪策略下的逻辑"""
        # todo 更新已经射击的子弹类型
        timeout = Timer(20).start()
        path = f'app/resource/images/water_bomb/{person}.png'
        while True:
            self.auto.take_screenshot()

            # 开完枪后回合转换
            if self.auto.find_element('更换', 'text', crop=(872 / 1920, 477 / 1080, 1120 / 1920, 550 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                self.is_reversal = False
                self.current_power = 1
                # 开完枪不管下一发是什么，都把子弹类型重置为-1
                self.bullet_type = -1
                return True
            # 开完枪之后进入新一轮道具画面
            if self.auto.click_element('继续', 'text', crop=(839 / 1920, 835 / 1080, 1075 / 1920, 900 / 1080),
                                       is_log=self.is_log, threshold=self.template_threshold):
                self.current_power = 1
                self.bullet_type = -1
                self.is_reversal = False
                return True
            # 开完枪后对局结束
            if self.auto.find_element(['重新开始', '翻倍连战'], 'text',
                                      crop=(1670 / 1920, 954 / 1080, 1800 / 1920, 1000 / 1080), is_log=self.is_log,
                                      threshold=self.template_threshold):
                self.have_extra_shoot = False
                self.sustain = False
                self.is_reversal = False
                self.current_power = 1
                self.bullet_type = -1
                return True
            if 'self' in person:
                if self.auto.find_element('追加', 'text', crop=(872 / 1920, 477 / 1080, 1120 / 1920, 550 / 1080),
                                          is_log=self.is_log, threshold=self.template_threshold):
                    self.is_reversal = False
                    self.current_power = 1
                    self.bullet_type = -1
                    return True
                if self.auto.click_element(path, 'image', crop=(1487 / 1920, 815 / 1080, 1723 / 1920, 900 / 1080),
                                           is_log=self.is_log, threshold=self.template_threshold,
                                           match_method=cv2.TM_CCOEFF_NORMED):
                    continue
            # 射击敌人
            else:
                if self.have_extra_shoot and self.auto.find_element('追加', 'text', crop=(
                        872 / 1920, 477 / 1080, 1120 / 1920, 550 / 1080), is_log=self.is_log,
                                                                    threshold=self.template_threshold):
                    self.have_extra_shoot = False
                    self.sustain = False
                    self.is_reversal = False
                    self.current_power = 1
                    self.bullet_type = -1
                    return True
                if self.auto.find_element('app/resource/images/water_bomb/gun.png', 'image',
                                          crop=(1494 / 1920, 352 / 1080, 1714 / 1920, 581 / 1080), is_log=self.is_log,
                                          threshold=self.template_threshold,
                                          match_method=cv2.TM_CCOEFF_NORMED):
                    self.auto.move_click(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y))
                    continue
                if self.auto.click_element(path, 'image', crop=(1640 / 1920, 900 / 1080, 1880 / 1920, 994 / 1080),
                                           is_log=self.is_log, threshold=self.template_threshold,
                                           match_method=cv2.TM_CCOEFF_NORMED):
                    continue

            if timeout.reached():
                self.logger.error(f'{person}超时')
                return False

    def handle_insight_sunglasses(self):
        """用完透视眼镜后的后处理"""
        timeout = Timer(20).start()
        break_flag = False
        while True:
            self.auto.take_screenshot()

            crop_image = self.auto.get_crop_form_first_screenshot(
                crop=(1470 / 2560, 1290 / 1440, 1640 / 2560, 1364 / 1440))
            self.auto.perform_ocr(image=crop_image, is_log=self.is_log)
            if self.auto.ocr_result:
                for ocr_result in self.auto.ocr_result:
                    if '空' in ocr_result[0] or self.auto.find_element('app/resource/images/water_bomb/blank.png',
                                                                       'image', crop=(
                                    1470 / 2560, 1290 / 1440, 1640 / 2560, 1364 / 1440),
                                                                       match_method=cv2.TM_CCOEFF_NORMED,
                                                                       is_log=self.is_log,
                                                                       threshold=self.template_threshold):
                        self.bullet_type = 0
                        return
                    elif '水' in ocr_result[0] or self.auto.find_element('app/resource/images/water_bomb/live.png',
                                                                         'image', crop=(
                                    1470 / 2560, 1290 / 1440, 1640 / 2560, 1364 / 1440),
                                                                         match_method=cv2.TM_CCOEFF_NORMED,
                                                                         is_log=self.is_log,
                                                                         threshold=self.template_threshold):
                        self.bullet_type = 1
                        return
            else:
                if break_flag:
                    self.logger.error('看破墨镜后处理未识别到任何文字')
                    break
                else:
                    break_flag = True
                    time.sleep(0.5)
                    continue

            if timeout.reached():
                self.logger.error('看破墨镜后处理超时')
                break

    def handle_steal(self, item_name):
        """使用偷"""
        self.use_normal_item(item_name.split('.')[0])
        steal_item = item_name.split('.')[-1]
        if self.select_and_steal(steal_item):
            return True
        return False

    def handle_hammer(self):
        """使用万宝槌"""
        self.use_normal_item('reset_hammer')

        if self.select_and_reset():
            return True
        return False

    def select_and_reset(self):
        timeout = Timer(30).start()
        select_flag = False
        finish_flag = False
        items_list = self.player_items.copy()
        # 去掉一个reset_hammer
        items_list.remove('reset_hammer')
        index = 0
        top_left, bottom_right = None, None

        self.scroll_to_bottom()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('查看道具', 'text', crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                return True
            if self.auto.find_image_and_count(
                    self.auto.get_crop_form_first_screenshot(crop=(440 / 1920, 332 / 1080, 1510 / 1920, 878 / 1080)),
                    'app/resource/images/water_bomb/steal_select.png', threshold=self.count_threshold,
                    is_log=self.is_log) == len(
                items_list):
                select_flag = True
            else:
                select_flag = False
            if select_flag and not self.auto.find_element('确定', 'text',
                                                          crop=(887 / 1920, 821 / 1080, 967 / 1920, 863 / 1080),
                                                          is_log=self.is_log, threshold=self.template_threshold):
                finish_flag = True
            if finish_flag and not self.auto.find_element('查看道具', 'text',
                                                          crop=(113 / 1920, 984 / 1080, 220 / 1920, 1020 / 1080),
                                                          is_log=self.is_log, threshold=self.template_threshold):
                self.auto.click_element('关闭', 'text', crop=(887 / 1920, 821 / 1080, 967 / 1920, 863 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold)
                continue
            if not select_flag:
                if top_left and bottom_right:
                    if self.auto.find_element('app/resource/images/water_bomb/steal_select.png', 'image', crop=(
                            top_left[0] / 1920, top_left[1] / 1080, bottom_right[0] / 1920, bottom_right[1] / 1080),
                                              is_log=self.is_log, threshold=self.template_threshold,
                                              match_method=cv2.TM_CCOEFF_NORMED):
                        index += 1
                        if index >= len(items_list):
                            return True
                path = f'app/resource/images/water_bomb/{items_list[index]}_steal.png'
                result = self.auto.find_element(path, 'image', crop=(440 / 1920, 332 / 1080, 1510 / 1920, 878 / 1080),
                                                is_log=self.is_log, threshold=self.template_threshold,
                                                match_method=cv2.TM_CCOEFF_NORMED)
                if result is not None:
                    top_left, bottom_right = result
                    self.auto.click_element_with_pos((top_left, bottom_right))
                    time.sleep(1)
                    continue
            else:
                self.auto.click_element('确定', 'text', crop=(887 / 1920, 821 / 1080, 967 / 1920, 863 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold)
                time.sleep(1)

            if timeout.reached():
                self.logger.error('使用重置之锤超时')
                return False

    def scroll_to_bottom(self):
        self.auto.mouse_scroll(int(960 / self.auto.scale_x), int(540 / self.auto.scale_y), -550)

    def select_and_steal(self, steal_item):
        """选择物品然后偷"""
        timeout = Timer(20).start()
        path = f'app/resource/images/water_bomb/{steal_item}_steal.png'
        select_flag = False

        self.scroll_to_bottom()
        while True:
            self.auto.take_screenshot()

            if self.auto.find_element('确定', 'text', crop=(887 / 1920, 821 / 1080, 967 / 1920, 863 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                self.auto.click_element(path, 'image', crop=(440 / 1920, 332 / 1080, 1510 / 1920, 878 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold,
                                        match_method=cv2.TM_CCOEFF_NORMED)
                self.auto.click_element('确定', 'text', crop=(887 / 1920, 821 / 1080, 967 / 1920, 863 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold)
            else:
                return True

            if timeout.reached():
                self.logger.error('偷道具超时')
                return False

    def use_normal_item(self, item_name):
        """根据物品名使用可以直接使用的道具"""
        timeout = Timer(20).start()
        appear_use_button = False
        path = f'app/resource/images/water_bomb/{item_name}.png'
        while True:
            self.auto.take_screenshot()

            if appear_use_button and not self.auto.find_element('使用', 'text',
                                                                crop=(500 / 1920, 700 / 1080, 562 / 1920, 735 / 1080),
                                                                is_log=self.is_log, threshold=self.template_threshold):
                time.sleep(1)
                return True
            if self.auto.find_element('使用', 'text', crop=(500 / 1920, 700 / 1080, 562 / 1920, 735 / 1080),
                                      is_log=self.is_log, threshold=self.template_threshold):
                appear_use_button = True
            if not appear_use_button:
                self.auto.click_element(path, 'image', crop=(145 / 1920, 758 / 1080, 665 / 1920, 852 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold,
                                        match_method=cv2.TM_CCOEFF_NORMED)
                time.sleep(0.5)
                continue
            else:
                self.auto.click_element('使用', 'text', crop=(500 / 1920, 700 / 1080, 562 / 1920, 735 / 1080),
                                        is_log=self.is_log, threshold=self.template_threshold)
                time.sleep(0.5)

            if timeout.reached():
                self.logger.error(f'使用道具{item_name}超时')
                return False

    def update_extra_status(self):
        """检查当前对面是否被铐上手铐"""
        if self.auto.find_element('app/resource/images/water_bomb/is_handcuffs.png', 'image',
                                  threshold=self.template_threshold,
                                  crop=(980 / 1920, 30 / 1080, 1250 / 1920, 150 / 1080), is_log=self.is_log,
                                  match_method=cv2.TM_CCOEFF_NORMED):
            self.sustain = True
            # if not self.have_extra_shoot:
            #     self.sustain = False
        else:
            self.sustain = False

    def update_hp_and_bullet(self):
        # self.auto.take_screenshot()

        player_hp_screenshot = self.auto.get_crop_form_first_screenshot(
            (683 / 1920, 131 / 1080, 942 / 1920, 186 / 1080))
        # player_hp_screenshot = self.auto.resize_image(player_hp_screenshot,(self.auto.scale_x,self.auto.scale_y))
        enemy_hp_screenshot = self.auto.get_crop_form_first_screenshot(
            (943 / 1920, 131 / 1080, 1237 / 1920, 186 / 1080))
        # enemy_hp_screenshot = self.auto.resize_image(enemy_hp_screenshot, (self.auto.scale_x, self.auto.scale_y))
        self.current_player_hp = self.auto.find_image_and_count(player_hp_screenshot,
                                                                'app/resource/images/water_bomb/hp.png',
                                                                threshold=self.count_threshold, is_log=self.is_log)
        no_hp = self.auto.find_image_and_count(player_hp_screenshot, 'app/resource/images/water_bomb/no_hp.png',
                                               threshold=self.count_threshold, is_log=self.is_log)
        self.max_hp = self.current_player_hp + no_hp
        self.current_enemy_hp = self.auto.find_image_and_count(enemy_hp_screenshot,
                                                               'app/resource/images/water_bomb/hp.png',
                                                               threshold=self.count_threshold, is_log=self.is_log)

        # 更新两种子弹状态
        is_num = True
        if self.auto.find_element(f'app/resource/images/water_bomb/q.png', 'image',
                                  crop=(2000 / 2560, 1280 / 1440, 2137 / 2560, 1397 / 1440), is_log=self.is_log,
                                  threshold=self.template_threshold,
                                  extract=[(255, 255, 255), 128],
                                  match_method=cv2.TM_CCOEFF_NORMED):
            # 在用了逆转后点了开始水弹
            if self.remaining_live_bullet == 0 and self.remaining_blank_bullet == 0:
                self.remaining_blank_bullet = self.remaining_live_bullet = 1
            is_num = False
        if is_num:
            for i in range(0, 5):
                if self.auto.find_element(f'app/resource/images/water_bomb/{i}.png', 'image',
                                          crop=(2000 / 2560, 1280 / 1440, 2137 / 2560, 1397 / 1440),
                                          threshold=self.template_threshold,
                                          is_log=self.is_log,
                                          extract=[(255, 255, 255), 128],
                                          match_method=cv2.TM_CCOEFF_NORMED):
                    self.remaining_live_bullet = i
                    break
            for i in range(0, 5):
                if self.auto.find_element(f'app/resource/images/water_bomb/{i}.png', 'image',
                                          crop=(2132 / 2560, 1300 / 1440, 2300 / 2560, 1397 / 1440),
                                          threshold=self.template_threshold,
                                          is_log=self.is_log,
                                          extract=[(255, 255, 255), 128],
                                          match_method=cv2.TM_CCOEFF_NORMED):
                    self.remaining_blank_bullet = i
                    break
        if self.remaining_live_bullet == 0:
            self.bullet_type = 0
        elif self.remaining_blank_bullet == 0:
            self.bullet_type = 1

        self.logger.info(f"当前血量上限：{self.max_hp}")
        self.logger.info(f"当前玩家血量：{self.current_player_hp}，对方血量：{self.current_enemy_hp}")
        self.logger.info(f"当前水弹数量：{self.remaining_live_bullet}，空弹数量：{self.remaining_blank_bullet}")
        # time.sleep(5)

    def update_items_list(self):
        """
        更新敌我道具列表
        :return:
        """
        # self.auto.take_screenshot()

        player_area = (145 / 1920, 758 / 1080, 665 / 1920, 852 / 1080)
        enemy_area = (136 / 1920, 856 / 1080, 665 / 1920, 953 / 1080)

        self.player_items = self.get_items(crop=player_area)
        self.enemy_items = self.get_items(crop=enemy_area)
        self.logger.info(f"玩家道具：{self.player_items}")
        self.logger.info(f"对方道具：{self.enemy_items}")

    def get_items(self, crop):
        """根据区域获取道具"""
        current_items = []
        path_list = [
            'app/resource/images/water_bomb/advanced_barrel.png',
            'app/resource/images/water_bomb/unload_puppet.png',
            'app/resource/images/water_bomb/gem_of_life.png',
            'app/resource/images/water_bomb/reset_hammer.png',
            'app/resource/images/water_bomb/handcuffs.png',
            'app/resource/images/water_bomb/reverse_magic.png',
            'app/resource/images/water_bomb/hand_of_kaito.png',
            'app/resource/images/water_bomb/insight_sunglasses.png'
        ]

        crop_screenshot = self.auto.get_crop_form_first_screenshot(crop)
        for path in path_list:
            # if self.auto.find_element(path,'image',crop=crop):
            for i in range(self.auto.find_image_and_count(crop_screenshot, path, threshold=self.count_threshold,
                                                          is_log=self.is_log)):
                key = path.split('/')[-1].split('.')[0]
                current_items.append(key)
        return current_items

    def get_status_dic(self):
        """获取当前所有状态，并返回一个字典"""
        status_dict = {
            'maxhp': int(self.max_hp),
            'shp': int(self.current_player_hp),
            'ehp': int(self.current_enemy_hp),
            'live': int(self.remaining_live_bullet),
            'blank': int(self.remaining_blank_bullet),
            'fired': self.bullet_list,
            'sitems': self.player_items,
            'eitems': self.enemy_items,
            'power': self.current_power,
            'bullet': self.bullet_type,
            'reversal': self.is_reversal,
            'extra_opp': self.sustain,
            'computer': self.is_now_computer,
        }
        return status_dict

    # 定义一个函数来更新状态并获取 action 和胜率
    def get_action_and_probability(self):
        """通过传入字典更新整个status对象，然后调用方法得到action"""
        status_dict = self.get_status_dic()
        # 更新 Status 对象
        status = Status.from_dict(status_dict)

        # 调用 win_prob 方法
        # print(status_dict)
        win_prob, strategy = self.round_fight.optimal_strategy(status)
        return win_prob, strategy
