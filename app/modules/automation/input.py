import ctypes
import string
import time
from ctypes import windll

import win32api
import win32con
import win32gui  # 不能删

from app.common.logger import logger


# from pynput import mouse


class Input:
    def __init__(self, hwnd, logger):
        self.logger = logger
        self.hwnd = hwnd
        # https://docs.microsoft.com/zh/windows/win32/inputdev/virtual-key-codes
        # key的wparam就是vkcode
        self.VkCode = {
            "back": 0x08,
            "tab": 0x09,
            "return": 0x0D,
            "shift": 0x10,
            "ctrl": 0x11,
            "alt": 0x12,
            "pause": 0x13,
            "capital": 0x14,
            "esc": 0x1B,
            "space": 0x20,
            "end": 0x23,
            "home": 0x24,
            "left": 0x25,
            "up": 0x26,
            "right": 0x27,
            "down": 0x28,
            "print": 0x2A,
            "snapshot": 0x2C,
            "insert": 0x2D,
            "delete": 0x2E,
            "lwin": 0x5B,
            "rwin": 0x5C,
            "numpad0": 0x60,
            "numpad1": 0x61,
            "numpad2": 0x62,
            "numpad3": 0x63,
            "numpad4": 0x64,
            "numpad5": 0x65,
            "numpad6": 0x66,
            "numpad7": 0x67,
            "numpad8": 0x68,
            "numpad9": 0x69,
            "multiply": 0x6A,
            "add": 0x6B,
            "separator": 0x6C,
            "subtract": 0x6D,
            "decimal": 0x6E,
            "divide": 0x6F,
            "f1": 0x70,
            "f2": 0x71,
            "f3": 0x72,
            "f4": 0x73,
            "f5": 0x74,
            "f6": 0x75,
            "f7": 0x76,
            "f8": 0x77,
            "f9": 0x78,
            "f10": 0x79,
            "f11": 0x7A,
            "f12": 0x7B,
            "numlock": 0x90,
            "scroll": 0x91,
            "lshift": 0xA0,
            "rshift": 0xA1,
            "lcontrol": 0xA2,
            "rcontrol": 0xA3,
            "lmenu": 0xA4,
            "rmenu": 0XA5
        }
        # https://learn.microsoft.com/zh-cn/windows/win32/inputdev/mouse-input-notifications
        self.WmCode = {
            "left_down": 0x0201,
            "left_up": 0x0202,
            "middle_down": 0x0207,
            "middle_up": 0x0208,
            "right_down": 0x0204,
            "right_up": 0x0205,
            "x1_down": 0x020B,
            "x1_up": 0x020C,
            "x2_down": 0x020B,
            "x2_up": 0x020C,
            "key_down": 0x0100,
            "key_up": 0x0101,
            "mouse_move": 0x0200,
            "mouse_wheel": 0x020A,
        }
        self.MwParam = {
            "x1": 0x0001,  # 侧键后退按钮
            "x2": 0x0002,  # 侧键前进按钮
        }
        # 排除缩放干扰
        ctypes.windll.user32.SetProcessDPIAware()

    def get_virtual_keycode(self, key: str):
        """根据按键名获取虚拟按键码
        Args:
            key (str): 按键名
        Returns:
            int: 虚拟按键码
        """
        # 获取打印字符
        if len(key) == 1 and key in string.printable:
            # https://docs.microsoft.com/zh/windows/win32/api/winuser/nf-winuser-vkkeyscana
            return windll.user32.VkKeyScanA(ord(key)) & 0xff
        # 获取控制字符
        else:
            return self.VkCode[key]

    def activate(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)

    def mouse_down(self, x: int, y: int, mouse_key: str = 'left'):
        """鼠标按下，可以指定按键, 默认左键"""
        wparam = 0
        if mouse_key in ["x1", "x2"]:
            wparam = self.MwParam[mouse_key]
        lparam = y << 16 | x
        message = self.WmCode[f"{mouse_key}_down"]
        win32gui.PostMessage(self.hwnd, message, wparam, lparam)

    def mouse_up(self, x: int, y: int, mouse_key: str = 'left'):
        """鼠标抬起，可以指定按键, 默认左键"""
        wparam = 0
        if mouse_key in ["x1", "x2"]:
            wparam = self.MwParam[mouse_key]
        lparam = y << 16 | x
        message = self.WmCode[f"{mouse_key}_up"]
        win32gui.PostMessage(self.hwnd, message, wparam, lparam)

    # 检测鼠标是否有活动
    @staticmethod
    def is_mouse_in_use(last_position, threshold=1):
        """
        判断用户是否正在移动鼠标
        :param last_position: 等待前的鼠标位置
        :param threshold: 阈值，越小越精细
        :return:
        """
        # 先等待一段时间
        time.sleep(0.1)
        # 获取当前鼠标位置
        current_position = win32api.GetCursorPos()

        # 检查鼠标是否移动（阈值小于一定距离认为是未移动）
        if abs(current_position[0] - last_position[0]) > threshold or abs(
                current_position[1] - last_position[1]) > threshold:
            return True  # 鼠标有活动
        return False  # 鼠标没有活动

    def move_click(self, x: int, y: int, mouse_key='left', press_time: float = 0.04, time_out: float = 10):
        """
        检测是否正在用鼠标，用户不使用鼠标时快速移动到x，y后点击再返回原位置，主要用于主界面有光标等地方，允许指定鼠标按键，运行设定按下时间
        假后台：能穿透窗口直接点到对应句柄的窗口，但是会抢一瞬间的鼠标
        :param mouse_key: 鼠标按键：left,right,middle,x(侧键)
        :param x: 横坐标
        :param y: 纵坐标
        :param press_time: 按下时长（越长越稳定）
        :param time_out: 等待按下的超时时间
        :return:
        """
        if isinstance(x, float):
            x = int(x)
        if isinstance(y, float):
            y = int(y)

        last_position = win32api.GetCursorPos()  # 获取初始鼠标位置
        start_time = time.time()
        try:
            while time.time() - start_time < time_out:
                if not self.is_mouse_in_use(last_position):
                    current_pos = win32api.GetCursorPos()
                    self.activate()
                    win32api.SetCursorPos((x, y))
                    self.mouse_down(x, y, mouse_key)
                    time.sleep(press_time)
                    self.mouse_up(x, y, mouse_key)
                    time.sleep(0.05)
                    win32api.SetCursorPos(current_pos)
                    self.logger.debug(f"鼠标移动后点击({x}, {y})")
                    break
                else:
                    # self.logger.debug("鼠标正在使用，等待...")
                    last_position = win32api.GetCursorPos()
            if time.time() - start_time > time_out:
                raise RuntimeError("等待点击超时")
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"鼠标移动点击({x}, {y})出错：{repr(e)}")

    def mouse_click(self, x: int, y: int, mouse_key='left', press_time: float = 0.002):
        """真后台：不抢鼠标，后台按键点击，主要用于无光标时，默认左键"""
        try:
            self.activate()
            # win32api.SetCursorPos((x, y))
            self.mouse_down(x, y, mouse_key)
            time.sleep(press_time)
            self.mouse_up(x, y, mouse_key)
            self.logger.debug(f"鼠标移动后点击({x}, {y})")
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"鼠标移动点击({x}, {y})出错：{repr(e)}")

    def move_to(self, x: int, y: int):
        """
        假后台：移动鼠标到坐标（x, y)
        :param x:
        :param y:
        :return:
        """
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
        wparam = 0
        lparam = y << 16 | x
        win32gui.PostMessage(self.hwnd, self.WmCode['mouse_move'], wparam, lparam)

    def move_down(self, x, y, mouse_key='left'):
        """鼠标移动到（x,y）后按下key键,默认左键"""
        pass

    def move_up(self, x, y, mouse_key='left'):
        """鼠标移动到（x,y）后松开key键,默认左键"""
        pass

    def mouse_scroll(self, x: int, y: int, delta: int = 120, time_out: float = 10.):
        """
        假后台：在坐标(x, y)滚动鼠标滚轮一次
        :param delta: 为正向上滚动，为负向下滚动
        :param x:
        :param y:
        :param time_out: 超时时间
        :return:
        """
        wparam = delta << 16
        message = self.WmCode['mouse_wheel']
        lparam = y << 16 | x

        last_position = win32api.GetCursorPos()  # 获取初始鼠标位置
        start_time = time.time()
        try:
            while time.time() - start_time < time_out:
                if not self.is_mouse_in_use(last_position):
                    current_pos = win32api.GetCursorPos()
                    self.activate()
                    win32api.SetCursorPos((x, y))
                    # 滚一次
                    win32gui.PostMessage(self.hwnd, message, wparam, lparam)
                    win32api.SetCursorPos(current_pos)
                    self.logger.debug(f"鼠标移动至({x},{y})滚动滚轮 {delta}")
                    break
                else:
                    # self.logger.debug("鼠标正在使用，等待...")
                    last_position = win32api.GetCursorPos()
            if time.time() - start_time > time_out:
                raise RuntimeError("等待滚动滚轮超时")
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"鼠标移动({x}, {y})后滚动出错：{repr(e)}")

    def press_key(self, key, press_time=0.2):
        """
        真后台：模拟键盘按键按下，允许长按
        :param key: 按下的按键
        :param press_time: 按下时长
        :return:
        """
        try:
            self.key_down(key)
            time.sleep(press_time)
            self.key_up(key)
            self.logger.debug(f"键盘按下{key}")
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"键盘按下{key}出错：{repr(e)}")

    def key_down(self, key):
        """
        按下指定按键
        :param key: 指定按键
        :return:
        """
        vk_code = self.get_virtual_keycode(key)
        scan_code = windll.user32.MapVirtualKeyW(vk_code, 0)
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
        wparam = vk_code
        lparam = (scan_code << 16) | 1
        win32gui.PostMessage(self.hwnd, self.WmCode["key_down"], wparam, lparam)

    def key_up(self, key):
        """
        抬起指定按键
        :param key: 指定按键
        :return:
        """
        vk_code = self.get_virtual_keycode(key)
        scan_code = windll.user32.MapVirtualKeyW(vk_code, 0)
        # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
        wparam = vk_code
        lparam = (scan_code << 16) | 1
        win32gui.PostMessage(self.hwnd, self.WmCode["key_up"], wparam, lparam)


