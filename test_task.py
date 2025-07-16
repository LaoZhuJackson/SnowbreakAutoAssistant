import ctypes
import time

import cv2
import numpy as np
import win32gui
from PIL import Image

from app.common.image_utils import ImageUtils
from app.common.utils import is_fullscreen
from app.modules.base_task.base_task import BaseTask
from app.modules.fishing.fishing import FishingModule
from app.modules.water_bomb.water_bomb import WaterBombModule
from app.view.subtask import SubTask

# WaterBombModule().run()
# print(is_fullscreen(658872))

# hwnd = 396808
# win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)

# FishingModule().run()
# FishingModule().get_press_key()

# class test(BaseTask):
#     def __init__(self):
#         super().__init__()
#
#     def format_and_replace(self, data):
#         results = []
#         # 遍历所有文本框
#         num_boxes = len(data['text'])
#         for i in range(num_boxes):
#             text = data['text'][i]
#             conf = int(data['conf'][i])
#
#             if text.strip() and conf > 0:  # 只处理有文本且置信度大于0的结果
#                 # 提取坐标
#                 left = data['left'][i]
#                 top = data['top'][i]
#                 width = data['width'][i]
#                 height = data['height'][i]
#
#                 # 坐标对角点
#                 bottom_right = [left + width, top + height]
#
#                 # 按照要求的格式组织数据
#                 result = [text, conf / 100.0, [[left, top], bottom_right]]
#                 results.append(result)
#         return results
#
#     def run(self):
#         # pytesseract.pytesseract.tesseract_cmd = r'D:\software\tesseract-ocr\tesseract.exe'
#         # while True:
#         #     self.auto.take_screenshot()
#         #     image = Image.fromarray(self.auto.current_screenshot)
#         #     data = pytesseract.image_to_data(image, lang='chi_sim', output_type=pytesseract.Output.DICT)
#         #     print(self.format_and_replace(data))
#
#     def stop_ocr(self):
#         pass

import cv2


def sift_similarity(img1, img2):
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        inliers = mask.sum()
        return inliers / len(good)
    else:
        return 0.0


import cv2
import numpy as np


