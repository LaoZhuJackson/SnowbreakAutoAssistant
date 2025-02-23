import win32concon
import win32gui
from PIL import Image

from app.common.utils import is_fullscreen
from app.modules.base_task.base_task import BaseTask
from app.modules.fishing.fishing import FishingModule
from app.modules.water_bomb.water_bomb import WaterBombModule
from app.view.subtask import SubTask


# WaterBombModule().run()
# print(is_fullscreen(658872))

# hwnd = 396808
# win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)

# FishingModule().run()
# FishingModule().get_press_key()

class test(BaseTask):
    def __init__(self):
        super().__init__()

    def format_and_replace(self, data):
        results = []
        # 遍历所有文本框
        num_boxes = len(data['text'])
        for i in range(num_boxes):
            text = data['text'][i]
            conf = int(data['conf'][i])

            if text.strip() and conf > 0:  # 只处理有文本且置信度大于0的结果
                # 提取坐标
                left = data['left'][i]
                top = data['top'][i]
                width = data['width'][i]
                height = data['height'][i]

                # 坐标对角点
                bottom_right = [left + width, top + height]

                # 按照要求的格式组织数据
                result = [text, conf / 100.0, [[left, top], bottom_right]]
                results.append(result)
        return results

    def run(self):
        pytesseract.pytesseract.tesseract_cmd = r'D:\software\tesseract-ocr\tesseract.exe'
        while True:
            self.auto.take_screenshot()
            image = Image.fromarray(self.auto.current_screenshot)
            data = pytesseract.image_to_data(image, lang='chi_sim', output_type=pytesseract.Output.DICT)
            print(self.format_and_replace(data))

    def stop_ocr(self):
        pass


if __name__ == '__main__':
    # t = test()
    # t.run()
    from ctypes import cdll

    # 手动加载 shm.dll
    try:
        cdll.LoadLibrary(
            'D:\\Learning\\compilingEnvironment\\miniconda\\envs\\saa_dev\\lib\\site-packages\\torch\\lib\\shm.dll')
        print("shm.dll loaded successfully.")
    except Exception as e:
        print(f"Failed to load shm.dll: {e}")
