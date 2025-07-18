from PyQt5.QtWidgets import QFrame

from app.common.style_sheet import StyleSheet
from app.ui.help_interface import Ui_help


class Help(QFrame, Ui_help):
    def __init__(self, text: str, parent=None):
        super().__init__()

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self._initWidget()
        self._connect_to_slot()

    def _initWidget(self):
        self.load_markdown()
        StyleSheet.HELP_INTERFACE.apply(self)

    def _connect_to_slot(self):
        pass

    def load_markdown(self):
        with open('./docs/help.md', 'r', encoding='utf-8') as file:
            text = file.read()
            self.TextEdit_markdown.setMarkdown(text)
