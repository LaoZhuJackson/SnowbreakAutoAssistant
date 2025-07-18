# coding:utf-8
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect

from qfluentwidgets import IconWidget, TextWrap, FlowLayout, CardWidget, FluentIcon
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet


class SampleCard(CardWidget):
    """ Sample card """

    def __init__(self, icon, title, content, routeKey, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.routekey = routeKey

        # 图标效果
        self.iconWidget = IconWidget(icon, self)
        self.iconOpacityEffect = QGraphicsOpacityEffect(self)
        self.iconOpacityEffect.setOpacity(0.8)  # 设置初始半透明度为不透明
        self.iconWidget.setGraphicsEffect(self.iconOpacityEffect)

        # 标题文本效果
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.titleOpacityEffect = QGraphicsOpacityEffect(self)
        self.titleOpacityEffect.setOpacity(0.8)  # 设置初始半透明度
        self.titleLabel.setGraphicsEffect(self.titleOpacityEffect)

        # 内容文本效果
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)
        self.contentOpacityEffect = QGraphicsOpacityEffect(self)
        self.contentOpacityEffect.setOpacity(0.8)  # 设置初始半透明度
        self.contentLabel.setGraphicsEffect(self.contentOpacityEffect)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        # print("触发了mouseReleaseEvent")
        signalBus.switchToSampleCard.emit(self.routekey, self.index)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.iconOpacityEffect.setOpacity(1)
        self.titleOpacityEffect.setOpacity(1)
        self.contentOpacityEffect.setOpacity(1)
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手形

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.iconOpacityEffect.setOpacity(0.8)
        self.titleOpacityEffect.setOpacity(0.8)
        self.contentOpacityEffect.setOpacity(0.8)
        self.setCursor(Qt.ArrowCursor)  # 恢复鼠标指针的默认形状


class SampleCard_URL(CardWidget):
    """ Sample card """

    def __init__(self, icon, title, content, url, parent=None):
        super().__init__(parent=parent)
        self.url = QUrl(url)

        # 图标效果
        self.iconWidget = IconWidget(icon, self)
        self.iconOpacityEffect = QGraphicsOpacityEffect(self)
        self.iconOpacityEffect.setOpacity(0.8)  # 设置初始半透明度为不透明
        self.iconWidget.setGraphicsEffect(self.iconOpacityEffect)

        # 标题文本效果
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.titleOpacityEffect = QGraphicsOpacityEffect(self)
        self.titleOpacityEffect.setOpacity(0.8)  # 设置初始半透明度
        self.titleLabel.setGraphicsEffect(self.titleOpacityEffect)

        # 内容文本效果
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)
        self.contentOpacityEffect = QGraphicsOpacityEffect(self)
        self.contentOpacityEffect.setOpacity(0.8)  # 设置初始半透明度
        self.contentLabel.setGraphicsEffect(self.contentOpacityEffect)

        # 链接图标
        self.urlWidget = IconWidget(FluentIcon.LINK, self)
        self.urlWidget.setFixedSize(16, 16)
        self.urlOpacityEffect = QGraphicsOpacityEffect(self)
        self.urlOpacityEffect.setOpacity(0.8)  # 设置初始半透明度
        self.urlWidget.setGraphicsEffect(self.urlOpacityEffect)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addStretch(2)
        self.hBoxLayout.addWidget(self.urlWidget)
        self.hBoxLayout.addStretch(1)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        QDesktopServices.openUrl(self.url)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.iconOpacityEffect.setOpacity(1)
        self.titleOpacityEffect.setOpacity(1)
        self.contentOpacityEffect.setOpacity(1)
        self.urlOpacityEffect.setOpacity(1)
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手形

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.iconOpacityEffect.setOpacity(0.8)
        self.titleOpacityEffect.setOpacity(0.8)
        self.contentOpacityEffect.setOpacity(0.8)
        self.urlOpacityEffect.setOpacity(0.8)
        self.setCursor(Qt.ArrowCursor)  # 恢复鼠标指针的默认形状


class SampleCardView(QWidget):
    """ Sample card view """

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        self.titleLabel.setObjectName('viewTitleLabel')
        StyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(self, icon, title, content, routeKey, index):
        """ add sample card """
        card = SampleCard(icon, title, content, routeKey, index, self)
        self.flowLayout.addWidget(card)

    def addSampleCard_URL(self, icon, title, content, url):
        """ add sample card """
        card = SampleCard_URL(icon, title, content, url, self)
        self.flowLayout.addWidget(card)
