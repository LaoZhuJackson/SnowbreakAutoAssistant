import time

from app.modules.ocr import ocr

image_path = '../app/resource/images/start_game/age.png'
image_path_no_text = '../app/resource/images/logo.png'
image_path_wrong_text = './wrong_text.png'


def benchmark(ocr_func, img, runs=100):
    # 预热
    for _ in range(10):
        ocr_func(img)

    # 正式测试
    start = time.time()
    for _ in range(runs):
        ocr_func(img)
    return (time.time() - start) / runs


if __name__ == '__main__':
    # import paddle
    # try:
    #     print(paddle.utils.run_check())
    # except Exception as e:
    #     print(e)
    result = ocr.run(image_path, [(34, 34, 34), 128])
    print(f"{result=}")

    # result = ([array([[10., 23.],
    #                   [75., 23.],
    #                   [75., 58.],
    #                   [10., 58.]], dtype=float32), array([[12., 70.],
    #                                                       [69., 70.],
    #                                                       [69., 87.],
    #                                                       [12., 87.]], dtype=float32), array([[7., 90.],
    #                                                                                           [76., 93.],
    #                                                                                           [75., 106.],
    #                                                                                           [6., 106.]],
    #                                                                                          dtype=float32)],
    #           [('16 +', 0.9349133968353271), ('CADPA', 0.9933081865310669), ('适龄提示', 0.9997501373291016)],
    #           {'det': 0.1181640625, 'rec': 0.18414640426635742, 'cls': 0, 'all': 0.30330681800842285})

    # print(f"单次识别耗时：{benchmark(ocr.run, image_path):.2f}秒")