if __name__ == '__main__':
    import win32gui


    def get_hwnd_by_title(window_title):

        def callback(hwnd, hwnd_list):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                hwnd_list.append(hwnd)
            return True

        hwnd_list = []
        win32gui.EnumWindows(callback, hwnd_list)
        return hwnd_list[0] if hwnd_list else None


    def enumerate_child_windows(parent_hwnd):
        def callback(handle, windows):
            windows.append(handle)
            return True

        child_windows = []
        win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
        return child_windows


    def get_hwnd(window_title):
        """根据传入的窗口名和类型确定可操作的句柄"""
        hwnd = win32gui.FindWindow(None, window_title)
        handle_list = []
        if hwnd:
            handle_list.append(hwnd)
            handle_list.extend(enumerate_child_windows(hwnd))
            print(handle_list)
        return None


    hwnd = get_hwnd_by_title("BrownDust II")
    print(f"窗口句柄：{hwnd}")
    title = "BrownDust II"
    get_hwnd(title)
    i = Input(hwnd, logger)
    click_dict = {
        "SAA尘白助手": [230, 895],
        "无标题 - 画图": [933, 594],
        "画图": [933, 594],
        "鸣潮": [1178, 477],
        "鸣潮  ": [1406, 40],
        "Wuthering Waves": [1178, 477],
        "西山居启动器-尘白禁区": [337, 559],
        "尘白禁区": [110, 463],
        "BrownDust II": [1441, 1336],
    }
    x_1 = click_dict[title][0]
    y_1 = click_dict[title][1]
    time.sleep(2)
    # i.move_click('left', x_1, y_1,press_time=1)
    # i.mouse_click(x_1, y_1)
    # i.move_click(x_1, y_1)
    # time.sleep(1)
    # i.press_key('esc')
    # i.mouse_scroll(-120,1532,534)