def find_a_in_b_1(img_a, img_b, min_matches=1, ransac_thresh=5.0, show_result=True):
    """
    使用 SIFT 特征匹配定位图 A 在图 B 中的位置
    :param img_a: 小图（图 A），numpy 数组（灰度或彩色）
    :param img_b: 大图（图 B），numpy 数组（灰度或彩色）
    :param min_matches: 最低有效匹配点数阈值
    :param ransac_thresh: RANSAC 重投影误差阈值
    :param show_result: 是否显示匹配结果和框选位置
    :return: 图 A 在图 B 中的位置坐标 (x1, y1, x2, y2)，若未找到返回 None
    """
    # 转换为灰度图
    gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY) if len(img_a.shape) == 3 else img_a
    gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY) if len(img_b.shape) == 3 else img_b

    # 初始化 SIFT 检测器
    sift = cv2.SIFT_create()

    # 检测关键点和计算描述子
    kp_a, des_a = sift.detectAndCompute(gray_a, None)
    kp_b, des_b = sift.detectAndCompute(gray_b, None)

    # 特征匹配（使用 FLANN 加速）
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des_a, des_b, k=2)

    # Lowe's 比率测试筛选优质匹配
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # 检查是否有足够匹配点
    if len(good_matches) < min_matches:
        print(f"匹配点不足 {min_matches} 个，当前匹配数：{len(good_matches)}")
        return None

    # 提取匹配点坐标
    src_pts = np.float32([kp_a[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_b[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 使用 RANSAC 计算单应性矩阵
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_thresh)
    inliers_mask = mask.ravel().tolist()

    # 计算图 A 在图 B 中的投影角点
    h, w = gray_a.shape
    corners_a = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
        -1, 1, 2
    )
    corners_b = cv2.perspectiveTransform(corners_a, H)

    # 转换为整数坐标
    x_coords = corners_b[:, 0, 0].astype(int)
    y_coords = corners_b[:, 0, 1].astype(int)
    x1, x2 = min(x_coords), max(x_coords)
    y1, y2 = min(y_coords), max(y_coords)

    # 可视化结果
    if show_result:
        # 绘制匹配点
        draw_params = dict(
            matchColor=(0, 255, 0),  # 绿色连线
            singlePointColor=None,
            matchesMask=inliers_mask,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )
        img_matches = cv2.drawMatches(
            img_a, kp_a, img_b, kp_b, good_matches, None, **draw_params
        )

        # 在图 B 中绘制矩形框
        img_result = cv2.polylines(
            img_b, [np.int32(corners_b)], True, (0, 0, 255), 2, cv2.LINE_AA
        )

        # 显示结果
        cv2.imshow("Matches", img_matches)
        cv2.imshow("Detected Location", img_result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return (x1, y1, x2, y2)


import cv2
import numpy as np


def find_a_in_b_2(a_img, b_img, min_matches=2, match_ratio=0.5, ransac_thresh=5.0):
    """
    在图像 B 中查找图像 A 的所有可能位置
    参数:
        a_img: 模板图像 (numpy.ndarray)
        b_img: 背景图像 (numpy.ndarray)
        min_matches: 最低匹配点数量阈值
        match_ratio: Lowe's 比率测试阈值 (0.7~0.8)
        ransac_thresh: RANSAC 重投影误差阈值
    返回:
        list: 包含字典的列表，每个字典包含 'bbox' 和 'score'
    """
    # 初始化 SIFT 检测器
    sift = cv2.SIFT_create()

    # 转换为灰度图
    a_img = cv2.cvtColor(a_img, cv2.COLOR_BGR2GRAY) if len(a_img.shape) == 3 else a_img
    b_img = cv2.cvtColor(b_img, cv2.COLOR_BGR2GRAY) if len(b_img.shape) == 3 else b_img

    # 检测特征点并计算描述子
    kp_a, des_a = sift.detectAndCompute(a_img, None)
    kp_b, des_b = sift.detectAndCompute(b_img, None)

    # 没有足够特征点时直接返回空列表
    if des_a is None or des_b is None or len(des_a) < 2 or len(des_b) < 2:
        return []

    # 使用 FLANN 匹配器加速匹配
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des_a, des_b, k=2)

    # 应用 Lowe's 比率测试筛选优质匹配
    good_matches = []
    for m, n in matches:
        if m.distance < match_ratio * n.distance:
            good_matches.append(m)

    # 如果没有足够匹配点则返回空
    if len(good_matches) < min_matches:
        return []

    # 将匹配点转换为坐标数组
    src_pts = np.float32([kp_a[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_b[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 使用 RANSAC 多次查找所有可能的单应性矩阵
    results = []
    while len(good_matches) >= min_matches:
        # 计算单应性矩阵
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_thresh)

        if H is None:
            break

        # 统计内点数量和索引
        inliers = mask.ravel().tolist()
        inlier_count = sum(inliers)

        if inlier_count < min_matches:
            break

        # 计算模板在目标图像中的位置（投影角点）
        h, w = a_img.shape[:2]
        corners = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
            -1, 1, 2
        )
        projected_corners = cv2.perspectiveTransform(corners, H)

        # 计算边界框
        x_coords = projected_corners[:, 0, 0]
        y_coords = projected_corners[:, 0, 1]
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)

        # 记录结果（坐标限制在图像范围内）
        bbox = [
            max(0, int(x_min)),
            max(0, int(y_min)),
            min(b_img.shape[1] - 1, int(x_max)),
            min(b_img.shape[0] - 1, int(y_max)),
        ]

        # 计算相似度得分（内点比例）
        score = inlier_count / len(good_matches)
        results.append({"bbox": bbox, "score": score})

        # 移除已使用的内点，继续查找下一个可能的位置
        remaining_idx = [i for i, val in enumerate(inliers) if val == 0]
        src_pts = src_pts[remaining_idx]
        dst_pts = dst_pts[remaining_idx]
        good_matches = [good_matches[i] for i in remaining_idx]

    # 可视化结果
    if len(results) > 0:
        output = cv2.cvtColor(b_img, cv2.COLOR_GRAY2BGR)
        for match in results:
            x1, y1, x2, y2 = match["bbox"]
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                output,
                f"Score: {match['score']:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )
        cv2.imshow("Matches", output)
        cv2.waitKey(0)
    else:
        print("未找到匹配位置")

    return results


# 示例用法
# if __name__ == "__main__":
#     # 读取图像（灰度图）
#     a_img = cv2.imread('app/resource/images/water_bomb/hp.png')
#     b_img = cv2.imread('C:/Users/laozhu/Desktop/2560_1440/PixPin_2025-02-28_16-05-00.png')
#     # a_img = cv2.imread("C:/Users/laozhu/Desktop/2560_1440/PixPin_2025-02-28_15-52-19.png", 0)  # 模板图像
#     # b_img = cv2.imread("C:/Users/laozhu/Desktop/2560_1440/PixPin_2025-02-28_15-47-36.png", 0)  # 背景图像
#
#     # 查找所有匹配位置
#     matches = find_a_in_b(a_img, b_img)

# 可视化结果
# if len(matches) > 0:
#     output = cv2.cvtColor(b_img, cv2.COLOR_GRAY2BGR)
#     for match in matches:
#         x1, y1, x2, y2 = match['bbox']
#         cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(output, f"Score: {match['score']:.2f}",
#                     (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
#     cv2.imshow("Matches", output)
#     cv2.waitKey(0)
# else:
#     print("未找到匹配位置")

# 示例用法
# if __name__ == "__main__":
#     # 读取图像
#     img_b = cv2.imread("large_image.jpg")  # 大图（背景图）
#     img_a = cv2.imread("small_template.jpg")  # 小图（待查找的模板）
#
#     # 查找位置
#     location = find_a_in_b(img_a, img_b)
#
#     if location:
#         x1, y1, x2, y2 = location
#         print(f"图 A 在图 B 中的位置坐标：左上角 ({x1}, {y1})，右下角 ({x2}, {y2})")
#     else:
#         print("未找到图 A 的位置")

if __name__ == "__main__":
    img1 = cv2.imread("app/resource/images/water_bomb/gem_of_life_steal.png")
    # img1 = cv2.imread('app/resource/images/water_bomb/reverse_magic_steal.png')
    # img1 = cv2.imread('app/resource/images/water_bomb/1.png')
    # img1 = cv2.imread('app/resource/images/water_bomb/hp.png')
    img2 = cv2.imread(
        "C:/Users/laozhu/Desktop/2560_1440/PixPin_2025-02-28_15-29-15.png"
    )
    # img2 = ImageUtils.extract_letters(img2,[255,255,255],128)
    # ImageUtils.show_ndarray(img2)
    # img2 = cv2.imread('app/resource/images/water_bomb/4.png')
    # ctypes.windll.user32.SetProcessDPIAware()
    # image = ImageUtils.show_extract('app/resource/images/water_bomb/steal_select_2.png',[(255, 202, 228), 128])
    start_time = time.time()
    print(find_a_in_b_2(img1, img2))
    print(f"用时{time.time() - start_time}")
