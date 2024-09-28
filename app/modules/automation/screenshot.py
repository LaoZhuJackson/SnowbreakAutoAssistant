from PIL import Image
import pyautogui
import win32gui


class Screenshot:
    @staticmethod
    def is_application_fullscreen(window):
        """
        判断是否全屏
        :param window: 游戏窗口
        :return:
        """
        screen_width, screen_height = pyautogui.size()
        return (window.width, window.height) == (screen_width, screen_height)

    @staticmethod
    def get_window_real_resolution(window):
        left, top, right, bottom = win32gui.GetClientRect(window._hWnd)
        return right - left, bottom - top

    @staticmethod
    def get_window_region(window):
        """
        获取窗口区域
        :param window: 游戏窗口
        :return:
        """
        if Screenshot.is_application_fullscreen(window):
            return window.left, window.top, window.width, window.height
        else:
            real_width, real_height = Screenshot.get_window_real_resolution(window)
            other_border = (window.width - real_width) // 2
            up_border = window.height - real_height - other_border
            return window.left + other_border, window.top + up_border, window.width - other_border - other_border, window.height - up_border - other_border

    @staticmethod
    def get_window(title):
        """
        获取窗口
        :param title: 窗口名
        :return:
        """
        windows = pyautogui.getWindowsWithTitle(title)
        if windows:
            window = windows[0]
            return window
        return False

    @staticmethod
    def take_screenshot(title, crop=(0, 0, 1, 1)):
        """
        截图窗口区域
        :param title: 窗口名
        :param crop: 截图的裁剪区域。
        :return:
        """
        window = Screenshot.get_window(title)
        if window:
            left, top, width, height = Screenshot.get_window_region(window)

            screenshot = pyautogui.screenshot(region=(
                int(left + width * crop[0]),
                int(top + height * crop[1]),
                int(width * crop[2]),
                int(height * crop[3])
            ))

            real_width, _ = Screenshot.get_window_real_resolution(window)
            if real_width > 1920:
                screenshot_scale_factor = 1920 / real_width
                screenshot = screenshot.resize((int(1920 * crop[2]), int(1080 * crop[3])))
            else:
                screenshot_scale_factor = 1

            screenshot_pos = (
                int(left + width * crop[0]),
                int(top + height * crop[1]),
                int(width * crop[2] * screenshot_scale_factor),
                int(height * crop[3] * screenshot_scale_factor)
            )

            return screenshot, screenshot_pos, screenshot_scale_factor

        return False
