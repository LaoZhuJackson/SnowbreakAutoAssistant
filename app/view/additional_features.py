from PyQt5.QtWidgets import QFrame, QWidget

from app.ui.additional_features_interface import Ui_additional_features


class Additional(QFrame, Ui_additional_features):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.setting_name_list = ['商店', '体力', '奖励']

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self._initWidget()
        self._connect_to_slot()
        self._redirectOutput()

    def _initWidget(self):
        # 正向链接
        self.SegmentedWidget.addItem(self.page_fishing.objectName(), '自动钓鱼',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_fishing))
        self.SegmentedWidget.addItem(self.page_2.objectName(), '待开发',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.SegmentedWidget.addItem(self.page_3.objectName(), '待开发',
                                     onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.SegmentedWidget.setCurrentItem(self.page_fishing.objectName())

        self.stackedWidget.setCurrentIndex(0)

        pass

    def _connect_to_slot(self):
        # 反向链接
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    def _redirectOutput(self):
        pass

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())
