from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCard, qconfig, FluentIconBase, LineEdit


class TextEditCard(SettingCard):
    textChanged = pyqtSignal(str)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, placeholder, content=None,
                 parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        title: str
            the title of card

        placeholder: str
            文本框的占位字符

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.line_edit = LineEdit(self)
        self.line_edit.setPlaceholderText(placeholder)
        self.setCurrentText()

        # 将文本框加入布局
        self.hBoxLayout.addWidget(self.line_edit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.line_edit.editingFinished.connect(self.__textChanged)

    def __textChanged(self):
        try:
            text = self.line_edit.text()
            self.setValue(text)
            # self.textChanged.emit(text)
        except Exception as e:
            print(e)

    def setCurrentText(self):
        # 初始化文本框
        try:
            self.line_edit.setText(qconfig.get(self.configItem))
        except Exception as e:
            print(e)

    def setValue(self, text: str):
        try:
            qconfig.set(self.configItem, text)
            # print(f"执行setValue:{qconfig.get(self.configItem)}")
        except Exception as e:
            print(e)
