import os
import traceback
from pathlib import Path

import cpufeature
import cv2
import numpy as np
import win32api
import win32con
import win32gui
import requests
from bs4 import BeautifulSoup
import re
import json

from requests import Timeout, RequestException

from app.common.config import config


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


def fetch_url(url: str, timeout: float = None, encoding: str = None):
    """
    通用网络请求函数

    参数:
        url: 请求的URL
        timeout: 超时时间（秒）
        encoding: 手动指定的编码格式

    返回:
        成功: requests.Response 对象
        失败: 包含错误信息的字典
    """
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/134.0.0.0 Safari/537.36"
    }
    port = config.update_proxies.value  # 假设config是已定义的配置对象
    proxies = {
        "http": f"http://127.0.0.1:{port}",
        "https": f"http://127.0.0.1:{port}"
    } if port else None

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            proxies=proxies
        )
        if encoding:
            response.encoding = encoding
        return response
    except Timeout:
        return {"error": f"⚠️ 连接超时，请检查网络是否能连接 {url}"}
    except RequestException as e:
        return {"error": f"🔌 网络请求 {url} 失败: {e}"}
    except Exception as e:
        return {"error": f"❌ 请求 {url} 发生未知错误: {e}"}


def get_date_from_api(url=None):
    """
    获取具体的活动日期
    :param url: 尘白官网的内容api接口链接
    :return: {'爆爆菜园': '07.17-08.21', '噬神斗场': '07.10-08.07', '禁区协议': '07.28-08.11', '激战智域': '08.04-08.18', '勇者游戏': '08.07-08.21', '青之迷狂': '07.10-08.21', '奇迹诺言': '07.24-08.21', '铭心指任': '07.10-08.21', '风行影随': '07.31-08.21'}
    """

    def format_date(date_str):
        """格式化日期字符串为 MM.DD 格式"""
        parts = date_str.split('月')
        month = parts[0].zfill(2)
        day = parts[1].replace('日', '').zfill(2)
        return f"{month}.{day}"

    # url = 'https://www.cbjq.com/api.php?op=search_api&action=get_article_detail&catid=7131&id=282'
    API_URL = url
    response = fetch_url(API_URL, timeout=3, encoding='utf-8')

    if isinstance(response, dict):  # 错误处理
        return response
    if response.status_code != 200:
        return {"error": f"请求失败，状态码: {response.status_code}"}

    try:
        data = response.json()
        content_html = data["data"][0]["content"]
    except (KeyError, IndexError, ValueError) as e:
        return {"error": f"❌ 解析JSON数据失败: {e}"}

    soup = BeautifulSoup(content_html, 'html.parser')
    paragraphs = soup.find_all('p')
    result_dict = {}
    current_index = 0
    while current_index < len(paragraphs):
        p = paragraphs[current_index]
        text = p.get_text(strip=True)
        # print(text)
        # 提取角色共鸣,同时还需要判断句号不在句子中，排除干扰
        if "角色共鸣" in text and "✧" in text and "。" not in text:
            match = re.search(r"「(.*?)」", text)
            if match:
                role_name = match.group(1)
            else:
                return {"error": f"未匹配到“角色共鸣”"}
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            if "活动时间：" in time_text and "常驻" not in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                # 检查是否匹配到两个日期
                if len(dates) >= 2:
                    start = format_date(dates[0])
                    end = format_date(dates[1])
                    result_dict[role_name] = f"{start}-{end}"
                else:
                    print(f"警告：角色共鸣时间格式异常: {time_text}")
                    # 跳过或记录错误

        # 提取活动任务时间
        elif "【调查清单】活动任务" in text:
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            if "常驻" not in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                if len(dates) >= 2:
                    start = format_date(dates[0])
                    end = format_date(dates[1])
                    result_dict["调查清单"] = f"{start}-{end}"
                else:
                    print(f"警告：调查清单时间格式异常: {time_text}")

        # 提取挑战玩法
        elif "挑战玩法" in text and "✧" in text:
            challenge_name = re.search(r"【(.*?)】", text).group(1)
            time_text = ''
            while "活动时间" not in time_text:
                current_index += 1
                time_text = paragraphs[current_index].get_text(strip=True)
            if "常驻" not in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                if len(dates) >= 2:
                    start = format_date(dates[0])
                    end = format_date(dates[1])
                    result_dict[challenge_name] = f"{start}-{end}"
                else:
                    print(f"警告：挑战玩法时间格式异常: {time_text}")

        elif "趣味玩法" in text and "✧" in text:
            play_name = re.search(r"【(.*?)】", text).group(1)
            current_index += 1
            time_text = paragraphs[current_index].get_text(strip=True)
            if "常驻" not in time_text:
                dates = re.findall(r"\d+月\d+日", time_text)
                if len(dates) >= 2:
                    start = format_date(dates[0])
                    end = format_date(dates[1])
                    result_dict[play_name] = f"{start}-{end}"
                else:
                    # print(f"警告：趣味玩法时间格式异常: {time_text}")
                    pass

        current_index += 1

    if len(result_dict) != 0:
        return result_dict
    else:
        return {"error": f"未匹配到任何活动。检查 {url} 是否正确"}


