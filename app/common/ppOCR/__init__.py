import os
from typing import Optional
import cpufeature
import json

from app.common.config import config
from app.common.fastest_mirror import FastestMirror
from app.common.logger import logger
from app.common.ppOCR.ocr import OCR
from app.common.update_handler import UpdateHandler


class OCRInstaller:
    """
    OCR 安装器，负责根据 CPU 特性选择合适的 OCR 工具，并处理安装过程。
    """

    def __init__(self):
        self.ocr_name, self.ocr_path = self._determine_ocr()

    def _cpu_support_avx2(self):
        """
        判断 CPU 是否支持 AVX2 指令集。
        """
        return cpufeature.CPUFeature["AVX2"]

    def _determine_ocr(self):
        """
        根据 CPU 是否支持 AVX2 指令集来决定使用的 OCR 工具。
        """
        if config.cpu_support_avx2.value is None:
            is_support = self._cpu_support_avx2()
            config.set(config.cpu_support_avx2, is_support)
        if config.cpu_support_avx2.value:
            ocr_name = "PaddleOCR-json"
            ocr_path = "./app/common/ppOCR/PaddleOCR-json_v1.4.1_windows_x64/PaddleOCR-json.exe"
            # print(f"CPU 支持 AVX2 指令集，使用 {ocr_name}")
        else:
            ocr_name = "RapidOCR-json"
            ocr_path = "./app/common/ppOCR/RapidOCR-json_v0.2.0/RapidOCR-json.exe"
            # print(f"CPU 不支持 AVX2 指令集，使用 {ocr_name}")
        return ocr_name, ocr_path

    def install_ocr(self):
        """
        安装选定的 OCR 工具。
        """

        base_url = "https://github.com/{name}/releases/download/{version}/{filename}"
        if self.ocr_name == "PaddleOCR-json":
            url = FastestMirror.get_github_mirror(base_url.format(name="hiroi-sora/PaddleOCR-json", version="v1.4.1",
                                                                  filename="PaddleOCR-json_v1.4.1_windows_x64.7z"))
            version = "PaddleOCR-json_v1.4.1"
        else:
            url = FastestMirror.get_github_mirror(
                base_url.format(name="hiroi-sora/RapidOCR-json", version="v0.2.0", filename="RapidOCR-json_v0.2.0.7z"))
            version = "RapidOCR-json_v0.2.0"

        update_handler = UpdateHandler(url, os.path.dirname(self.ocr_path), version, config_item=config.is_ocr)
        update_handler.run()

    def check_ocr(self):
        """
        检查 OCR 工具是否已安装，如未安装则进行安装。
        """
        if not os.path.exists(self.ocr_path):
            return False
        else:
            return True


# 初始化 OCR 安装器
ocr_installer = OCRInstaller()
# 读取 OCR 替换配置
with open("./AppData/ocr_replacements.json", 'r', encoding='utf-8') as file:
    replacements = json.load(file)
# 初始化 OCR 对象
ocr = OCR(ocr_installer.ocr_path, logger, replacements)
