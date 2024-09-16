import sys
import time

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFrame, QTextEdit
from qfluentwidgets import FluentIcon as FIF, PlainTextEdit
from PyQt5.QtCore import QObject, pyqtSignal

from ui.terminal_interface import Ui_Terminal


# class TerminalTextEdit(PlainTextEdit):
#     def __init__(self, original_stream):
#         super().__init__()
#         # 留原始输出流
#         self.original_stream = original_stream
#
#     def write(self, text):
#         try:
#             self.original_stream.write(text)
#             self.appendPlainText(text)
#         except Exception as e:
#             # 如果发生异常，打印到原始标准错误流
#             self.original_stream.write(f"Error writing to original stream: {str(e)}\n")
#             self.original_stream.flush()


class Terminal(QFrame, Ui_Terminal):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        # self.textEdit = TerminalTextEdit(self.original_stdout)
        # self.textEdit.setEnabled(False)
        # self.verticalLayout.addWidget(self.textEdit)
        # self.verticalLayout.setStretch(1, 11)



        self._initWidget()
        self._connect_to_slot()


    def _initWidget(self):
        pass

    def _connect_to_slot(self):
        pass
