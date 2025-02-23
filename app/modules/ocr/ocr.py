import logging

import cv2
import gc
import time

# import pytesseract
from PIL import Image
# from paddleocr import PaddleOCR

from app.common.image_utils import ImageUtils
from app.common.logger import logger

# class OCR:
#     def __init__(self, logger, replacements=None):
#         self.ocr = None
#         self.logger = logger
#         self.replacements = replacements
#         self.time = time.time()
#
#     def run(self, image, extract: list = None):
#         """
#         进行ocr识别并返回格式化后的识别结果
#         :param extract: 是否提取文字，[(文字rgb颜色),threshold数值]
#         :param image: 支持图像路径字符串，以及np.array类型(height, width, channels)
#         :return:
#         """
#         self.instance_ocr()
#         try:
#             if isinstance(image, str):
#                 image = cv2.imread(image, cv2.IMREAD_UNCHANGED)  # 读取图像，保持原始通道
#                 if image.shape[2] == 4:  # 如果是RGBA图像
#                     image = image[:, :, :3]  # 只保留RGB通道
#             if extract:
#                 # 需要提取文字
#                 letter = extract[0]
#                 threshold = extract[1]
#                 image = ImageUtils.extract_letters(image, letter, threshold)
#                 # ImageUtils.show_ndarray(image)
#             original_result = self.ocr(image)
#
#             if time.time() - self.time >= 10:
#                 self.stop_ocr()
#                 self.time = time.time()
#
#             if original_result:
#                 return self.format_and_replace(original_result)
#             else:
#                 return None
#         except Exception as e:
#             logger.error(e)
#             return None
#
# def format_and_replace(self, result):
#     """
#     转换OCR结果格式，返回统一的数据格式并替换OCR结果中的错误字符串
#     :param result: 原始ocr识别结果
#     :return:输出示例
#     ['16 +', 0.93, [[10.0, 23.0], [75.0, 58.0]]]
#     ['CADPA', 0.99, [[12.0, 70.0], [69.0, 87.0]]]
#     ['适龄提示', 1.0, [[7.0, 90.0], [75.0, 106.0]]]
#     """
#     formatted_result = []
#     # print(f"original result: {result}")
#
#     # 获取坐标和文本+置信度
#     boxes = result[0]  # OCR 输出的坐标
#     text_confidences = result[1]  # OCR 输出的文本和置信度
#
#     for i in range(len(boxes)):
#         # 获取当前框的坐标
#         box = boxes[i]
#         # 左上角坐标
#         top_left = box[0]
#         # 右下角坐标
#         bottom_right = box[2]
#
#         # 获取当前文本和置信度
#         text, confidence = text_confidences[i]
#
#         # 进行错误文本替换
#         # 直接替换
#         for old_text, new_text in self.replacements['direct'].items():
#             text = text.replace(old_text, new_text)
#
#         # 条件替换：只有当 new_str 不出现在 item["text"] 中时，才进行替换
#         for old_text, new_text in self.replacements['conditional'].items():
#             if new_text not in text:
#                 text = text.replace(old_text, new_text)
#         # 格式化输出: [文本, 置信度, 左上和右下坐标]
#         formatted_result.append([text, round(confidence, 2), [top_left.tolist(), bottom_right.tolist()]])
#
#     # self.log_result(formatted_result)
#     return formatted_result
#
#     def log_result(self, results):
#         log_content = []
#         for result in results:
#             log_content.append(f'{result[0]}:{result[1]}')
#         self.logger.debug(f"OCR识别结果: {log_content}")
#
#     def instance_ocr(self):
#         """实例化OCR，若ocr实例未创建，则创建之"""
#         if self.ocr is None:
#             try:
#                 # 自动检测是否可用NVIDIA GPU
#                 # FIXME ocr用上高贵的gpu use_gpu = paddle.is_compiled_with_cuda() and paddle.device.get_device().startswith("gpu")
#                 use_gpu = False
#                 # print(f"{use_gpu=}")
#                 self.logger.debug("开始初始化OCR...")
#                 self.ocr = PaddleOCR(
#                     det_model_dir='app/resource/paddleocr/whl/det/ch',
#                     rec_model_dir='app/resource/paddleocr/whl/rec/ch',
#                     cls_model_dir='app/resource/paddleocr/whl/cls',
#                     use_gpu=use_gpu,
#                     use_angle_cls=False,
#                     warmup=False,
#                     max_batch_size=1,
#                     rec_batch_num=1,
#                     benchmark=False,
#                     lang='ch'
#                 )
#             except Exception as e:
#                 self.logger.error(f"初始化OCR失败：{e}")
#                 raise Exception("初始化OCR失败")
#
#     def stop_ocr(self):
#         self.ocr = None
#         gc.collect()

