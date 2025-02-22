import cv2
import gc
import time
from paddleocr import PaddleOCR

from app.common.image_utils import ImageUtils
from app.common.logger import logger


class OCR:
    def __init__(self, logger, replacements=None):
        self.ocr = None
        self.logger = logger
        self.replacements = replacements
        self.time = time.time()

    def run(self, image, extract: list = None):
        """
        进行ocr识别并返回格式化后的识别结果
        :param extract: 是否提取文字，[(文字rgb颜色),threshold数值]
        :param image: 支持图像路径字符串，以及np.array类型(height, width, channels)
        :return:
        """
        self.instance_ocr()
        try:
            if isinstance(image, str):
                image = cv2.imread(image, cv2.IMREAD_UNCHANGED)  # 读取图像，保持原始通道
                if image.shape[2] == 4:  # 如果是RGBA图像
                    image = image[:, :, :3]  # 只保留RGB通道
            if extract:
                # 需要提取文字
                letter = extract[0]
                threshold = extract[1]
                image = ImageUtils.extract_letters(image, letter, threshold)
                # ImageUtils.show_ndarray(image)
            original_result = self.ocr(image)

            if time.time() - self.time >= 30:
                self.stop_ocr()
                self.time = time.time()

            if original_result:
                return self.format_and_replace(original_result)
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None

    def format_and_replace(self, result):
        """
        转换OCR结果格式，返回统一的数据格式并替换OCR结果中的错误字符串
        :param result: 原始ocr识别结果
        :return:输出示例
        ['16 +', 0.93, [[10.0, 23.0], [75.0, 58.0]]]
        ['CADPA', 0.99, [[12.0, 70.0], [69.0, 87.0]]]
        ['适龄提示', 1.0, [[7.0, 90.0], [75.0, 106.0]]]
        """
        formatted_result = []
        # print(f"original result: {result}")

        # 获取坐标和文本+置信度
        boxes = result[0]  # OCR 输出的坐标
        text_confidences = result[1]  # OCR 输出的文本和置信度

        for i in range(len(boxes)):
            # 获取当前框的坐标
            box = boxes[i]
            # 左上角坐标
            top_left = box[0]
            # 右下角坐标
            bottom_right = box[2]

            # 获取当前文本和置信度
            text, confidence = text_confidences[i]

            # 进行错误文本替换
            # 直接替换
            for old_text, new_text in self.replacements['direct'].items():
                text = text.replace(old_text, new_text)

            # 条件替换：只有当 new_str 不出现在 item["text"] 中时，才进行替换
            for old_text, new_text in self.replacements['conditional'].items():
                if new_text not in text:
                    text = text.replace(old_text, new_text)
            # 格式化输出: [文本, 置信度, 左上和右下坐标]
            formatted_result.append([text, round(confidence, 2), [top_left.tolist(), bottom_right.tolist()]])

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
                # 自动检测是否可用NVIDIA GPU
                # FIXME ocr用上高贵的gpu use_gpu = paddle.is_compiled_with_cuda() and paddle.device.get_device().startswith("gpu")
                use_gpu = False
                # print(f"{use_gpu=}")
                self.logger.debug("开始初始化OCR...")
                self.ocr = PaddleOCR(
                    det_model_dir='app/resource/paddleocr/whl/det/ch',
                    rec_model_dir='app/resource/paddleocr/whl/rec/ch',
                    cls_model_dir='app/resource/paddleocr/whl/cls',
                    use_gpu=use_gpu,
                    use_angle_cls=False,
                    warmup=False,
                    max_batch_size=1,
                    rec_batch_num=1,
                    benchmark=False,
                    lang='ch'
                )
            except Exception as e:
                self.logger.error(f"初始化OCR失败：{e}")
                raise Exception("初始化OCR失败")

    def exit_ocr(self):
        """退出OCR实例，清理资源"""
        self.logger.info("关闭ocr")
        if self.ocr is not None:
            del self.ocr

    def stop_ocr(self):
        self.ocr = None
        gc.collect()
