import ctypes
import time
import traceback

import win32con
import win32gui
import win32ui
import numpy as np
import cv2

from app.common.image_utils import ImageUtils
from app.common.logger import logger
from app.common.utils import is_fullscreen
from app.modules.automation.timer import Timer


def auto_crop_image(img):
    """裁切四周的黑边"""
    # 如果是全图都是黑的
    if np.mean(img) < 50:
        return img
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # =============== 垂直方向裁剪（左右黑边） ===============
    col_sum = np.sum(gray, axis=0) / 255  # 每列像素强度总和

    # 动态阈值（取最大值的3%作为黑边判断基准）
    col_threshold = np.max(col_sum) * 0.03

    # 左边界检测（第一个非黑列）
    left = 0
    for i in range(w):
        if col_sum[i] > col_threshold:
            left = i + 1  # 直接使用检测到的索引
            break

    # 右边界检测（最后一个非黑列）
    right = w - 1
    for i in range(w - 1, -1, -1):
        if col_sum[i] > col_threshold:
            right = i - 1
            break

    # =============== 水平方向裁剪（顶部标题+底部黑边） ===============
    row_sum = np.sum(gray, axis=1) / 255

    # 动态阈值（取最大值的3%作为内容判断基准）
    row_threshold = np.max(row_sum) * 0.03

    # 顶部边界检测
    top = 0
    for i in range(h):
        if row_sum[i] > row_threshold:
            top = i
            break

    # 底部边界检测
    bottom = h - 1
    for i in range(h - 1, -1, -1):
        if row_sum[i] > row_threshold:
            bottom = i
            break

    # =============== 执行精确裁剪 ===============
    cropped = img[top:bottom + 1, left:right + 1]  # Python切片含头不含尾
    return cropped


class Screenshot:
    _screenshot_interval = Timer(0.1)

    def __init__(self, logger=None):
        self.base_width = 1920
        self.base_height = 1080
        self.logger = logger
        # 排除缩放干扰
        ctypes.windll.user32.SetProcessDPIAware()

    def get_window(self, title):
        hwnd = win32gui.FindWindow(None, title)  # 获取窗口句柄
        if hwnd:
            # logger.info(f"找到窗口‘{title}’的句柄为：{hwnd}")
            return hwnd
        else:
            self.logger.error(f"未找到窗口: {title}")
            return None

    def screenshot(self, hwnd, crop=(0, 0, 1, 1), is_starter=True):
        """
        截取特定区域
        :param is_starter: 是否是启动器
        :param hwnd: 需要截图的窗口句柄
        :param crop: 截取区域, 格式为 (crop_left, crop_top, crop_right, crop_bottom)，范围是0到1之间，表示相对于窗口的比例
        :return:
        """

        try:
            self._screenshot_interval.wait()
            self._screenshot_interval.reset()
            # 获取带标题的窗口尺寸
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # print(left, top, right, bottom)
            w = right - left
            h = bottom - top
            # print(w, h)

            # 获取设备上下文
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # 创建位图对象
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bitmap)

            # 进行截图
            user32 = ctypes.windll.user32
            # 启动器0,1,2均可以，但是游戏窗口必须要是2,0和1都是黑屏，2: 捕捉包括窗口的边框、标题栏以及整个窗口的内容
            user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)  # PW_RENDERFULLCONTENT=2
            # 转换为 numpy 数组
            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)
            # img_size = np.frombuffer(bmpstr, dtype=np.uint8).size
            img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))
            # # 取平均颜色
            # color = cv2.mean(img)
            # # 如果是启动器且全黑
            # if is_starter and color == (17.0, 16.0, 15.0, 255.0):
            #     # 最小化窗口
            #     win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            #     time.sleep(0.01)  # 等待一下
            #     # 恢复窗口
            #     win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            #     time.sleep(0.3)
            #     # 置低窗口
            #     win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            #     user32 = ctypes.windll.user32
            #     # 启动器0,1,2均可以，但是游戏窗口必须要是2,0和1都是黑屏，2: 捕捉包括窗口的边框、标题栏以及整个窗口的内容
            #     user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)  # PW_RENDERFULLCONTENT=2
            #
            #     # 转换为 numpy 数组
            #     bmpinfo = bitmap.GetInfo()
            #     bmpstr = bitmap.GetBitmapBits(True)
            #     img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))

            # 释放资源
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            # OpenCV 处理
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if not is_fullscreen(hwnd):
                img = img[40:, :, :]
                h -= 40
                # ImageUtils.show_ndarray(img)
                img = auto_crop_image(img)
            img_crop, relative_pos = ImageUtils.crop_image(img, crop, hwnd)

            # 缩放图像以自适应分辨率图像识别
            if is_starter:
                scale_x = 1
                scale_y = 1
            else:
                scale_x = self.base_width / w
                scale_y = self.base_height / h

            # win32api.SetCursorPos((left+screenshot_pos[0], top+screenshot_pos[1]))
            # ImageUtils.show_ndarray(img_resized)
            return img_crop, scale_x, scale_y, relative_pos
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"截图失败：{repr(e)},窗口可以不置顶但不能最小化")
            return None


if __name__ == '__main__':
    # 替换成你的游戏窗口标题
    game_window = "尘白禁区"
    screen = Screenshot(logger=logger)
    hwnd = screen.get_window(game_window)
    result = screen.screenshot(hwnd, (0, 0, 1, 1), False)

    # game_window = "尘白禁区"
    # screen = Screenshot(logger=logger)
    # hwnd = screen.get_window(game_window)
    # result = screen.take_screenshot(hwnd, (0.5, 0.5, 1, 1), False)

    if result is not None:
        img_resized, scale_x, scale_y, screenshot_pos = result
        print(scale_x, scale_y, screenshot_pos)
        img_resized = auto_crop_image(img_resized)
        # cv2.imshow("Game Screenshot", img_resized)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
