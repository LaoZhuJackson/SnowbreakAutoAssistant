import json

from PyQt5.QtWidgets import QFrame, QTableWidgetItem

from app.common.style_sheet import StyleSheet
from app.ui.ocr_replacement_table import Ui_ocrtable


class OcrReplacementTable(QFrame, Ui_ocrtable):
    def __init__(self, text: str, parent=None):
        super().__init__()

        self.setupUi(self)
        self.setObjectName(text.replace(' ', '-'))
        self.parent = parent

        self._initWidget()
        self._connect_to_slot()

    def _initWidget(self):
        self.BodyLabel_tips.setText(
            "### 提示\n* 功能未完成！！！别用！！！\n* 双击单元格可修改\n* 新增和删除都说的是最后一行\n* 修改完记得保存")

        self.TableWidget_ocr_table.setBorderVisible(True)
        self.TableWidget_ocr_table.setBorderRadius(8)
        self.TableWidget_ocr_table.verticalHeader().hide()
        self.TableWidget_ocr_table.setHorizontalHeaderLabels(['类型', '替换前', '替换后'])

        self.load_table()
        StyleSheet.OCR_TABLE.apply(self)

    def _connect_to_slot(self):
        pass

    def load_table(self):
        with open("AppData/ocr_replacements.json", 'r', encoding='utf-8') as file:
            replacements = json.load(file)
            direct_dic = replacements['direct']
            conditional_dic = replacements['conditional']
            total_rows = len(direct_dic) + len(conditional_dic)
            self.TableWidget_ocr_table.setRowCount(total_rows)

            row_index = 0
            for key, value in direct_dic.items():
                self.TableWidget_ocr_table.setItem(row_index, 0, QTableWidgetItem('直接替换'))
                self.TableWidget_ocr_table.setItem(row_index, 1, QTableWidgetItem(key))
                self.TableWidget_ocr_table.setItem(row_index, 2, QTableWidgetItem(value))
                row_index += 1
            for key, value in conditional_dic.items():
                self.TableWidget_ocr_table.setItem(row_index, 0, QTableWidgetItem('条件替换'))
                self.TableWidget_ocr_table.setItem(row_index, 1, QTableWidgetItem(key))
                self.TableWidget_ocr_table.setItem(row_index, 2, QTableWidgetItem(value))
                row_index += 1

        self.TableWidget_ocr_table.resizeColumnsToContents()
        # self.resize(self.parent.width(), self.parent.height())
