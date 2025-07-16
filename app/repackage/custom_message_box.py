import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

from qfluentwidgets import (
    MessageBoxBase,
    SubtitleLabel,
    LineEdit,
    PushButton,
    CaptionLabel,
    setTheme,
    Theme,
    PixmapLabel,
    BodyLabel,
)


class CustomMessageBox(MessageBoxBase):
    """Custom message box"""

    def __init__(self, parent=None, title="标题", content_type=None):
        super().__init__(parent)
        self.title = title
        self.titleLabel = SubtitleLabel(title, self)
        self.content_type = content_type
        self.content = self.init_content()

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.content)

        # change the text of button
        self.yesButton.setText("确定")
        self.cancelButton.setText("关闭")
        self.hideCancelButton()
        self.setClosableOnMaskClicked(True)

        # self.widget.setMinimumWidth(50)
        # self.widget.setMinimumHeight(50)

    def init_content(self):
        widget = None
        if self.content_type == "image":
            widget = PixmapLabel(self)
            widget.setObjectName("content")
        elif self.content_type == "markdown":
            widget = BodyLabel(self)
            widget.setTextFormat(QtCore.Qt.MarkdownText)
            widget.setWordWrap(True)
            widget.setObjectName("content")
        return widget
