import sys
# from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextBrowser
# from PySide6.QtGui import QIcon

from pathlib import Path


def app_dir():
    """Returns the base application path."""
    if hasattr(sys, "frozen"):
        # Handles PyInstaller
        return Path(sys.executable).parent  # 使用pyinstaller打包后的exe目录
    return Path(__file__).parent  # 没打包前的py目录


class Config:
    app_ver = "2.0.2-official"
    app_name = "SAA"
    app_exec = "SAA"
    app_publisher = "laozhu"
    app_url = "https://github.com/LaoZhuJackson/SnowbreakAutoAssistant"
    app_icon = "app/resource/images/logo.ico"
    app_dir = "D:/Learning/Project/auto_chenbai"
    # app_dir = app_dir()

# class MainWindow(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         # self.setWindowFlags(Qt.WindowCloseButtonHint)  # 只显示关闭按钮
#         self.setFixedSize(400, 300)
#
#         self.setWindowTitle("HELLO")
#         layout = QVBoxLayout(self)
#         purpose = QTextBrowser()
#         purpose.setText("Perfect Build!\n" * 50)
#         purpose.setReadOnly(True)  # 设置为只读，防止用户编辑文本
#         layout.addWidget(purpose)
#         self.setLayout(layout)
#
#
# if __name__ == "__main__":
#     app = QApplication([])
#     window = MainWindow()
#     window.setWindowIcon(QIcon(Config.app_icon))
#     window.show()
#     app.exec()
