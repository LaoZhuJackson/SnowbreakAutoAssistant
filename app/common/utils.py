import numpy as np
import win32api
import win32con
import win32gui
import requests
from bs4 import BeautifulSoup
import re
import json


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


# 添加随机噪声的函数
def add_noise(image, noise_factor=0.01):
    noise = np.random.normal(0, 1, image.shape) * noise_factor
    noisy_image = np.clip(image + noise, 0, 255).astype(np.uint8)
    return noisy_image


def enumerate_child_windows(parent_hwnd):
    def callback(handle, windows):
        windows.append(handle)
        return True

    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows


def get_hwnd(window_title, window_class):
    """根据传入的窗口名和类型确定可操作的句柄"""
    hwnd = win32gui.FindWindow(None, window_title)
    handle_list = []
    if hwnd:
        handle_list.append(hwnd)
        handle_list.extend(enumerate_child_windows(hwnd))
        for handle in handle_list:
            class_name = win32gui.GetClassName(handle)
            if class_name == window_class:
                # 找到需要的窗口句柄
                return handle
    return None


def get_date():
    # url = 'https://www.cbjq.com/p/zt/2023/04/13/index/news.html?catid=7131&infoid=247'
    API_URL = "https://www.cbjq.com/api.php?op=search_api&action=get_article_detail&catid=7131&id=247"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        return {"error": f"请求失败，状态码: {response.status_code}"}

    try:
        data = response.json()
        content_html = data["data"][0]["content"]  # 获取活动内容HTML
    except Exception as e:
        return {"error": f"数据解析失败: {str(e)}"}

    soup = BeautifulSoup(content_html, 'html.parser')
    paragraphs = soup.find_all('p')
    result_dict = {}
    current_index = 0
    while current_index < len(paragraphs):
        p = paragraphs[current_index]
        text = p.get_text(strip=True)

        # 提取角色共鸣
        if "角色共鸣" in text and "✧" in text:
            role_name = re.search(r"「(.*?)」", text).group(1)
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            if "活动时间：" in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                start = f"{dates[0].split('月')[0].zfill(2)}.{dates[0].split('月')[1].replace('日', '').zfill(2)}"
                end = f"{dates[1].split('月')[0].zfill(2)}.{dates[1].split('月')[1].replace('日', '').zfill(2)}"
                result_dict[role_name] = f"{start}-{end}"

        # 提取活动任务时间
        elif "【调查清单】活动任务" in text:
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            dates = re.findall(r"\d+月\d+日", time_text)
            start = f"{dates[0].split('月')[0].zfill(2)}.{dates[0].split('月')[1].replace('日', '').zfill(2)}"
            end = f"{dates[1].split('月')[0].zfill(2)}.{dates[1].split('月')[1].replace('日', '').zfill(2)}"
            result_dict["调查清单"] = f"{start}-{end}"

        # 提取挑战玩法
        elif "挑战玩法" in text and "✧" in text:
            challenge_name = re.search(r"【(.*?)】", text).group(1)
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            dates = re.findall(r"\d+月\d+日", time_text)
            start = f"{dates[0].split('月')[0].zfill(2)}.{dates[0].split('月')[1].replace('日', '').zfill(2)}"
            end = f"{dates[1].split('月')[0].zfill(2)}.{dates[1].split('月')[1].replace('日', '').zfill(2)}"
            result_dict[challenge_name] = f"{start}-{end}"

        elif "趣味玩法" in text and "✧" in text:
            play_name = re.search(r"【(.*?)】", text).group(1)
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            if "常驻" not in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                start = f"{dates[0].split('月')[0].zfill(2)}.{dates[0].split('月')[1].replace('日', '').zfill(2)}"
                end = f"{dates[1].split('月')[0].zfill(2)}.{dates[1].split('月')[1].replace('日', '').zfill(2)}"
                result_dict[play_name] = f"{start}-{end}"

        current_index += 1

    if len(result_dict) != 0:
        with open('Appdata/activity_date.json', 'w') as f:
            json.dump(result_dict, f, indent=4)
    return result_dict


if __name__ == "__main__":
    print(get_date())