# class OCR:
#     pytesseract.pytesseract.tesseract_cmd = r'D:\software\tesseract-ocr\tesseract.exe'
#     logging.getLogger('Tesseract').setLevel(logging.CRITICAL)
#     def __init__(self, logger, replacements=None):
#         self.ocr = pytesseract.image_to_data
#         self.logger = logger
#         self.replacements = replacements
#
#     def run(self,image, extract: list = None):
#         try:
#             if isinstance(image, str):
#                 image = cv2.imread(image, cv2.IMREAD_UNCHANGED)  # 读取图像，保持原始通道
#                 if image.shape[2] == 4:  # 如果是RGBA图像
#                     image = image[:, :, :3]  # 只保留RGB通道
#             if extract:
#                 letter = extract[0]
#                 threshold = extract[1]
#                 image = ImageUtils.extract_letters(image, letter, threshold)
#             # 确保颜色顺序从 BGR 转为 RGB
#             image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#             image.show()
#             original_result = self.ocr(image,lang='chi_sim', output_type=pytesseract.Output.DICT)
#             if any(text.strip() for text in original_result['text']):  # 检查 'text' 列表中是否有非空字符串:
#                 return self.format_and_replace(original_result)
#             else:
#                 return None
#         except Exception as e:
#             logger.error(e)
#             return None
#
#     def format_and_replace(self, result):
#         """
#         转换OCR结果格式，返回统一的数据格式并替换OCR结果中的错误字符串
#         :param result: 原始ocr识别结果
#         :return: 格式化后的输出，形如 [['16 +', 0.93, [[10.0, 23.0], [75.0, 58.0]]], ...]
#         """
#         formatted_result = []
#
#         # 遍历每一个识别框
#         for i in range(len(result['text'])):
#             text = result['text'][i]
#             conf = int(result['conf'][i]) if result['conf'][i] != 'nan' else 0
#
#             if text.strip():  # 忽略空文本
#                 # 获取坐标
#                 left = result['left'][i]
#                 top = result['top'][i]
#                 width = result['width'][i]
#                 height = result['height'][i]
#
#                 # 右下角坐标
#                 bottom_right = [left + width, top + height]
#
#                 # 进行错误文本替换
#                 for old_text, new_text in self.replacements['direct'].items():
#                     text = text.replace(old_text, new_text)
#
#                 # 条件替换：只有当 new_str 不出现在 item["text"] 中时，才进行替换
#                 for old_text, new_text in self.replacements['conditional'].items():
#                     if new_text not in text:
#                         text = text.replace(old_text, new_text)
#
#                 # 格式化输出: [文本, 置信度, 左上和右下坐标]
#                 formatted_result.append([text, round(conf / 100.0, 2), [[left, top], bottom_right]])
#
#         self.log_result(formatted_result)
#         return formatted_result
#
#     def log_result(self, results):
#         log_content = []
#         for result in results:
#             log_content.append(f'{result[0]}:{result[1]}')
#         self.logger.debug(f"OCR识别结果: {log_content}")
#
#     def stop_ocr(self):
#         pass
import easyocr

class OCR:
    def __init__(self, logger, replacements=None):
        # 使用 easyocr 创建 OCR 阅读器
        self.ocr = None
        self.logger = logger
        self.replacements = replacements

    def run(self, image, extract: list = None, is_log=True):
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

            # 调用 easyocr 进行 OCR
            original_result = self.ocr.readtext(image)

            if original_result:  # 检查是否识别到文字
                return self.format_and_replace(original_result, is_log)
            else:
                return None
        except Exception as e:
            self.logger.error(e)
            return None

    def format_and_replace(self, result, is_log=True):
        """
        转换OCR结果格式，返回统一的数据格式并替换OCR结果中的错误字符串
        :param result: 原始OCR识别结果
        :param is_log: 是否打印日志
        :return: 格式化后的输出，形如 [['16 +', 0.93, [[10.0, 23.0], [75.0, 58.0]]], ...]
        """
        formatted_result = []

        # 遍历每个识别框
        for item in result:
            text = item[1]  # OCR 提取的文本
            conf = item[2]  # 识别置信度
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
            try:
                self.logger.debug("开始初始化OCR...")
                self.ocr = easyocr.Reader(['ch_sim'])  # 'ch_sim' 用于简体中文
            except Exception as e:
                self.logger.error(f"初始化OCR失败：{e}")
                raise Exception("初始化OCR失败")

    def stop_ocr(self):
        pass
