import ctypes
import time

import win32api
import win32con
import win32gui

from app.common.config import config
from app.common.logger import logger
from app.common.signal_bus import signalBus
from app.modules.automation.automation import Automation
from app.modules.automation.timer import Timer


class BaseTask:
    def __init__(self):
        self.logger = logger
        self.auto = None

    def run(self):
        pass

    def stop(self):
        self.auto.stop()

    def determine_screen_ratio(self, hwnd):
        """判断句柄对应窗口是否为16:9"""
        # 获取窗口客户区尺寸（不含边框和标题栏）
        client_rect = win32gui.GetClientRect(hwnd)
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]

        # 避免除零错误
        if client_height == 0:
            self.logger.warning("窗口高度为0，无法计算比例")
            return False

        # 计算实际宽高比
        actual_ratio = client_width / client_height
        # 16:9的标准比例值
        target_ratio = 16 / 9

        # 允许1%的容差范围
        tolerance = 0.05
        is_16_9 = abs(actual_ratio - target_ratio) <= (target_ratio * tolerance)

        # 记录结果
        status = "符合" if is_16_9 else "不符合"
        self.logger.warn(
            f"窗口客户区尺寸: {client_width}x{client_height} "
            f"({actual_ratio:.3f}:1), {status}16:9标准比例"
        )
        # 如果用户设置了自动缩放才执行以下命令
        if config.autoScaling.value:
            # 排除缩放干扰
            ctypes.windll.user32.SetProcessDPIAware()
            # 若不符合比例则进行窗口调整
            if not is_16_9:
                # 获取原始窗口矩形
                original_rect = win32gui.GetWindowRect(hwnd)
                config.set(config.is_resize, original_rect)

                # 获取窗口边框尺寸
                window_rect = win32gui.GetWindowRect(hwnd)
                border_width = (window_rect[2] - window_rect[0] - client_width) // 2
                title_height = (window_rect[3] - window_rect[1] - client_height) - border_width

                # 计算所需的总窗口尺寸
                target_client_width = 1940
                target_client_height = 1135

                # 设置窗口位置和大小
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOP,
                    -10,  # 左上角X坐标
                    -48,  # 左上角Y坐标
                    target_client_width,
                    target_client_height,
                    win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                )

                self.logger.warn(f"已调整窗口到 {target_client_width}x{target_client_height} 并贴齐左上角")
            else:
                # 获取主显示器分辨率
                screen_width = win32api.GetSystemMetrics(0)
                screen_height = win32api.GetSystemMetrics(1)
                if client_width < screen_width:
                    # 获取原始窗口矩形
                    original_rect = win32gui.GetWindowRect(hwnd)
                    config.set(config.is_resize, original_rect)
                    # 设置窗口位置和大小
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_TOP,
                        -10,  # 左上角X坐标
                        -48,  # 左上角Y坐标
                        client_width,
                        client_height,
                        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
                    )
                    self.logger.warn(f"已调整窗口贴齐左上角")
        else:
            self.logger.warn(f"设置中未开启自动缩放，请手动调整窗口大小并将窗口贴在左上角或在设置中开启自动缩放")

        return is_16_9

    def init_auto(self, name):
        if config.server_interface.value != 2:
            game_name = '尘白禁区'
            game_class = 'UnrealWindow'
        else:
            game_name = 'Snowbreak: Containment Zone'  # 国际服
            game_class = 'UnrealWindow'
        auto_dict = {
            'game': [game_name, game_class],
            # 'starter': [config.LineEdit_starter_name.value, config.LineEdit_starter_class.value]
        }
        if self.auto is None:
            try:
                self.auto = Automation(auto_dict[name][0], auto_dict[name][1], self.logger)
                if self.determine_screen_ratio(self.auto.hwnd):
                    signalBus.sendHwnd.emit(self.auto.hwnd)
                    return True
                else:
                    self.logger.error(f'游戏窗口比例不是16:9')
                    return False
            except Exception as e:
                self.logger.error(f'初始化auto失败：{e}')
                return False
        else:
            self.logger.debug(f'延用auto：{self.auto.hwnd}')
            return True
        # else:
        #     if switch:
        #         timeout = Timer(10).start()
        #         while True:
        #             try:
        #                 self.auto = Automation(auto_dict[name][0], auto_dict[name][1], self.logger)
        #                 self.logger.info(f'切换auto成功')
        #                 return True
        #             except Exception as e:
        #                 self.logger.warn(f'未找到{auto_dict[name][0]}，等待1秒')
        #                 time.sleep(1)
        #             if timeout.reached():
        #                 self.logger.error(f'切换auto超时')
        #                 break

    # def chose_auto(self, only_game=False):
    #     """
    #     自动选择auto，有游戏窗口时选游戏，没有游戏窗口时选启动器，都没有的时候循环，寻找频率1次/s
    #     :return:
    #     """
    #     timeout = Timer(20).start()
    #     while True:
    #         # 每次循环重新导入
    #         from app.modules.automation.automation import auto_starter, auto_game
    #         if win32gui.FindWindow(None, config.LineEdit_game_name.value) or only_game:
    #             if not auto_game:
    #                 instantiate_automation(auto_type='game')  # 尝试实例化 auto_game
    #             self.auto = auto_game
    #             flag = 'game'
    #         else:
    #             if not auto_starter:
    #                 instantiate_automation(auto_type='starter')  # 尝试实例化 auto_starter
    #             self.auto = auto_starter
    #             flag = 'starter'
    #         if self.auto:
    #             return flag
    #         if timeout.reached():
    #             logger.error("获取auto超时")
    #             break
