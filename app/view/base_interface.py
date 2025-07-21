import sys

from PyQt5.QtWidgets import QTextBrowser

from app.common.logger import logger, stdout_stream, stderr_stream


class BaseInterface:
    def __init__(self):
        self.logger = logger
        self.auto = None

    def redirectOutput(self, log_widget):
        # 普通输出
        sys.stdout = stdout_stream
        # 报错输出
        sys.stderr = stderr_stream
        # 先断开可能存在的所有连接
        try:
            stdout_stream.message.disconnect()
            stderr_stream.message.disconnect()
        except TypeError:
            pass  # 没有连接存在时会抛出TypeError
        # 将新消息信号连接到对应输出位置
        stdout_stream.message.connect(lambda message: self.__updateDisplay(message, log_widget))
        stderr_stream.message.connect(lambda message: self.__updateDisplay(message, log_widget))

    def __updateDisplay(self, message, log_widget: QTextBrowser):
        # 将消息添加到 textBrowser，自动识别 HTML
        log_widget.insertHtml(message)
        log_widget.insertPlainText('\n')  # 为下一行消息留出空间
        log_widget.ensureCursorVisible()  # 滚动到最新消息

    def toggle_button(self, running):
        pass

    # def chose_auto(self, only_game=False):
    #     """
    #     自动选择auto，有游戏窗口时选游戏，没有游戏窗口时选启动器，都没有的时候循环，寻找频率1次/s
    #     :return:
    #     """
    #     timeout = Timer(20).start()
    #     while True:
    #         # 每次循环重新导入
    #         from app.modules.automation.automation import auto_starter, auto_game
    #         if win32gui.FindWindow(None, config.LineEdit_game_name.value) or only_game:
    #             if not auto_game:
    #                 instantiate_automation(auto_type='game')  # 尝试实例化 auto_game
    #             self.auto = auto_game
    #             flag = 'game'
    #         else:
    #             if not auto_starter:
    #                 instantiate_automation(auto_type='starter')  # 尝试实例化 auto_starter
    #             self.auto = auto_starter
    #             flag = 'starter'
    #         if self.auto:
    #             return flag
    #         if timeout.reached():
    #             logger.error("获取auto超时")
    #             break
