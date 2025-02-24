import functools
import math
import threading
import time
import traceback

import cv2
import numpy as np
import win32gui

from app.common.config import config
from app.common.image_utils import ImageUtils
from app.common.logger import logger
from app.common.singleton import SingletonMeta
from app.common.utils import random_rectangle_point, add_noise
from app.modules.automation.input import Input
from app.modules.automation.screenshot import Screenshot
from app.modules.automation.timer import Timer
from app.modules.ocr import ocr


def atoms(func):
    """
    用于各种原子操作中实现立即停止的装饰器
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 检查self.running是否为false
        if not args[0].running:
            raise Exception("已停止")
        else:
            # 判断是否暂停
            if args[0].pause:
                # 每次执行完原子函数后，等待外部条件重新开始
                args[0].pause_event.wait()  # 等待外部触发继续执行
        return func(*args, **kwargs)

    return wrapper


class Automation:
    """
    自动化管理类，用于管理与游戏窗口相关的自动化操作。
    """

    # _screenshot_interval = Timer(0.1)

    def __init__(self, window_title, window_class, logger):
        """
        :param window_title: 游戏窗口的标题。
        :param window_class: 是启动器还是游戏窗口
        :param logger: 用于记录日志的Logger对象，可选参数。
        """
        # 启动器截图和操作的窗口句柄不同
        self.screenshot_hwnd = None
        self.window_title = window_title
        self.window_class = window_class
        self.is_starter = window_class != config.LineEdit_game_class.value
        self.logger = logger
        self.hwnd = self.get_hwnd()
        self.screenshot = Screenshot(self.logger)
        # 当前截图
        self.current_screenshot = None
        # 保存状态机的第一张截图，为了让current_screenshot可以肆无忌惮的裁切
        self.first_screenshot = None
        self.scale_x = 1
        self.scale_y = 1
        self.relative_pos = None
        self.ocr_result = None

        self.running = True
        self.pause = False
        self.pause_event = threading.Event()  # 用来控制暂停

        self._init_input()

    def _init_input(self):
        self.input_handler = Input(self.hwnd, self.logger)
        # 鼠标部分
        self.move_click = self.input_handler.move_click
        self.mouse_click = self.input_handler.mouse_click
        self.mouse_down = self.input_handler.mouse_down
        self.mouse_up = self.input_handler.mouse_up
        self.mouse_scroll = self.input_handler.mouse_scroll
        self.move_to = self.input_handler.move_to
        # 按键部分
        self.press_key = self.input_handler.press_key
        self.key_down = self.input_handler.key_down
        self.key_up = self.input_handler.key_up

    def enumerate_child_windows(self, parent_hwnd):
        def callback(handle, windows):
            windows.append(handle)
            return True

        child_windows = []
        win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
        return child_windows

    def get_hwnd(self):
        """根据传入的窗口名和类型确定可操作的句柄"""
        hwnd = win32gui.FindWindow(None, self.window_title)
        handle_list = []
        if hwnd:
            handle_list.append(hwnd)
            self.screenshot_hwnd = hwnd
            handle_list.extend(self.enumerate_child_windows(hwnd))
            for handle in handle_list:
                class_name = win32gui.GetClassName(handle)
                if class_name == self.window_class:
                    # 找到需要的窗口句柄
                    self.logger.info(f"找到窗口 {self.window_title} 的句柄为：{handle}")
                    return handle
        else:
            raise ValueError(f"未找到{self.window_title}的句柄，请确保对应窗口已打开")

    @atoms
    def take_screenshot(self, crop=(0, 0, 1, 1)):
        """
        捕获游戏窗口的截图。
        :param crop: 截图的裁剪区域，格式为(x1, y1, width, height)，默认为全屏。
        :return: 成功时返回截图及其位置和缩放因子，失败时抛出异常。
        """
        try:
            result = self.screenshot.screenshot(self.screenshot_hwnd, (0, 0, 1, 1), self.is_starter)
            if result:
                self.first_screenshot, self.scale_x, self.scale_y, self.relative_pos = result
                if crop != (0, 0, 1, 1):
                    self.current_screenshot, self.relative_pos = ImageUtils.crop_image(self.first_screenshot, crop,
                                                                                       self.hwnd)
                else:
                    self.current_screenshot = self.first_screenshot
                # self.logger.debug(f"缩放比例为：({self.scale_x},{self.scale_y})")
                return result
            else:
                # 为none的时候已经在screenshot中log了，此处无需再log
                self.current_screenshot = None
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"截图失败：{e}")

    def calculate_positions(self, template, max_loc):
        """
        找到图片后计算相对位置，input_handler接收的均为相对窗口的相对坐标，所以这里要返回的也是相对坐标
        :param template:
        :param max_loc:
        :return:
        """
        try:
            channels, width, height = template.shape[::-1]
        except:
            width, height = template.shape[::-1]

        top_left = (
            int(max_loc[0] + self.relative_pos[0]),
            int(max_loc[1] + self.relative_pos[1]),
        )
        bottom_right = (
            top_left[0] + width,
            top_left[1] + height,
        )
        return top_left, bottom_right

    def find_image_element(self, target, threshold, match_method=cv2.TM_SQDIFF_NORMED, extract=None, is_log=False):
        """
        寻找图像
        :param is_log:
        :param extract:
        :param match_method: 模版匹配使用的方法
        :param target: 图片路径
        :param threshold: 置信度
        :return: 左上，右下相对坐标，寻找到的目标的置信度
        """
        try:
            # 获取透明部分的掩码（允许模版图像有透明处理）
            mask = ImageUtils.get_template_mask(target)
            template = cv2.imread(target)  # 读取模板图片
            if mask is not None:
                matchVal, matchLoc = ImageUtils.match_template(self.current_screenshot, template, mask,
                                                               (self.scale_x, self.scale_y),
                                                               match_method=match_method, extract=extract)
            else:
                matchVal, matchLoc = ImageUtils.match_template(self.current_screenshot, template,
                                                               scale=(self.scale_x, self.scale_y),
                                                               match_method=match_method, extract=extract)
            if is_log:
                self.logger.debug(f"目标图片：{target.replace('app/resource/images/', '')} 相似度：{matchVal:.2f}")
            if not math.isinf(matchVal) and (threshold is None or matchVal >= threshold):
                top_left, bottom_right = self.calculate_positions(template, matchLoc)
                return top_left, bottom_right, matchVal
            if is_log:
                self.logger.debug(f"没有找到相似度大于 {threshold} 的结果")
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"寻找图片出错：{e}")
        return None, None, None

    @atoms
    def perform_ocr(self, extract: list = None, image=None, allowlist=None, is_log=False):
        """执行OCR识别，并更新OCR结果列表。如果未识别到文字，保留ocr_result为一个空列表。"""
        try:
            # image=None时
            if image is None:
                # ImageUtils.show_ndarray(self.current_screenshot)
                self.ocr_result = ocr.run(self.current_screenshot, extract, allowlist=allowlist, is_log=is_log)
            # 传入特定的图片进行ocr识别
            else:
                # ImageUtils.show_ndarray(image)
                self.ocr_result = ocr.run(image, extract, allowlist=allowlist, is_log=is_log)
            if not self.ocr_result:
                # self.logger.info(f"未识别出任何文字")
                self.ocr_result = []
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"OCR识别失败：{e}")
            self.ocr_result = []  # 确保在异常情况下，ocr_result为列表类型

    def calculate_text_position(self, result):
        """
        计算文本所在的相对位置
        :param result: 格式=['适龄提示', 1.0, [[10.0, 92.0], [71.0, 106.0]]],单条结果
        :return: 左上，右下相对坐标
        """
        result_pos = result[2]
        result_width = result_pos[1][0] - result_pos[0][0]
        result_height = result_pos[1][1] - result_pos[0][1]

        # self.relative_pos格式：(800, 480, 1600, 960),转回用户尺度后再加相对窗口坐标
        top_left = (
            self.relative_pos[0] + result_pos[0][0],
            self.relative_pos[1] + result_pos[0][1]
        )
        bottom_right = (
            top_left[0] + result_width,
            top_left[1] + result_height,
        )
        # print(f"{top_left=}")
        # print(f"{bottom_right=}")
        return top_left, bottom_right

    def is_text_match(self, text, targets, include):
        """
        判断文本是否符合搜索条件，并返回匹配的文本。
        :param text: OCR识别出的文本。
        :param targets: 目标文本列表。
        :param include: 是否包含目标字符串。
        :return: (是否匹配, 匹配的目标文本)
        """
        if include:
            for target in targets:
                if target in text:
                    return True, target  # 直接返回匹配成功及匹配的目标文本
            return False, None  # 如果没有匹配，返回False和None
        else:
            return text in targets, text if text in targets else None

    def search_text_in_ocr_results(self, targets, include):
        """从ocr识别结果中找目标文字"""
        for result in self.ocr_result:
            match, matched_text = self.is_text_match(result[0], targets, include)
            if match:
                # self.matched_text = matched_text  # 更新匹配的文本变量
                # self.logger.info(f"目标文字：{matched_text} 相似度：{result[1]:.2f}")
                return self.calculate_text_position(result)
        # self.logger.info(f"目标文字：{', '.join(targets)} 未找到匹配文字")
        return None, None

    def find_text_element(self, target, include, need_ocr=True, extract=None, is_log=False):
        """

        :param is_log:
        :param target:
        :param include:
        :param need_ocr:
        :param extract: 是否提取文字，[(文字rgb颜色),threshold数值]
        :return:
        """
        target_texts = [target] if isinstance(target, str) else list(target)  # 确保目标文本是列表格式
        if need_ocr:
            self.perform_ocr(extract, is_log=is_log)
        return self.search_text_in_ocr_results(target_texts, include)

    @atoms
    def find_element(self, target, find_type: str, threshold: float = 0.7, crop: tuple = (0, 0, 1, 1),
                     take_screenshot=False, include: bool = True, need_ocr: bool = True, extract: list = None,
                     match_method=cv2.TM_SQDIFF_NORMED, is_log=False):
        """
        寻找元素
        :param is_log:
        :param match_method: 模版匹配方法
        :param target:
        :param find_type:
        :param threshold:
        :param crop:
        :param take_screenshot:
        :param include:
        :param need_ocr:
        :param extract:
        :return: 查找成功返回（top_left,bottom_right），失败返回None
        """
        top_left = bottom_right = image_threshold = None
        if take_screenshot:
            # 调用take_screenshot更新self.current_screenshot,self.scale_x,self.scale_y,self.relative_pos
            screenshot_result = self.take_screenshot(crop)
            if not screenshot_result:
                return None
        else:
            # 不截图的时候做相应的裁切，使外部可以不写参数
            if self.current_screenshot is not None:
                # 更新当前裁切后的截图和相对位置坐标
                # ImageUtils.show_ndarray(self.current_screenshot, 'before_current')
                self.current_screenshot, self.relative_pos = ImageUtils.crop_image(self.first_screenshot, crop,
                                                                                   self.hwnd)
                # ImageUtils.show_ndarray(self.current_screenshot, 'after_current')
            else:
                self.logger.error(f"当前没有current_screenshot,裁切失败")
        if find_type in ['image', 'text', 'image_threshold']:
            if find_type == 'image':
                top_left, bottom_right, image_threshold = self.find_image_element(target, threshold,
                                                                                  match_method=match_method,
                                                                                  extract=extract, is_log=is_log)
            elif find_type == 'text':
                top_left, bottom_right = self.find_text_element(target, include, need_ocr, extract, is_log)
            if top_left and bottom_right:
                if find_type == 'image_threshold':
                    return image_threshold
                return top_left, bottom_right
        else:
            raise ValueError(f"错误的类型{find_type}")
        return None

    def click_element_with_pos(self, pos, action="move_click", offset=(0, 0), n=3, is_calculate=True):
        """
        根据左上和右下坐标确定点击位置并执行点击
        :param is_calculate: 是否计算点击坐标，当传入的是（top_left,bottom_right）时需要计算，传入的是（x,y）时不需要
        :param pos: （top_left,bottom_right）|(x,y)
        :param action: 执行的动作类型
        :param offset: x,y的偏移量
        :param n: 聚拢值，越大越聚拢
        :return: None
        """
        # 范围内正态分布取点
        if is_calculate:
            x, y = random_rectangle_point(pos, n)
        else:
            x, y = pos
        # print(f"{x=},{y=}")
        # 加上手动设置的偏移量
        click_x = x + offset[0]
        click_y = y + offset[1]
        # 动作到方法的映射
        action_map = {
            "mouse_click": self.mouse_click,
            "down": self.mouse_down,
            "move": self.move_to,
            "move_click": self.move_click,
        }
        if action in action_map:
            action_map[action](click_x, click_y)
            # print(f"点击{click_x},{click_y}")
        else:
            raise ValueError(f"未知的动作类型: {action}")
        return True

    def click_element(self, target, find_type: str, threshold: float = 0.7, crop: tuple = (0, 0, 1, 1),
                      take_screenshot=False, include: bool = True, need_ocr: bool = True, extract: list = None,
                      action: str = 'move_click', offset: tuple = (0, 0), n: int = 3,
                      match_method=cv2.TM_SQDIFF_NORMED, is_log=False):
        """
        寻找目标位置，并在位置做出对应action
        :param is_log:
        :param match_method: 模版匹配方法
        :param n: 正态分布随机获取点的居中程度，越大越居中
        :param target: 寻找目标
        :param find_type: 寻找类型
        :param threshold: 置信度
        :param crop: 截图区域，take_screenshot为任何值crop都生效，为true时直接得到裁剪后的截图，为false时将根据crop对current_screenshot进行二次裁剪
        :param take_screenshot: 是否截图
        :param include: 是否允许target含于ocr结果
        :param need_ocr: 是否ocr
        :param extract: 是否使截图转换成白底黑字，只有find_type=="text"且需要ocr的时候才生效，[(文字rgb颜色),threshold数值]
        :param action: 默认假后台点击，可选'mouse_click','mouse_down','move','move_click'
        :param offset: 点击位置偏移量，默认不偏移
        :return:
        """
        coordinates = self.find_element(target, find_type, threshold, crop, take_screenshot, include, need_ocr, extract,
                                        match_method, is_log)
        # print(f"{coordinates=}")
        if coordinates:
            return self.click_element_with_pos(coordinates, action, offset, n)
        return False

    @atoms
    def find_target_near_source(self, target, source_pos, need_update_ocr: bool = True, crop=(0, 0, 1, 1), include=True,
                                n=30, is_log=False):
        """
        查找距离源最近的目标文本的中心坐标。
        :param is_log:
        :param n: 聚拢度
        :param include: 是否包含
        :param target:目标文本
        :param need_update_ocr: 是否需要重新截图更新self.ocr_result
        :param crop: 截图区域,只有need_update_ocr为true时才生效
        :param source_pos:源的位置坐标，用于计算与目标的距离,格式：（x,y）
        :return:相对窗口的最近目标文本的中心坐标，格式(x,y)
        """
        target_texts = [target] if isinstance(target, str) else list(target)  # 确保目标文本是列表格式
        min_distance = float('inf')
        target_pos = None
        if need_update_ocr:
            # 更新self.current_screenshot
            self.take_screenshot(crop)
            # 更新self.ocr_result
            self.perform_ocr(is_log=is_log)
        for result in self.ocr_result:
            text = result[0]
            match, matched_text = self.is_text_match(text, target_texts, include)
            if match:
                # 计算出相对屏幕的坐标后再计算中心坐标，用于后续与传入的source_pos计算距离
                result_x, result_y = random_rectangle_point(self.calculate_text_position(result), n)
                # 计算距离
                distance = math.sqrt((source_pos[0] - result_x) ** 2 + (source_pos[1] - result_y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    target_pos = (result_x, result_y)
        if target_pos is None:
            # self.logger.error(f"目标文字：{target_texts} 未找到匹配文字")
            return None, min_distance
        return target_pos, min_distance

    def stop(self):
        self.running = False

    def reset(self):
        self.running = True

    def pause(self):
        self.pause = True
        # 清除事件，线程会暂停
        self.pause_event.clear()

    def resume(self):
        self.pause = False
        # 设置事件，线程会继续
        self.pause_event.set()

    def get_crop_form_first_screenshot(self, crop=(0, 0, 1, 1), is_resize=True):
        crop_image, _ = ImageUtils.crop_image(self.first_screenshot, crop, self.hwnd)
        if is_resize:
            crop_image = ImageUtils.resize_image(crop_image, (self.scale_x, self.scale_y))
        return crop_image

    @atoms
    def read_text_from_crop(self, crop=(0, 0, 1, 1), extract=None, is_screenshot=False, allowlist=None, is_log=False):
        """
        通过crop找对应的文本内容
        :param is_log:
        :param allowlist: 限制 OCR 模型识别的字符集
        :param crop: 查找区域
        :param extract: 指定提取背景
        :param is_screenshot: 是否截图
        :return: ocr识别内容（格式化后的）
        """
        if is_screenshot:
            self.take_screenshot()
        crop_image, _ = ImageUtils.crop_image(self.first_screenshot, crop, self.hwnd)
        # ImageUtils.show_ndarray(crop_image)
        self.perform_ocr(image=crop_image, extract=extract, allowlist=allowlist, is_log=is_log)
        return self.ocr_result

    @atoms
    def find_image_and_count(self, target, template, threshold=0.6, extract=None):
        """在屏幕截图中查找与目标图片相似的图片，并计算匹配数量。

        参数:
        - target: 需要找模板图片的图片。
        - template: 模板图片。
        - threshold: 匹配阈值。
        - extract: 是否提取目标颜色，[(对应的rgb颜色),threshold数值]

        返回:
        - 匹配的数量，或在出错时返回 None。
        """
        try:
            if isinstance(target, str):
                target = cv2.imread(target)
            if isinstance(template, str):
                template = cv2.imread(template)
            # 将图片从BGR格式转换为RGB格式
            target_rgb = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
            if extract is not None:
                rbg = extract[0]
                thr = extract[1]
                target_rgb = ImageUtils.extract_letters(target_rgb, rbg, thr)
                template_rgb = ImageUtils.extract_letters(template, rbg, thr)

            return ImageUtils.count_template_matches(target_rgb, template_rgb, threshold)
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"寻找图片并计数出错：{e}")
            return None


# 用于保存是否已实例化
auto_starter = None
auto_game = None


def instantiate_automation(auto_type: str):
    global auto_starter, auto_game

    # 尝试实例化 starter
    if auto_type == 'starter':
        try:
            auto_starter = Automation(config.LineEdit_starter_name.value, config.LineEdit_starter_class.value, logger)
        except Exception as e:
            logger.warn(f"未能成功实例化starter：{e}")

    elif auto_type == 'game':
        try:
            auto_game = Automation(config.LineEdit_game_name.value, config.LineEdit_game_class.value, logger)
        except Exception as e:
            logger.warn(f"未能成功实例化game：{e}")
    else:
        try:
            auto_starter = Automation(config.LineEdit_starter_name.value, config.LineEdit_starter_class.value, logger)
        except Exception as e:
            logger.warn(f"未能成功实例化starter：{e}")
        try:
            auto_game = Automation(config.LineEdit_game_name.value, config.LineEdit_game_class.value, logger)
        except Exception as e:
            logger.warn(f"未能成功实例化game：{e}")


# 调用实例化方法
instantiate_automation('all')

if __name__ == '__main__':
    pass
