import ctypes
import string
from ctypes import windll, byref, wintypes
from ctypes.wintypes import HWND, POINT
import time

import win32api
import win32con
import win32gui
import win32process

PostMessageW = windll.user32.PostMessageW
ClientToScreen = windll.user32.ClientToScreen

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x202
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120


def move_to(handle: HWND, x: int, y: int):
    """移动鼠标到坐标（x, y)

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_MOUSEMOVE, wparam, lparam)


def left_down(handle: HWND, x: int, y: int):
    """在坐标(x, y)按下鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_LBUTTONDOWN, wparam, lparam)


def left_up(handle: HWND, x: int, y: int):
    """在坐标(x, y)放开鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_LBUTTONUP, wparam, lparam)


def scroll(handle: HWND, delta: int, x: int, y: int):
    """在坐标(x, y)滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        delta (int): 为正向上滚动，为负向下滚动
        x (int): 横坐标
        y (int): 纵坐标
    """
    move_to(handle, x, y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel
    wparam = delta << 16
    p = POINT(x, y)
    ClientToScreen(handle, byref(p))
    lparam = p.y << 16 | p.x
    PostMessageW(handle, WM_MOUSEWHEEL, wparam, lparam)


def scroll_up(handle: HWND, x: int, y: int):
    """在坐标(x, y)向上滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    scroll(handle, WHEEL_DELTA, x, y)


def scroll_down(handle: HWND, x: int, y: int):
    """在坐标(x, y)向下滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    scroll(handle, -WHEEL_DELTA, x, y)


MapVirtualKeyW = windll.user32.MapVirtualKeyW
VkKeyScanA = windll.user32.VkKeyScanA

WM_KEYDOWN = 0x100
WM_KEYUP = 0x101

# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
VkCode = {
    "back": 0x08,
    "tab": 0x09,
    "return": 0x0D,
    "shift": 0x10,
    "control": 0x11,
    "menu": 0x12,
    "pause": 0x13,
    "capital": 0x14,
    "escape": 0x1B,
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


def get_virtual_keycode(key: str):
    """根据按键名获取虚拟按键码

    Args:
        key (str): 按键名

    Returns:
        int: 虚拟按键码
    """
    if len(key) == 1 and key in string.printable:
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscana
        return VkKeyScanA(ord(key)) & 0xff
    else:
        return VkCode[key]


def key_down(handle: HWND, key: str):
    """按下指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
    wparam = vk_code
    lparam = (scan_code << 16) | 1
    PostMessageW(handle, WM_KEYDOWN, wparam, lparam)


