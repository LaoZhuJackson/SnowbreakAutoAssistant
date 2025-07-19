import logging
import re

LogName = 'Umi-OCR_log'
LogFileName = 'Umi-OCR_debug.log'


class ColorCodeFilter(logging.Filter):
    def filter(self, record):
        if record.msg and isinstance(record.msg, str):
            record.msg = re.sub(r'\x1b\[[0-9;]*m', '', record.msg)  # 移除颜色代码
        return True


class Logger:

    def __init__(self):
        self.initLogger()

    def initLogger(self):
        '''初始化日志'''

        # 日志
        self.logger = logging.getLogger(LogName)
        self.logger.setLevel(logging.DEBUG)

        # 控制台
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.DEBUG)
        streamHandler.addFilter(ColorCodeFilter())  # 添加文字编码过滤器
        formatPrint = logging.Formatter(
            '【%(levelname)s】 %(message)s')
        streamHandler.setFormatter(formatPrint)
        # self.logger.addHandler(streamHandler)

        return
        # 日志文件
        fileHandler = logging.FileHandler(LogFileName, encoding='utf-8')  # 确保文件日志使用 UTF-8
        fileHandler.setLevel(logging.ERROR)
        formatFile = logging.Formatter(
            '''
【%(levelname)s】 %(asctime)s
%(message)s
    file: %(module)s | function: %(funcName)s | line: %(lineno)d
    thread_id: %(thread)d | thread_name: %(thread)s''')
        fileHandler.setFormatter(formatFile)
        self.logger.addHandler(fileHandler)


LOG = Logger()


def GetLog():
    return LOG.logger
