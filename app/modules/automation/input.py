import pyautogui
import time
import ctypes
import pydirectinput


class Input:
    # 禁用pyautogui的失败安全特性，防止意外中断
    pyautogui.FAILSAFE = False

    def __init__(self, logger):
        self.logger = logger  # 初始化日志记录器

    def mouse_click(self, x, y):
        """在屏幕上的（x，y）位置执行鼠标点击操作"""
        try:
            pydirectinput.click(x, y)
            self.logger.debug(f"鼠标点击 ({x}, {y})")
        except Exception as e:
            self.logger.error(f"鼠标点击出错：{e}")

    def move_click(self, x, y):
        """在屏幕上的（x，y）位置执行鼠标双击操作"""
        try:
            pydirectinput.moveTo(x, y)
            time.sleep(0.2)
            pydirectinput.click(x, y)
            self.logger.debug(f"鼠标移动后点击 ({x}, {y})")
        except Exception as e:
            self.logger.error(f"鼠标点击出错：{e}")

    def mouse_down(self, x, y):
        """在屏幕上的（x，y）位置按下鼠标按钮"""
        try:
            pydirectinput.mouseDown(x, y)
            self.logger.debug(f"鼠标按下 ({x}, {y})")
        except Exception as e:
            self.logger.error(f"鼠标按下出错：{e}")

    def mouse_up(self):
        """释放鼠标按钮"""
        try:
            pydirectinput.mouseUp()
            self.logger.debug("鼠标释放")
        except Exception as e:
            self.logger.error(f"鼠标释放出错：{e}")

    def mouse_move(self, x, y):
        """将鼠标光标移动到屏幕上的（x，y）位置"""
        try:
            pydirectinput.moveTo(x, y)
            self.logger.debug(f"鼠标移动 ({x}, {y})")
        except Exception as e:
            self.logger.error(f"鼠标移动出错：{e}")

    def drag_mouse(self, end_x, end_y, start_x=None, start_y=None, duration=1):
        try:
            if start_x and start_y:
                pyautogui.moveTo(start_x, start_y)
            # 一定要先停顿一下，原因不明
            time.sleep(0.5)
            pydirectinput.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=duration)
            time.sleep(0.5)
            pydirectinput.mouseUp()
            self.logger.debug(f"鼠标拖拽 ({start_x}, {start_y})->({end_x},{end_y})")
        except Exception as e:
            self.logger.error(f"鼠标拖拽出错：{e}")

    def mouse_scroll(self, count, direction=-1, pause=True):
        """
        滚动鼠标滚轮，方向和次数由参数指定
        :param count: 滚动次数
        :param direction: 每次滚动长度，正数表示向上滚动。负数向下
        :param pause:
        :return:
        """
        for _ in range(count):
            pyautogui.scroll(direction, _pause=pause)
        self.logger.debug(f"滚轮滚动 {count * direction} 次")

    def press_key(self, key, wait_time=0.2):
        """模拟键盘按键，可以指定按下的时间"""
        try:
            # 按下鼠标侧键
            if key in ["mouse5", "mouse4"]:
                # 定义鼠标事件常量
                MOUSEEVENTF_XDOWN = 0x0080  # 侧键按下
                MOUSEEVENTF_XUP = 0x0100  # 侧键松开
                # 定义侧键按钮
                XBUTTON1 = 0x0001  # 后退按钮
                XBUTTON2 = 0x0002  # 前进按钮

                # 模拟鼠标侧键点击
                def click_side_button(button):
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, button, 0)  # 按下
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, button, 0)  # 松开

                if key == 'mouse5':
                    # 模拟“前进”按钮点击
                    click_side_button(XBUTTON2)
                else:
                    # 模拟“后退”按钮点击
                    click_side_button(XBUTTON1)
                self.logger.debug(f"鼠标按下 {key}")
            else:
                pydirectinput.keyDown(key)
                time.sleep(wait_time)  # 等待指定的时间
                pydirectinput.keyUp(key)
                self.logger.debug(f"键盘按下 {key}")
        except Exception as e:
            self.logger.error(f"键盘按下 {key} 出错：{e}")

    def secretly_press_key(self, key, wait_time=0.2):
        """(不输出具体键位)模拟键盘按键，可以指定按下的时间"""
        try:
            pydirectinput.keyDown(key)
            time.sleep(wait_time)  # 等待指定的时间
            pydirectinput.keyUp(key)
            self.logger.debug("键盘按下 *")
        except Exception as e:
            self.logger.error(f"键盘按下 * 出错：{e}")

    def press_mouse(self, wait_time=0.2):
        """模拟鼠标左键的点击操作，可以指定按下的时间"""
        try:
            pyautogui.mouseDown()
            time.sleep(wait_time)  # 等待指定的时间
            pyautogui.mouseUp()
            self.logger.debug("按下鼠标左键")
        except Exception as e:
            self.logger.error(f"按下鼠标左键出错：{e}")

    def key_down(self, key):
        """在屏幕上的（x，y）位置执行鼠标点击操作"""
        try:
            pydirectinput.keyDown(key)
            self.logger.debug(f"键盘按下 {key}")
        except Exception as e:
            self.logger.error(f"键盘按下 {key} 出错：{e}")

    def key_up(self, key):
        """在屏幕上的（x，y）位置执行鼠标点击操作"""
        try:
            pydirectinput.keyUp(key)
            self.logger.debug(f"键盘松开 {key}")
        except Exception as e:
            self.logger.error(f"键盘松开 {key} 出错：{e}")
