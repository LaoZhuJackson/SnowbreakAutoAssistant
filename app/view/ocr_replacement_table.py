import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QTableWidgetItem
from qfluentwidgets import InfoBar, InfoBarPosition

from app.common.style_sheet import StyleSheet
from app.ui.ocr_replacement_table import Ui_ocrtable


class OcrReplacementTable(QFrame, Ui_ocrtable):
    def __init__(self, text: str, parent=None):
        super().__init__()

        self.setupUi(self)
        self.setObjectName(text.replace(" ", "-"))
        self.parent = parent

        self.old_type = None
        self.old_key = None
        self.old_value = None

        self._initWidget()
        self._connect_to_slot()

    def _initWidget(self):
        self.BodyLabel_tips.setText(
            "### 提示\n* 双击单元格可修改\n* 填好上面对应的内容后点击“新增”按钮可以添加新的替换规则\n* 错误文本：ocr识别出来的错误内容，如果看不到去设置那开启显示ocr识别结果。正确文本：游戏中对应的正确文字\n* 删除需要先选中你需要删除的行，然后再点删除按钮"
        )

        power_usage_items = ["直接替换", "条件替换"]
        self.ComboBox_type.addItems(power_usage_items)
        self.LineEdit_before.setPlaceholderText("错误文本")
        self.LineEdit_after.setPlaceholderText("正确文本")

        # 新增路径属性
        self.json_path = self.get_json_path()

        self.TableWidget_ocr_table.setBorderVisible(True)
        self.TableWidget_ocr_table.setBorderRadius(8)
        self.TableWidget_ocr_table.verticalHeader().hide()
        self.TableWidget_ocr_table.setHorizontalHeaderLabels(
            ["类型", "替换前", "替换后"]
        )

        self.load_table()
        StyleSheet.OCR_TABLE.apply(self)

    def _connect_to_slot(self):
        self.PrimaryPushButton_add.clicked.connect(self.on_add_button_click)
        self.PushButton_delete.clicked.connect(self.delete_row)
        self.TableWidget_ocr_table.cellChanged.connect(self.change_row)
        self.TableWidget_ocr_table.cellDoubleClicked.connect(self.enter_cell)

    def get_json_path(self):
        """获取JSON文件的绝对路径"""
        # 获取可执行文件所在目录
        base_dir = os.path.dirname(sys.executable)
        # 组合完整路径
        json_path = os.path.join(base_dir, "AppData", "ocr_replacements.json")

        # 如果AppData目录不存在则创建
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        # print(json_path)
        return json_path

    def enter_cell(self, row, col):
        self.old_type = (
            "direct"
            if self.TableWidget_ocr_table.item(row, 0).text() == "直接替换"
            else "conditional"
        )
        self.old_key = self.TableWidget_ocr_table.item(row, 1).text()
        self.old_value = self.TableWidget_ocr_table.item(row, 2).text()

    def change_row(self, row, col):
        # 临时断开信号
        # self.TableWidget_ocr_table.cellChanged.disconnect(self.change_row)
        self.TableWidget_ocr_table.blockSignals(True)
        try:
            item = self.TableWidget_ocr_table.item(row, col)
            if not item:
                return
            if not (self.old_type and self.old_key and self.old_value):
                return
            data = self.load_json()
            if col == 0:
                print(item.text())
                if item.text() != "直接替换" and item.text() != "条件替换":
                    InfoBar.error(
                        title="类型错误",
                        content="类型值支持“直接替换”或“条件替换”",
                        orient=Qt.Horizontal,
                        isClosable=True,  # disable close button
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self,
                    )
                    self.load_table()
                    return
                key_type = "direct" if item.text() == "直接替换" else "conditional"
                if key_type == self.old_type:
                    return
                if key_type == "direct":
                    data[key_type][self.old_key] = self.old_value
                    del data["conditional"][self.old_key]
                else:
                    data[key_type][self.old_key] = self.old_value
                    del data["direct"][self.old_key]
            elif col == 1:
                if item.text() == self.old_key:
                    return
                data[self.old_type][item.text()] = self.old_value
                del data[self.old_type][self.old_key]
            else:
                if item.text() == self.old_value:
                    return
                data[self.old_type][self.old_key] = item.text()
            self.save_data(data)
            self.load_table()
            InfoBar.info(
                title="修改成功",
                content="已成功修改对应的替换规则",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self,
            )
        finally:
            # 重新连接信号
            # self.TableWidget_ocr_table.cellChanged.connect(self.change_row)
            self.TableWidget_ocr_table.blockSignals(True)

    def on_add_button_click(self):
        try:
            # 临时断开信号
            # self.TableWidget_ocr_table.cellChanged.disconnect(self.change_row)
            self.TableWidget_ocr_table.blockSignals(True)
            replace_type = (
                "direct" if self.ComboBox_type.currentIndex() == 0 else "conditional"
            )
            original_text = self.LineEdit_before.text()
            replacement_text = self.LineEdit_after.text()

            if original_text == "" or replacement_text == "":
                InfoBar.error(
                    title="替换文本不能为空",
                    content="输入需要替换的前后文本",
                    orient=Qt.Horizontal,
                    isClosable=True,  # disable close button
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self,
                )
                return

            # 读取现有 JSON 文件
            data = self.load_json()
            # 添加新规则
            data[replace_type][original_text] = replacement_text
            # 写回 JSON 文件
            self.save_data(data)
            self.load_table()
            InfoBar.info(
                title="添加成功",
                content="已成功添加新的替换规则",
                orient=Qt.Horizontal,
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self,
            )
        except Exception as e:
            print(e)
        finally:
            # 重新连接信号
            # self.TableWidget_ocr_table.cellChanged.connect(self.change_row)
            self.TableWidget_ocr_table.blockSignals(False)

    def load_json(self):
        # 确保文件存在
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump({"direct": {}, "conditional": {}}, f, indent=4)

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {str(e)}, path:{self.json_path}")
            return {"direct": {}, "conditional": {}}

    def save_data(self, data):
        try:
            # 检查文件是否可写
            if os.path.exists(self.json_path):
                if not os.access(self.json_path, os.W_OK):
                    print("错误：文件不可写！")
                    raise PermissionError("文件不可写")
            print("文件可写！")
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving JSON: {str(e)}, path:{self.json_path}")
            InfoBar.error(
                title="保存失败",
                content=f"无法写入配置文件：{str(e)}",
                isClosable=True,  # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self,
            )

    def delete_row(self):
        try:
            # 临时断开信号
            # self.TableWidget_ocr_table.cellChanged.disconnect(self.change_row)

            # 阻断信号传送
            self.TableWidget_ocr_table.blockSignals(True)
            select_row = self.TableWidget_ocr_table.currentRow()
            if select_row >= 0:
                key_type = (
                    "direct"
                    if self.TableWidget_ocr_table.item(select_row, 0).text()
                    == "直接替换"
                    else "conditional"
                )
                key_to_delete = self.TableWidget_ocr_table.item(select_row, 1).text()
                data = self.load_json()
                if key_type not in data:
                    InfoBar.error(
                        title="删除失败",
                        content=f"{key_type} 不在 JSON 中！",
                        orient=Qt.Horizontal,
                        isClosable=True,  # disable close button
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self,
                    )
                    return
                if key_to_delete not in data[key_type]:
                    InfoBar.error(
                        title="删除失败",
                        content=f"键 '{key_to_delete}' 不存在于 {key_type} 中！",
                        orient=Qt.Horizontal,
                        isClosable=True,  # disable close button
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self,
                    )
                    return
                del data[key_type][key_to_delete]
                self.save_data(data)
                self.load_table()
                InfoBar.info(
                    title="删除成功",
                    content=f"已删除对应行",
                    orient=Qt.Horizontal,
                    isClosable=True,  # disable close button
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self,
                )
            else:
                InfoBar.error(
                    title="未选中需要删除的行",
                    content="选中需要删除的行之后再点击删除",
                    orient=Qt.Horizontal,
                    isClosable=True,  # disable close button
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=2000,
                    parent=self,
                )
        except Exception as e:
            print(e)
        finally:
            # 重新连接信号
            # self.TableWidget_ocr_table.cellChanged.connect(self.change_row)
            self.TableWidget_ocr_table.blockSignals(False)

    def load_table(self):
        replacements = self.load_json()
        direct_dic = replacements["direct"]
        conditional_dic = replacements["conditional"]
        total_rows = len(direct_dic) + len(conditional_dic)
        self.TableWidget_ocr_table.setRowCount(total_rows)

        row_index = 0
        for key, value in direct_dic.items():
            self.TableWidget_ocr_table.setItem(
                row_index, 0, QTableWidgetItem("直接替换")
            )
            self.TableWidget_ocr_table.setItem(row_index, 1, QTableWidgetItem(key))
            self.TableWidget_ocr_table.setItem(row_index, 2, QTableWidgetItem(value))
            row_index += 1
        for key, value in conditional_dic.items():
            self.TableWidget_ocr_table.setItem(
                row_index, 0, QTableWidgetItem("条件替换")
            )
            self.TableWidget_ocr_table.setItem(row_index, 1, QTableWidgetItem(key))
            self.TableWidget_ocr_table.setItem(row_index, 2, QTableWidgetItem(value))
            row_index += 1

        self.TableWidget_ocr_table.resizeColumnsToContents()
        # self.resize(self.parent.width(), self.parent.height())