def cpu_support_avx2():
    """
    判断 CPU 是否支持 AVX2 指令集。
    """
    config.set(config.cpu_support_avx2, cpufeature.CPUFeature["AVX2"])
    return cpufeature.CPUFeature["AVX2"]


def count_color_blocks(image, lower_color, upper_color, preview=False):
    """计算颜色块数量，并可选择预览掩膜"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    if preview:  # 添加预览模式
        # 将掩膜与原图叠加显示
        masked_img = cv2.bitwise_and(image, image, mask=mask)
        cv2.imshow("Mask Preview", masked_img)
        # cv2.waitKey(1)  # 保持1ms后自动关闭（非阻塞模式）
        cv2.waitKey(0)  # 按任意键继续（阻塞模式）

    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours)


def rgb_to_opencv_hsv(r, g, b):
    # 输入：RGB 值（范围 0-255）
    # 输出：OpenCV 格式的 HSV 值（H:0-179, S:0-255, V:0-255）
    rgb_color = np.uint8([[[b, g, r]]])  # OpenCV 使用 BGR 顺序
    hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_BGR2HSV)
    return hsv_color[0][0]


def get_hsv(target_rgb):
    # 转换为 OpenCV 的 HSV 值
    h, s, v = rgb_to_opencv_hsv(*target_rgb)

    # 设置容差范围
    h_tolerance = 2
    s_tolerance = 35
    v_tolerance = 10

    lower_color = np.array([max(0, h - h_tolerance), max(0, s - s_tolerance), max(0, v - v_tolerance)])
    upper_color = np.array([min(179, h + h_tolerance), min(255, s + s_tolerance), min(255, v + v_tolerance)])

    print(f"Lower HSV: {lower_color}")
    print(f"Upper HSV: {upper_color}")


def get_gitee_text(text_path: str):
    """
        从Gitee获取文本文件并按行返回内容

        参数:
            text_path: 文件在仓库中的路径 (如: "requirements.txt")

        返回:
            成功: 包含每行文本的列表
            失败: None
    """
    url = f"https://gitee.com/laozhu520/auto_chenbai/raw/main/{text_path}"
    response = fetch_url(url, timeout=3)

    if isinstance(response, dict):  # 错误处理
        return response
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return None

    # 自动检测编码并处理文本
    response.encoding = response.apparent_encoding
    return response.text.splitlines()


def get_start_arguments(start_path, start_model):
    """
    自动判断是什么服，什么启动器，返回对应的启动参数
    :param start_path: 启动路径，由用户提供，可以在启动器查看
    :param start_model: 由用户设置，在SAA设置中选服
    :return:
    """
    # 统一进入game文件夹
    user_dir = os.path.join(start_path, 'game').replace('\\', '/')
    arg = None
    # 国服新版启动命令
    if start_model == 0:
        if has_folder_in_path(start_path, "Temp"):
            arg = [
                "-FeatureLevelES31",
                "-ChannelID=jinshan",
                '-userdir=' + user_dir,
                '--launcher-language="en"',
                '--launcher-channel="CBJQos"',
                '--launcher-gamecode="cbjq"'
            ]
        else:
            # 国服旧版启动命令
            # self.start_path = D:\Game\尘白禁区\Snow\data
            arg = [
                "-FeatureLevelES31",
                "-ChannelID=jinshan",
                '-userdir=' + user_dir
            ]
    # b服启动命令
    # self.start_path = E:\Snow\data
    elif start_model == 1:
        arg = [
            "-FeatureLevelES31",
            "-ChannelID=bilibili",
            '-userdir=' + user_dir
        ]
    # 国际服启动命令
    # E:\SteamLibrary\steamapps\common\SNOWBREAK
    elif start_model == 2:
        arg = [
            "-FeatureLevelES31",
            "-channelid=seasun",
            "steamapps"
        ]
    return arg


def has_folder_in_path(path, dir_name):
    """
    判断指定路径是否包含名为 dir_name 的文件夹（区分大小写）
    :param path: 要检查的路径
    :param dir_name: 要检查的文件夹名字
    :return: bool: 如果包含 dir_name 文件夹返回 True，否则返回 False
    """
    try:
        path = Path(path)
        for item in path.iterdir():
            if item.is_dir() and item.name == dir_name:
                return True
        return False
    except Exception as e:
        print(f"检查子文件夹出错:{e}")
        return False


def is_exist_snowbreak():
    if config.server_interface.value != 2:
        game_name = '尘白禁区'
        game_class = 'UnrealWindow'
    else:
        game_name = 'Snowbreak: Containment Zone'  # 国际服
        game_class = 'UnrealWindow'
    return get_hwnd(game_name, game_class)


if __name__ == "__main__":
    get_hsv((124, 174, 235))
    get_hsv((112, 165, 238))
    # get_hsv((205, 202, 95))
    # get_hsv((209,207, 96))