def key_up(handle: HWND, key: str):
    """放开指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
    wparam = vk_code
    lparam = (scan_code << 16) | 0XC0000001
    PostMessageW(handle, WM_KEYUP, wparam, lparam)


def background_click(hwnd, x, y):
    """
    后台模拟鼠标点击
    :param hwnd: 目标窗口句柄
    :param x: 窗口客户区X坐标
    :param y: 窗口客户区Y坐标
    """
    # 将客户区坐标转换为屏幕坐标
    client_rect = win32gui.GetClientRect(hwnd)
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x, y))

    # 计算窗口左上角的屏幕坐标
    window_left, window_top, _, _ = win32gui.GetWindowRect(hwnd)
    client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))

    # 计算点击位置相对于窗口左上角的偏移
    offset_x = screen_x - client_left
    offset_y = screen_y - client_top

    # 移动光标过去，方便查看
    # win32api.SetCursorPos((screen_x, screen_y))
    # print(offset_x, offset_y)

    # 构造坐标参数（低位WORD是X坐标，高位WORD是Y坐标）
    lparam = win32api.MAKELONG(offset_x, offset_y)

    # 发送鼠标按下消息
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)  # 短暂延时模拟真实点击
    # 发送鼠标弹起消息
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    print(f"点击{handle}({offset_x},{offset_y})完成")


def win32_click(x, y):
    # 模拟鼠标点击
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)  # 按下鼠标左键
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)  # 放开鼠标左键


def get_window_properties(hwnd):
    window_title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    window_text = win32gui.GetWindowText(hwnd)
    window_rect = win32gui.GetWindowRect(hwnd)
    return window_title, class_name, window_text, window_rect


def enumerate_child_windows(parent_hwnd):
    def callback(hwnd, windows):
        windows.append(hwnd)
        return True

    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows


def print_window_info(hwnd):
    window_title, class_name, window_text, window_rect = get_window_properties(hwnd)
    print('--' * 60)
    print(f'窗口句柄：{hwnd}')
    print(f'标题：{window_title}')
    print(f'类名：{class_name}')
    print(f'文本内容：{window_text}')
    print(f'矩形位置：{window_rect}')


def find_window_by_title_contains(keyword):
    hwnd = win32gui.FindWindow(None, None)
    while hwnd:
        window_title = win32gui.GetWindowText(hwnd)
        if keyword in window_title:
            print(f"找到窗口{window_title}，句柄为{hwnd}")
            return hwnd
        hwnd = win32gui.FindWindowEx(None, hwnd, None, None)
    return None


def activate(hwnd):
    win32gui.PostMessage(hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)


def move_to(hwnd, x, y):
    x = x if isinstance(x, int) else int(x)
    y = y if isinstance(y, int) else int(y)
    lParam = win32api.MAKELONG(x, y)

    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
    # win32api.SetCursorPos((x, y))


def send_background_click(hwnd, x_screen, y_screen):
    # 将屏幕坐标转换为窗口客户区坐标
    (x_client, y_client) = win32gui.ScreenToClient(hwnd, (x_screen, y_screen))

    # 打包坐标到lParam
    lParam = win32api.MAKELONG(x_client, y_client)

    # 附加输入线程（可选，可能需要）
    foreground_thread = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
    current_thread = win32api.GetCurrentThreadId()
    print(f"{current_thread=}")
    print(f"{foreground_thread=}")
    if foreground_thread != current_thread:
        win32process.AttachThreadInput(current_thread, foreground_thread[0], True)

    try:
        # 发送鼠标移动消息
        win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
        # 发送左键按下
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        # 发送左键释放（适当延迟，可选）
        win32api.Sleep(100)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    finally:
        # 解除线程附加
        if foreground_thread != current_thread:
            win32process.AttachThreadInput(current_thread, foreground_thread[0], False)


# 定义鼠标钩子回调函数
# @ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM, ctypes.POINTER(None))
# def MouseProc(nCode, wParam, lParam, idHook):
#     if nCode >= 0:
#         if wParam == WM_LBUTTONDOWN:
#             # 修改鼠标位置
#             ctypes.windll.user32.SetCursorPos(x, y)
#     return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

def refresh_window(hwnd):
    """ 强制刷新窗口，而不改变其 z 轴位置 """
    # InvalidateRect：让窗口的区域失效，要求重新绘制
    win32gui.InvalidateRect(hwnd, None, True)  # None 表示整个窗口区域
    # UpdateWindow：强制更新窗口内容
    win32gui.UpdateWindow(hwnd)


if __name__ == "__main__":
    # 需要和目标窗口同一权限，游戏窗口通常是管理员权限
    import sys

    if not windll.shell32.IsUserAnAdmin():
        print("不是管理员")
        # 不是管理员就提权
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
    else:
        print("是管理员")

    window_name = "西山居启动器-尘白禁区"

    ctypes.windll.user32.SetProcessDPIAware()

    import cv2

    click_dict = {
        "SAA尘白助手": [230, 895],
        "无标题 - 画图": [933, 594],
        "画图": [933, 594],
        "鸣潮": [1178, 477],
        "鸣潮  ": [1406, 40],
        "Wuthering Waves": [1178, 477],
        "西山居启动器-尘白禁区": [1362, 899],
        "尘白禁区": [120, 380],
    }
    handle = windll.user32.FindWindowW(None, window_name)
    # handle = win32gui.GetDesktopWindow()
    # handle = find_window_by_title_contains(window_name)
    print_window_info(handle)
    rect = win32gui.GetWindowRect(handle)

    handle_list = []
    if handle != 0:
        child_windows = enumerate_child_windows(handle)
        for hwnd in child_windows:
            print_window_info(hwnd)
            handle_list.append(hwnd)
    else:
        print(f"未找到：{window_name}")
    # key = 'escape'
    # key_down(handle, key)
    # time.sleep(2)
    # key_up(handle, key)

    x = click_dict[window_name][0]
    y = click_dict[window_name][1]

    # x,y = rect[0], rect[1]
    # w,h = rect[2] - x, rect[3] - y

    long_positon = win32api.MAKELONG(x, y)

    # print(handle_list)
    # time.sleep(3)
    # win32gui.PostMessage(handle, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    # print("activate")
    # key = 'escape'
    # key_down(handle, key)
    # time.sleep(0.1)
    # key_up(handle, key)
    # move_to(handle,x,y)
    # time.sleep(3)
    # # current_pos = win32api.GetCursorPos()
    # # print('当前鼠标位置：', current_pos)
    # win32api.SetCursorPos((x, y))
    # # left_down(handle,x,y)
    # win32api.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_positon)
    # time.sleep(0.004)
    # # left_up(handle,x,y)
    # win32api.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_positon)
    # # win32api.SetCursorPos(current_pos)
    # time.sleep(1)
    # print("第二次点击")
    # win32api.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_positon)
    # time.sleep(0.05)
    # win32api.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_positon)
    # win32api.SetCursorPos(current_pos)
    # print(f"点击({x + 200},{y + 300})完成")

    # send_background_click(handle,x,y)

    # 设置鼠标钩子
    # hhk = ctypes.windll.user32.SetWindowsHookExW(14, MouseProc, ctypes.windll.kernel32.GetModuleHandleW(None), 0)
    #
    # # 消息循环
    # ctypes.windll.user32.PumpMessages()
    # win32api.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_positon)
    # time.sleep(1)
    # win32api.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_positon)
    #
    # # 移除钩子
    # ctypes.windll.user32.UnhookWindowsHookEx(hhk)

    for handle in handle_list:
        print_window_info(handle)

        # win32api.PostMessage(handle,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,long_positon)
        # time.sleep(0.1)
        # win32api.PostMessage(handle,win32con.WM_LBUTTONUP, 0, long_positon)
        # 发送鼠标按下消息
        # activate(handle)
        # background_click(handle, x, y)
        # refresh_window(handle)
        # print(f"点击{handle}({x},{y})完成")
        time.sleep(3)

    # move_to(handle, x, y)
    # # 点击线路
    # handle = 134606
    # print_window_info(handle)
    # left_down(handle, x, y)
    # time.sleep(0.1)
    # left_up(handle, x, y)
    # time.sleep(1)

    # 滚动线路列表
    # scroll_down(handle, 1000, 200)
    # print("开始")
    # handle = 201834 #鸣潮unreal句柄
    # handle = 396384 #尘白unreal句柄

    # win32gui.SetWindowPos(handle, win32con.HWND_TOP, 0, 0, 1536, 864, win32con.SWP_NOZORDER)
    # win32gui.SendMessage(handle, win32con.WM_SETFOCUS, 0, 0)
    # win32gui.SetForegroundWindow(handle)
    # activate(handle)
    # key = 'menu'
    # key_down(handle, key)
    # time.sleep(5)
    # background_click(handle, x, y)
    # time.sleep(1)
    # background_click(handle, x, y)
    # time.sleep(2)
    # background_click(handle, x, y)
    # time.sleep(2)
    # background_click(handle, x, y)
    # key_up(handle, key)
    # time.sleep(3)
    # background_click(handle, x, y)
    # handle = 200188
    # activate(handle)
    # background_click(handle, x, y)
    # win32_click(x, y)
