import traceback

import cv2

from app.common.config import config
from app.common.image_utils import ImageUtils
from app.common.utils import cpu_support_avx2
from app.modules.onnxocr.onnx_paddleocr import ONNXPaddleOcr


class OCR:
    def __init__(self, logger, replacements=None):
        # 使用 easyocr 创建 OCR 阅读器
        self.ocr = None
        self.logger = logger
        self.replacements = replacements

    def run(self, image, extract: list = None, is_log=False):
        self.instance_ocr()
        try:
            if isinstance(image, str):
                image = cv2.imread(image, cv2.IMREAD_UNCHANGED)  # 读取图像，保持原始通道
                if image.shape[2] == 4:  # 如果是RGBA图像
                    image = image[:, :, :3]  # 只保留RGB通道
            if extract:
                letter = extract[0]
                threshold = extract[1]
                image = ImageUtils.extract_letters(image, letter, threshold)
            # ImageUtils.show_ndarray(image)
            # 调用 easyocr 进行 OCR
            original_result = self.ocr.ocr(image)[0]
            if original_result:  # 检查是否识别到文字
                return self.format_and_replace(original_result, is_log)
            else:
                if is_log:
                    self.logger.debug(f"OCR未识别出任何文字")
                return None
        except Exception as e:
            self.logger.error(f"执行ocr出错：{e}")
            traceback.print_exc()
            return None

    def format_and_replace(self, result, is_log=False):
        """
        转换OCR结果格式，返回统一的数据格式并替换OCR结果中的错误字符串
        :param result: 原始OCR识别结果
        :param is_log: 是否打印日志
        :return: 格式化后的输出，形如 [['16 +', 0.93, [[10.0, 23.0], [75.0, 58.0]]], ...]
        """
        formatted_result = []

        # 遍历每个识别框
        for item in result:
            text = item[1][0]  # OCR 提取的文本
            conf = item[1][1]  # 识别置信度
            box = item[0]  # 识别框的坐标

            # 获取坐标
            left = box[0][0]
            top = box[0][1]
            right = box[2][0]
            bottom = box[2][1]

            # 进行错误文本替换
            for old_text, new_text in self.replacements['direct'].items():
                text = text.replace(old_text, new_text)

            # 条件替换：只有当 new_str 不出现在 item["text"] 中时，才进行替换
            for old_text, new_text in self.replacements['conditional'].items():
                if new_text not in text:
                    text = text.replace(old_text, new_text)

            # 格式化输出: [文本, 置信度, 左上和右下坐标]
            formatted_result.append([text, round(conf, 2), [[left, top], [right, bottom]]])

        if is_log:
            self.log_result(formatted_result)
        return formatted_result

    def log_result(self, results):
        log_content = []
        for result in results:
            log_content.append(f'{result[0]}:{result[1]}')
        self.logger.debug(f"OCR识别结果: {log_content}")

    def instance_ocr(self):
        """实例化OCR，若ocr实例未创建，则创建之"""
        if self.ocr is None:
            if config.cpu_support_avx2.value is None:
                cpu_support_avx2()
            try:
                self.logger.debug("开始初始化OCR...")
                #
                if config.cpu_support_avx2.value or config.ocr_use_gpu.value:
                    self.ocr = ONNXPaddleOcr(use_angle_cls=True, use_gpu=config.ocr_use_gpu.value)
                    self.logger.info(f"初始化OCR完成")
                else:
                    self.logger.error(f"初始化OCR失败：此cpu不支持AVX2指令集")
            except Exception as e:
                self.logger.error(f"初始化OCR失败：{e}")
                raise Exception("初始化OCR失败")

    def stop_ocr(self):
        pass
