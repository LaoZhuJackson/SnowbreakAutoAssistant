import time
import pyautogui
import pyscreeze


def click(image_path, timeout=30, confidence=0.7, wait_time=0.3, clicked_wait=0.5):
    """带超时的点击"""
    time.sleep(wait_time)
    start_time = time.time()
    while time.time() - start_time < timeout:
        # print(time.time() - start_time)
        try:
            # 尝试定位界面中的特定图像
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location is not None:
                # 图像找到，执行点击，退出循环
                print("找到对应图片，并单击")
                pyautogui.click(location)
                time.sleep(clicked_wait)
                return location
            # 图像未找到，等待一小段时间后重试
            time.sleep(0.5)
        except pyautogui.ImageNotFoundException:
            # 如果跳过没有检测到图片就跳过
            pass
    print("点击超时")
    return None


def ensure_click(location, image_path=None, times=2, confidence=0.7):
    """确保点击成功"""
    for i in range(times):
        time.sleep(0.5)
        if image_path:
            result = is_exist_image(image_path, confidence=confidence, wait_time=0)
            if result is True:
                pyautogui.moveTo(location)
                pyautogui.click(location)
            else:
                break
        else:
            pyautogui.moveTo(location)
            pyautogui.click(location)


# def click_by_box(image_path, location, timeout=5, confidence=0.7):
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         # print(time.time() - start_time)
#         try:
#             # 尝试定位界面中的特定图像
#             l = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
#             if l is not None:
#                 # 图像找到，执行点击，退出循环
#                 print("找到对应图片，单击指定位置")
#                 pyautogui.click(location)
#                 time.sleep(0.3)
#                 return True
#             # 图像未找到，等待一小段时间后重试
#             time.sleep(0.5)
#         except pyautogui.ImageNotFoundException:
#             # 如果跳过没有检测到图片就跳过
#             pass
#     print("点击超时")
#     return False


def wait_for_image(image_path, time_out=30, confidence=0.7):
    """等待特定的图片出现"""
    start_time = time.time()
    while time.time() - start_time < time_out:
        try:
            # 尝试定位界面中的特定图像
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location is None:
                time.sleep(1)
            else:
                print("成功识别")
                return True
        except pyautogui.ImageNotFoundException:
            # 如果跳过没有检测到图片就跳过
            pass
    print("跳过wait_for_image，执行下一步")
    return False


def wait_then_click(image_path, time_out=30, confidence=0.7):
    """等待到对应图片后立马点击"""
    start_time = time.time()
    while time.time() - start_time < time_out:
        try:
            # 尝试定位界面中的特定图像
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location is None:
                time.sleep(1)
            else:
                print("成功识别，开始点击")
                ensure_click(location, image_path)
                return True
        except pyautogui.ImageNotFoundException:
            # 如果跳过没有检测到图片就跳过
            pass
    print("跳过wait_then_click，执行下一步")
    return False


def is_exist_image(image_path, confidence=0.7, wait_time=0.3):
    """判断界面是否存在某个图片"""
    time.sleep(wait_time)
    try:
        # 尝试定位界面中的特定图像
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location is not None:
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False


def locate(image_path, confidence=0.7, wait_time=0.3):
    """判断界面是否存在某个图片"""
    time.sleep(wait_time)
    try:
        # 尝试定位界面中的特定图像
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location is not None:
            return location
        return None
    except pyautogui.ImageNotFoundException:
        return None


def exist_then_click(image_path, confidence=0.7, wait_time=0.3):
    """判断界面是否存在某个图片"""
    time.sleep(wait_time)
    try:
        # 尝试定位界面中的特定图像
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location is not None:
            ensure_click(location, image_path)
            return True
    except pyautogui.ImageNotFoundException:
        return False


def move_to_then_click(image_path, time_out=5, confidence=0.7):
    """先移动鼠标，再点击，适合界面有动画的时候"""
    start_time = time.time()
    while time.time() - start_time < time_out:
        try:
            # 尝试定位界面中的特定图像
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location is not None:
                pyautogui.moveTo(location)
                ensure_click(location, image_path, confidence=confidence)
                return True
        except pyautogui.ImageNotFoundException:
            pass
    print("跳过move_to_then_click，执行下一步")
    return False


def match_all_by_x(image_path, confidence=0.7, wait_time=0.3):
    time.sleep(wait_time)
    # 创建一个新列表来存储不接近的匹配项
    sortedMatches = []
    unique_matches = []
    # 定义距离阈值（以像素为单位）
    distance_threshold = 10
    try:
        # 尝试定位界面中的特定图像
        locations = pyautogui.locateAllOnScreen(image_path, confidence=confidence)
        locations_list = list(locations)
        # print(f"locations_list:{locations_list}")
        # print(f"locations:{locations}")
        if locations_list:
            # 根据 left 属性的值对匹配项进行排序
            sortedMatches = sorted(locations_list, key=lambda box: box.left)
        if sortedMatches:
            # 手动剔除重复项
            unique_matches.append(sortedMatches[0])  # 添加第一个匹配项作为基准
            for match in sortedMatches[1:]:
                last_unique = unique_matches[-1]
                dist_x = abs(match.left - last_unique.left)
                if dist_x > distance_threshold:
                    unique_matches.append(match)
            return unique_matches
    except pyautogui.ImageNotFoundException:
        return []
    except pyscreeze.ImageNotFoundException:
        return []


def drag(start_point, x_offset, y_offset, duration=1):
    # 将鼠标移动到起始位置
    pyautogui.moveTo(start_point)
    time.sleep(0.1)

    # 按下鼠标左键
    pyautogui.mouseDown()

    # 拖拽到目标位置
    pyautogui.moveTo(x=start_point.x + x_offset, y=start_point.y + y_offset, duration=duration)  # duration 为拖动时间

    # 释放鼠标左键
    pyautogui.mouseUp()


def back_to_home():
    root = "app/resource/images/in_game/"
    while not is_exist_image(root + "setting_icon.png"):
        if is_exist_image(root + "home.png"):
            move_to_then_click(root + "home.png")
        else:
            pyautogui.press('esc')
        time.sleep(1)
