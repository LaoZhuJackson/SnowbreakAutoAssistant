import numpy as np
import win32api
import win32con
import win32gui

from app.common.config import config
from app.common.logger import logger
# from app.modules.automation.automation import instantiate_automation
from app.modules.automation.timer import Timer


def random_normal_distribution_int(a, b, n=15):
    """
    在区间 [a, b) 内产生符合正态分布的随机数，原理是取n个随机数的平均值来模拟正态分布
    :param a: 最小值
    :param b: 最大值
    :param n: 随机数的数量，值越大分布越集中
    :return:int
    """
    if a < b:
        output = np.mean(np.random.randint(a, b, size=n))
        return int(output.round())
    else:
        return b


def random_rectangle_point(area, n=3):
    """
    在区域内产生符合二维正态分布的随机点，通常在点击操作中使用
    :param area: ((upper_left_x, upper_left_y), (bottom_right_x, bottom_right_y)).
    :param n: 随机数的数量，值越大分布越集中
    :return: tuple(int): (x, y)
    """
    # print(f"{area=}")
    # area=((1285, 873), (1417, 921))
    x = random_normal_distribution_int(area[0][0], area[1][0], n=n)
    y = random_normal_distribution_int(area[0][1], area[1][1], n=n)
    return x, y


def is_fullscreen(hwnd):
    """
    判断窗口是否全屏运行
    :param hwnd: 窗口句柄
    :return: True if the window is fullscreen, False otherwise
    """
    # 获取窗口的矩形区域（left, top, right, bottom）
    window_rect = win32gui.GetWindowRect(hwnd)
    window_width = window_rect[2] - window_rect[0]  # 窗口宽度
    window_height = window_rect[3] - window_rect[1]  # 窗口高度

    # 获取屏幕的宽度和高度
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # 判断窗口大小是否与屏幕大小一致
    if window_width == screen_width and window_height == screen_height:
        return True
    else:
        return False


def get_all_children(widget):
    """
    递归地获取指定QWidget及其所有后代控件的列表。

    :param widget: QWidget对象，从该对象开始递归查找子控件。
    :return: 包含所有子控件（包括后代）的列表。
    """
    children = []
    for child in widget.children():
        children.append(child)
        children.extend(get_all_children(child))  # 递归调用以获取后代控件
    return children
