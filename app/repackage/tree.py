from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidgetItem,
    QFrame,
    QHBoxLayout,
    QTreeWidgetItemIterator,
    QScrollArea,
    QApplication,
)
from qfluentwidgets import TreeWidget, ScrollArea

from app.common.style_sheet import StyleSheet


class Frame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName("frame")
        StyleSheet.VIEW_INTERFACE.apply(self)

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)


class TreeFrame_person(Frame):
    itemStateChanged = pyqtSignal(int, int)

    def __init__(self, parent=None, enableCheck=False):
        super().__init__(parent)
        self.parent = parent
        self.tree = TreeWidget(self.parent)
        self.addWidget(self.tree)

        item1 = QTreeWidgetItem(["人物碎片"])
        item1.addChildren(
            [
                QTreeWidgetItem(["肴"]),
                QTreeWidgetItem(["安卡希雅"]),
                QTreeWidgetItem(["里芙"]),
                QTreeWidgetItem(["辰星"]),
                QTreeWidgetItem(["茉莉安"]),
                QTreeWidgetItem(["芬妮"]),
                QTreeWidgetItem(["芙提雅"]),
                QTreeWidgetItem(["瑟瑞斯"]),
                QTreeWidgetItem(["琴诺"]),
                QTreeWidgetItem(["猫汐尔"]),
                QTreeWidgetItem(["晴"]),
                QTreeWidgetItem(["恩雅"]),
                QTreeWidgetItem(["妮塔"]),
            ]
        )
        self.tree.addTopLevelItem(item1)

        self.tree.setHeaderHidden(True)

        # 连接展开和收起信号到槽函数
        self.tree.itemExpanded.connect(self.adjustSizeToTree)
        self.tree.itemCollapsed.connect(self.adjustSizeToTree)
        # 禁用树状组件的滚动条
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFixedSize(250, 45)

        if enableCheck:
            it = QTreeWidgetItemIterator(self.tree)
            while it.value():
                it.value().setCheckState(0, Qt.Unchecked)
                it += 1

        self.tree.itemChanged.connect(self.onItemChanged)

    def adjustSizeToTree(self):
        """
        调整 Frame 的大小以适应 QTreeWidget 的展开状态
        """
        # 获取树状结构的总行数
        total_height = 0
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            total_height += self.tree.sizeHintForIndex(
                self.tree.indexFromItem(item)
            ).height()
            total_height += self._calculateHeightForChildren(item)

        # 调整当前窗口大小
        self.setFixedSize(250, total_height + 5)  # 适当增加额外的空间

    def _calculateHeightForChildren(self, item):
        """递归计算子节点的高度"""
        height = 0
        if item.isExpanded():
            for i in range(item.childCount()):
                child = item.child(i)
                height += self.tree.sizeHintForIndex(
                    self.tree.indexFromItem(child)
                ).height()
                height += self._calculateHeightForChildren(child)
        return height

    def onItemChanged(self, item, column):
        item_path = self.get_item_path(item)
        if len(item_path) == 1:
            index = item_path[0]
        else:
            index = item_path[1] + 1
        self.itemStateChanged.emit(index, item.checkState(0))

    def get_item_path(self, item):
        """
        获取指定 QTreeWidgetItem 的完整路径，返回层级中的所有行索引。
        """
        path = []
        current_item = item

        # 一直向上查找父项，直到到达顶层
        while current_item is not None:
            parent = current_item.parent()
            if parent is None:
                # 如果没有父级，说明是顶层项，使用 topLevelItemCount() 查找顶层项索引
                index = self.tree.indexOfTopLevelItem(current_item)
            else:
                # 如果有父级，使用父级的 indexOfChild() 方法找到相对于父级的索引
                index = parent.indexOfChild(current_item)

            # 在路径中记录当前层的索引
            path.insert(0, index)
            current_item = parent

        return path


class TreeFrame_weapon(Frame):
    itemStateChanged = pyqtSignal(int, int)

    def __init__(self, parent=None, enableCheck=False):
        super().__init__(parent)
        self.parent = parent
        self.tree = TreeWidget(self.parent)
        self.addWidget(self.tree)

        item1 = QTreeWidgetItem(["武器"])
        item1.addChildren(
            [
                QTreeWidgetItem(["彩虹打火机"]),
                QTreeWidgetItem(["草莓蛋糕"]),
                QTreeWidgetItem(["深海呼唤"]),
            ]
        )
        self.tree.addTopLevelItem(item1)

        self.tree.setHeaderHidden(True)

        # 连接展开和收起信号到槽函数
        self.tree.itemExpanded.connect(self.adjustSizeToTree)
        self.tree.itemCollapsed.connect(self.adjustSizeToTree)
        # 禁用树状组件的滚动条
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFixedSize(250, 45)

        if enableCheck:
            it = QTreeWidgetItemIterator(self.tree)
            while it.value():
                it.value().setCheckState(0, Qt.Unchecked)
                it += 1

        self.tree.itemChanged.connect(self.onItemChanged)

    def adjustSizeToTree(self):
        """
        调整 Frame 的大小以适应 QTreeWidget 的展开状态
        """
        # 获取树状结构的总行数
        total_height = 0
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            total_height += self.tree.sizeHintForIndex(
                self.tree.indexFromItem(item)
            ).height()
            total_height += self._calculateHeightForChildren(item)

        # 调整当前窗口大小
        self.setFixedSize(250, total_height + 5)  # 适当增加额外的空间

    def _calculateHeightForChildren(self, item):
        """递归计算子节点的高度"""
        height = 0
        if item.isExpanded():
            for i in range(item.childCount()):
                child = item.child(i)
                height += self.tree.sizeHintForIndex(
                    self.tree.indexFromItem(child)
                ).height()
                height += self._calculateHeightForChildren(child)
        return height

    def onItemChanged(self, item, column):
        item_path = self.get_item_path(item)
        if len(item_path) == 1:
            index = item_path[0]
        else:
            index = item_path[1] + 1
        self.itemStateChanged.emit(index, item.checkState(0))

    def get_item_path(self, item):
        """
        获取指定 QTreeWidgetItem 的完整路径，返回层级中的所有行索引。
        """
        path = []
        current_item = item

        # 一直向上查找父项，直到到达顶层
        while current_item is not None:
            parent = current_item.parent()
            if parent is None:
                # 如果没有父级，说明是顶层项，使用 topLevelItemCount() 查找顶层项索引
                index = self.tree.indexOfTopLevelItem(current_item)
            else:
                # 如果有父级，使用父级的 indexOfChild() 方法找到相对于父级的索引
                index = parent.indexOfChild(current_item)

            # 在路径中记录当前层的索引
            path.insert(0, index)
            current_item = parent

        return path
