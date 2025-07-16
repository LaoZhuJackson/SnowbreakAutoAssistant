import time

from app.common.config import config
from app.modules.automation.timer import Timer
from app.modules.base_task.base_task import BaseTask


class ActionModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.is_log = False
        self.times = 1

    def run(self):
        self.is_log = config.isLog.value
        self.times = config.SpinBox_action_times.value
        print(self.times)
        print(type(self.times))

        self.enter_train()
        for i in range(self.times):
            self.fight()
        self.auto.back_to_home()

    def fight(self):
        timeout = Timer(40).start()
        is_enter = False
        is_move = False
        is_finish = False

        while True:
            self.auto.take_screenshot()
            if not is_finish:
                if not is_enter:
                    if self.auto.click_element(
                        "开始",
                        "text",
                        crop=(2303 / 2560, 1300 / 1440, 2492 / 2560, 1383 / 1440),
                        is_log=self.is_log,
                    ):
                        is_enter = True
                        time.sleep(3)
                        continue
                    if self.auto.click_element(
                        "准备",
                        "text",
                        crop=(2303 / 2560, 1309 / 1440, 2492 / 2560, 1383 / 1440),
                        is_log=self.is_log,
                    ):
                        continue
                    if self.auto.click_element(
                        "支援技",
                        "text",
                        crop=(161 / 2560, 609 / 1440, 347 / 2560, 700 / 1440),
                        is_log=self.is_log,
                    ):
                        time.sleep(0.5)
                        continue
                else:
                    if not is_move:
                        if self.auto.find_element(
                            "黄色区域",
                            "text",
                            crop=(1111 / 2560, 311 / 1440, 1456 / 2560, 362 / 1440),
                            is_log=self.is_log,
                        ):
                            self.auto.key_down("w")
                            is_move = True
                            continue
                    else:
                        if config.ComboBox_run.value == 0:
                            self.auto.press_key("shift")
                            time.sleep(6)
                        else:
                            for i in range(5):
                                self.auto.press_key("shift", press_time=1)
                                time.sleep(0.3)
                        self.auto.key_up("w")
                        is_finish = True
                        continue
            else:
                if self.auto.click_element(
                    "退出",
                    "text",
                    crop=(903 / 1920, 938 / 1080, 1017 / 1920, 1004 / 1080),
                    is_log=self.is_log,
                ):
                    break
                if self.auto.find_element(
                    "设置",
                    "text",
                    crop=(1211 / 2560, 778 / 1440, 1340 / 2560, 842 / 1440),
                    is_log=self.is_log,
                ):
                    self.auto.press_key("esc")
                    continue
                time.sleep(2)

            if timeout.reached():
                self.logger.error("执行常规行动超时")
                break

    def enter_train(self):
        timeout = Timer(20).start()

        while True:
            self.auto.take_screenshot()

            if self.auto.click_element(
                "支援技",
                "text",
                crop=(161 / 2560, 609 / 1440, 347 / 2560, 700 / 1440),
                is_log=self.is_log,
            ):
                break
            if self.auto.find_element(
                "行动",
                "text",
                crop=(480 / 2560, 1340 / 1440, 625 / 2560, 1400 / 1440),
                is_log=self.is_log,
            ):
                if not self.auto.click_element(
                    "实战训练",
                    "text",
                    crop=(2168 / 2560, 1060 / 1440, 2400 / 2560, 1132 / 1440),
                    is_log=self.is_log,
                ):
                    self.auto.mouse_scroll(
                        int(619 / self.auto.scale_x),
                        int(866 / self.auto.scale_y),
                        -8500,
                    )
                else:
                    break
            else:
                if self.auto.click_element(
                    "战斗",
                    "text",
                    crop=(1536 / 1920, 470 / 1080, 1632 / 1920, 516 / 1080),
                    is_log=self.is_log,
                ):
                    time.sleep(1)
                    continue
                if self.auto.click_element(
                    "行动",
                    "text",
                    crop=(2085 / 2560, 716 / 1440, 2542 / 2560, 853 / 1440),
                    is_log=self.is_log,
                ):
                    time.sleep(0.5)
                    continue

            if timeout.reached():
                self.logger.error("进入常规行动")
                break
