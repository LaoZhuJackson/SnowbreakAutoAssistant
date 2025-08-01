# coding:utf-8
"""
PyQt5 QtWidgets 模拟模块
提供 QTextBrowser 和其他 Widget 的基础实现
"""

import sys
from typing import Any, Optional
from .QtCore import QObject


class QWidget(QObject):
    """PyQt5 QWidget 模拟器"""
    
    def __init__(self, parent=None):
        """初始化 QWidget"""
        super().__init__(parent)
        self._enabled = True
        self._visible = True
        self._geometry = (0, 0, 100, 100)  # x, y, width, height
        self._style_sheet = ""
        self._object_name = ""
    
    def setEnabled(self, enabled: bool):
        """设置是否可用"""
        self._enabled = enabled
    
    def isEnabled(self) -> bool:
        """获取是否可用"""
        return self._enabled
    
    def setVisible(self, visible: bool):
        """设置是否可见"""
        self._visible = visible
    
    def isVisible(self) -> bool:
        """获取是否可见"""
        return self._visible
    
    def show(self):
        """显示控件"""
        self._visible = True
    
    def hide(self):
        """隐藏控件"""
        self._visible = False
    
    def setGeometry(self, x: int, y: int, width: int, height: int):
        """设置几何位置"""
        self._geometry = (x, y, width, height)
    
    def geometry(self) -> tuple:
        """获取几何位置"""
        return self._geometry
    
    def setStyleSheet(self, style_sheet: str):
        """设置样式表"""
        self._style_sheet = style_sheet
    
    def styleSheet(self) -> str:
        """获取样式表"""
        return self._style_sheet
    
    def setObjectName(self, name: str):
        """设置对象名称"""
        self._object_name = name
    
    def objectName(self) -> str:
        """获取对象名称"""
        return self._object_name


class QTextEdit(QWidget):
    """PyQt5 QTextEdit 模拟器"""
    
    def __init__(self, parent=None):
        """初始化 QTextEdit"""
        super().__init__(parent)
        self._text = ""
        self._html = ""
        self._read_only = False
        self._cursor_position = 0
    
    def setText(self, text: str):
        """设置纯文本"""
        self._text = text
        self._html = text
        self._cursor_position = len(text)
    
    def text(self) -> str:
        """获取纯文本"""
        return self._text
    
    def setHtml(self, html: str):
        """设置HTML文本"""
        self._html = html
        # 简单移除HTML标签作为纯文本
        import re
        self._text = re.sub(r'<[^>]+>', '', html)
        self._cursor_position = len(self._text)
    
    def toHtml(self) -> str:
        """获取HTML文本"""
        return self._html
    
    def insertPlainText(self, text: str):
        """插入纯文本"""
        if self._cursor_position >= len(self._text):
            self._text += text
            self._html += text
        else:
            self._text = self._text[:self._cursor_position] + text + self._text[self._cursor_position:]
            self._html = self._html[:self._cursor_position] + text + self._html[self._cursor_position:]
        self._cursor_position += len(text)
        
        # 如果是在命令行环境，直接输出到控制台
        if not self._read_only:
            sys.stdout.write(text)
            sys.stdout.flush()
    
    def insertHtml(self, html: str):
        """插入HTML文本"""
        # 在实际GUI环境中，这会以HTML格式插入
        # 在模拟环境中，我们移除HTML标签并插入纯文本
        import re
        plain_text = re.sub(r'<[^>]+>', '', html)
        
        if self._cursor_position >= len(self._html):
            self._html += html
            self._text += plain_text
        else:
            self._html = self._html[:self._cursor_position] + html + self._html[self._cursor_position:]
            self._text = self._text[:self._cursor_position] + plain_text + self._text[self._cursor_position:]
        
        self._cursor_position += len(plain_text)
        
        # 在命令行环境中输出带颜色的文本（如果支持）
        if not self._read_only:
            # 尝试解析简单的颜色HTML标签
            color_text = self._parse_html_colors(html)
            sys.stdout.write(color_text)
            sys.stdout.flush()
    
    def _parse_html_colors(self, html: str) -> str:
        """解析HTML颜色标签（简单实现）"""
        import re
        
        # 简单的颜色映射（ANSI颜色代码）
        color_map = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'gray': '\033[37m',
            'grey': '\033[37m',
            'orange': '\033[33m',  # 橙色用黄色代替
        }
        
        reset = '\033[0m'
        
        # 查找颜色标签
        pattern = r'<span style="color:\s*([^;"]+);"[^>]*>(.*?)</span>'
        
        def replace_color(match):
            color = match.group(1).lower().strip()
            text = match.group(2)
            if color in color_map:
                return f"{color_map[color]}{text}{reset}"
            return text
        
        result = re.sub(pattern, replace_color, html)
        # 移除其他HTML标签
        result = re.sub(r'<[^>]+>', '', result)
        return result
    
    def clear(self):
        """清空文本"""
        self._text = ""
        self._html = ""
        self._cursor_position = 0
    
    def setReadOnly(self, read_only: bool):
        """设置只读模式"""
        self._read_only = read_only
    
    def isReadOnly(self) -> bool:
        """获取是否只读"""
        return self._read_only
    
    def ensureCursorVisible(self):
        """确保光标可见（在模拟器中无操作）"""
        pass


class QTextBrowser(QTextEdit):
    """PyQt5 QTextBrowser 模拟器"""
    
    def __init__(self, parent=None):
        """初始化 QTextBrowser"""
        super().__init__(parent)
        self.setReadOnly(True)  # QTextBrowser 默认是只读的
        self._source = ""
        self._search_paths = []
    
    def setSource(self, source: str):
        """设置源文档"""
        self._source = source
    
    def source(self) -> str:
        """获取源文档"""
        return self._source
    
    def setSearchPaths(self, paths: list):
        """设置搜索路径"""
        self._search_paths = paths.copy()
    
    def searchPaths(self) -> list:
        """获取搜索路径"""
        return self._search_paths.copy()
    
    def backward(self):
        """后退（在模拟器中无操作）"""
        pass
    
    def forward(self):
        """前进（在模拟器中无操作）"""
        pass
    
    def home(self):
        """回到主页（在模拟器中无操作）"""
        pass
    
    def reload(self):
        """重新加载（在模拟器中无操作）"""
        pass


class QApplication:
    """PyQt5 QApplication 模拟器"""
    
    _instance = None
    
    def __init__(self, argv=None):
        """初始化 QApplication"""
        if QApplication._instance is None:
            QApplication._instance = self
        self._argv = argv or []
        self._quit_called = False
    
    @staticmethod
    def instance():
        """获取应用程序实例"""
        return QApplication._instance
    
    def exec_(self) -> int:
        """执行应用程序主循环（模拟）"""
        print("QApplication: 应用程序在模拟模式下运行")
        return 0
    
    def quit(self):
        """退出应用程序"""
        self._quit_called = True
        print("QApplication: 应用程序退出")
    
    def processEvents(self):
        """处理事件（在模拟器中无操作）"""
        pass


# 常用控件别名
QLabel = QWidget
QPushButton = QWidget
QLineEdit = QTextEdit
QFrame = QWidget
QScrollArea = QWidget
QMainWindow = QWidget
