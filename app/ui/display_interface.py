import os
import random

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QBrush
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
)
from qfluentwidgets import ScrollArea, FluentIcon

from app.common.setting import VERSION, REPO_URL, GITHUB_FEEDBACK_URL
from app.common.style_sheet import StyleSheet

from app.repackage.link_card import LinkCardView
from app.repackage.samplecardview import SampleCardView


class BannerWidget(QWidget):
    """Banner widget"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(350)

        self.vBoxLayout = QVBoxLayout(self)
        # 大标题
        self.galleryLabel = QLabel(
            f'尘白自动化助手 {VERSION}\nSnowbreak Auto Assistant', self
        )
        self.galleryLabel.setStyleSheet(
            "color: #ECF9F8;font-size: 30px; font-weight: 600;"
        )

        # 创建阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # 阴影模糊半径
        shadow.setColor(Qt.black)  # 阴影颜色
        shadow.setOffset(1.2, 1.2)  # 阴影偏移量

        # 将阴影效果应用于小部件
        self.galleryLabel.setGraphicsEffect(shadow)

        self.basedir = "app/resource/images/display"
        random_number = random.randint(1, 9)
        # banner_path = os.path.join(self.basedir, f"background_{random_number}.jpg")
        banner_path = os.path.join(self.basedir, f"background_1.jpg")
        self.banner = QPixmap(banner_path)
        # 超链接卡片
        self.linkCardView = LinkCardView(self)
        # 设置边界
        self.linkCardView.setContentsMargins(0, 0, 0, 36)
        self.galleryLabel.setObjectName("galleryLabel")
        # 纵向布局
        linkCardLayout = QHBoxLayout()
        linkCardLayout.addWidget(self.linkCardView)
        linkCardLayout.setAlignment(Qt.AlignBottom)
        # 设置横向布局使靠左上显示
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addLayout(linkCardLayout)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr("GitHub地址"),
            self.tr("你的星星\n就是我的动力|･ω･)"),
            REPO_URL,
        )
        self.linkCardView.addCard(
            FluentIcon.INFO,
            self.tr("提出建议"),
            self.tr("前往github\n在issue中提建议(´▽`)ﾉ "),
            GITHUB_FEEDBACK_URL,
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        # 提示指示 QPainter 在缩放像素图（pixmap）时应该使用平滑的像素变换 | 开启了抗锯齿
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        # 指示不使用任何笔进行绘制，通常用于当你只想填充形状而不绘制它们的边界时
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        # 表示使用交叉数法则，即从任意方向绘制一条线，与多边形相交的次数奇数时填充，偶数时不填充
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()
        # 计算图片的高度
        try:
            image_height = self.width() * self.banner.height() // self.banner.width()
            pixmap = self.banner.scaled(
                self.width(),
                image_height,
                aspectRatioMode=Qt.KeepAspectRatio,
                transformMode=Qt.SmoothTransformation,
            )
        except ZeroDivisionError as e:
            print(f"图片加载失败:{e}")
            # logging.error(f"图片加载失败:{e}")
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))


class DisplayInterface(ScrollArea):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.basedir = "app/resource/images/display"

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName("view")
        self.setObjectName("displayInterface")
        StyleSheet.DISPLAY_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """load samples"""

        quick_jump = SampleCardView(self.tr("快捷跳转"), self.view)
        # 跳转设置
        quick_jump.addSampleCard(
            icon=os.path.join(self.basedir, "setting.svg"),
            title="设置",
            content=self.tr("软件相关设置"),
            routeKey="settingInterface",
            index=0,
        )
        quick_jump.addSampleCard(
            icon=os.path.join(self.basedir, "play.svg"),
            title="功能界面",
            content=self.tr("简单设置后一键种草！"),
            routeKey="Home-Interface",
            index=0,
        )
        # 使用教程跳转
        quick_jump.addSampleCard(
            icon=os.path.join(self.basedir, "explain.svg"),
            title="使用教程",
            content=self.tr("查看教程快速使用"),
            routeKey="Help-Interface",
            index=0,
        )
        quick_jump.addSampleCard_URL(
            icon=os.path.join(self.basedir, "electronics.svg"),
            title="实现后台操作",
            content=self.tr("让电脑不再跟你抢键鼠"),
            url="https://www.bilibili.com/read/cv24286313/",
        )

        self.vBoxLayout.addWidget(quick_jump)
