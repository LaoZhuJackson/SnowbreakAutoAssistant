import time
from dataclasses import dataclass

import cv2
from app.common.config import config
from app.modules.automation.timer import Timer


@dataclass
class IslandProfile:
    name: str
    fixed_interval_sec: float
    patrol_refresh_interval_sec: float
    enter_wait_sec: float = 6


@dataclass
class _SyncState:
    key: str
    profile: IslandProfile
    mode: int  # 0 fixed, 1 patrol
    done: bool = False
    error: bool = False
    no_collect_streak: int = 0

    def period_sec(self) -> float:
        return float(self.profile.patrol_refresh_interval_sec if self.mode == 1 else self.profile.fixed_interval_sec)


class CapturePalsModule:
    """
    尘白抓帕鲁模块
    目标：保持功能与行为语义不变，但结构更清晰、稳定、易维护。
    """

    ENTER_WAIT_SEC = 6
    MAX_FAILED_F_ATTEMPTS = 10
    FAILED_F_SLEEP = 0.5
    PATROL_NO_COLLECT_MAX = 3
    FIXED_NO_COLLECT_MAX = 3

    _RETRY_PER_ACTION = 5
    _DEFAULT_TICK = 0.2

    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger

        self.is_log = False
        self.stop_requested = False

        # ===== collect =====
        self.collect_image = "app/resource/images/fishing/collect.png"
        self.collect_crop = (1506 / 1920, 684 / 1080, 1547 / 1920, 731 / 1080)
        self.collect_threshold = 0.65

        # ===== exit map =====
        self.btn_exit_map_image = "app/resource/images/capture_pals/exit_map.png"
        self.btn_exit_map_crop = (1838 / 1920, 968 / 1080, 1870 / 1920, 1006 / 1080)
        self.btn_exit_map_threshold = 0.5

        self.btn_exit_confirm_image = "app/resource/images/capture_pals/exit_confirm.png"
        self.btn_exit_confirm_crop = (1371 / 1920, 740 / 1080, 1421 / 1920, 787 / 1080)

        # ===== island select =====
        self.partner_island_image = "app/resource/images/capture_pals/partner_island.png"
        self.adventure_island_image = "app/resource/images/capture_pals/adventure_island.png"

        self.partner_island_crop = (707 / 1920, 451 / 1080, 770 / 1920, 504 / 1080)
        self.adventure_island_crop = (1318 / 1920, 558 / 1080, 1378 / 1920, 612 / 1080)

        self.start_battle_text = "开始"
        self.start_battle_crop = (1734 / 1920, 973 / 1080, 1798 / 1920, 1013 / 1080)

        # ===== in-map task icon =====
        self.in_map_task_image = "app/resource/images/capture_pals/in_map_task.png"
        self.in_map_task_crop = (1824 / 1920, 434 / 1080, 1857 / 1920, 465 / 1080)
        self.in_map_task_threshold = 0.65

        # ===== profiles =====
        self.partner_profile = IslandProfile(
            name="伙伴岛", fixed_interval_sec=35.0, patrol_refresh_interval_sec=2.0, enter_wait_sec=self.ENTER_WAIT_SEC
        )
        self.adventure_profile = IslandProfile(
            name="探险岛", fixed_interval_sec=5 * 60.0, patrol_refresh_interval_sec=20 * 60.0, enter_wait_sec=self.ENTER_WAIT_SEC
        )

    # =========================================================
    # 基础工具：刷新、等待、点击重试
    # =========================================================
    def _refresh(self):
        self.auto.take_screenshot()

    def _wait_until(self, predicate, timeout_sec: float, tick: float = 0.2, msg: str = "") -> bool:
        t = Timer(timeout_sec).start()
        if msg:
            self.logger.info(msg)
        while not t.reached():
            self._refresh()
            if predicate():
                return True
            self.sleep_with_log(tick)
        return False

    def _click_image_repeat_if_present(self, img_path: str, crop: tuple, threshold: float, max_times: int, sleep_sec: float = 0.0):
        """
        - 只要还能 click（即找到了并点了），就继续点
        - 最多点 max_times 次
        """
        for _ in range(max_times):
            clicked = self.auto.click_element(img_path, "image", threshold=threshold, crop=crop, is_log=self.is_log)
            if not clicked:
                return
            if sleep_sec > 0:
                self.sleep_with_log(sleep_sec)
            self._refresh()

    def _click_text_repeat_if_present(self, text: str, crop: tuple, max_times: int, sleep_sec: float = 0.0):
        for _ in range(max_times):
            clicked = self.auto.click_element(text, "text", crop=crop, is_log=self.is_log)
            if not clicked:
                return
            if sleep_sec > 0:
                self.sleep_with_log(sleep_sec)
            self._refresh()

    def _right_click_repeat(self, x: float, y: float, max_times: int = 5, press_time: float = 0.06,
                            per_try_timeout: float = 0.6, sleep_sec: float = 0.08,) -> None:
        for _ in range(max_times):
            self.auto.move_click(x, y, "right", press_time=press_time, time_out=per_try_timeout)
            if sleep_sec > 0:
                self.sleep_with_log(sleep_sec)
            self._refresh()

    # =========================================================
    # 状态判定：对外版本会 refresh；内部 no_refresh 避免重复截图
    # =========================================================
    def is_in_map_no_refresh(self) -> bool:
        return bool(
            self.auto.find_element(
                self.in_map_task_image,
                "image",
                threshold=self.in_map_task_threshold,
                crop=self.in_map_task_crop,
                is_log=self.is_log,
                match_method=cv2.TM_CCOEFF_NORMED,
            )
        )

    def is_on_island_select_page_no_refresh(self) -> bool:
        return bool(
            self.auto.find_element(
                self.partner_island_image,
                "image",
                threshold=0.5,
                crop=self.partner_island_crop,
                is_log=self.is_log,
                match_method=cv2.TM_CCOEFF_NORMED,
            )
        )

    def is_in_map(self) -> bool:
        self._refresh()
        return self.is_in_map_no_refresh()

    def is_on_island_select_page(self) -> bool:
        self._refresh()
        return self.is_on_island_select_page_no_refresh()

    # =========================================================
    # 入口
    # =========================================================
    def run(self):
        self.is_log = config.isLog.value

        state = self.wait_for_start_page(timeout_sec=120.0)
        if state == "TIMEOUT":
            self.logger.error("启动失败：超时仍未检测到初始页面。请手动进入抓帕鲁选岛页面或进入地图后再启动。")
            return

        if state == "IN_MAP":
            self.logger.info("检测到已在地图内，先退出回选岛页面以保证流程一致")
            if not self.exit_map_to_island_select():
                self.logger.error("已在地图内但退出失败，请检查退出按钮图片/确认按钮crop")
                return

        enable_partner = config.CheckBox_capture_pals_partner.value
        enable_adventure = config.CheckBox_capture_pals_adventure.value
        sync_enabled = config.CheckBox_capture_pals_sync.value

        self.partner_profile.fixed_interval_sec = float(config.SpinBox_capture_pals_partner_fixed_interval.value)
        self.partner_profile.patrol_refresh_interval_sec = float(config.SpinBox_capture_pals_partner_patrol_interval.value)
        self.adventure_profile.fixed_interval_sec = float(config.SpinBox_capture_pals_adventure_fixed_interval.value)
        self.adventure_profile.patrol_refresh_interval_sec = float(config.SpinBox_capture_pals_adventure_patrol_interval.value)

        if not enable_partner and not enable_adventure:
            self.logger.error("未选择任何岛屿，无法开始抓帕鲁")
            return

        partner_mode = int(config.ComboBox_capture_pals_partner_mode.value) if enable_partner else 0
        adventure_mode = int(config.ComboBox_capture_pals_adventure_mode.value) if enable_adventure else 0

        if sync_enabled and enable_partner and enable_adventure:
            self.logger.info("启用：同步抓帕鲁（两岛独立模式 + 到上限后自动只刷未完成岛）")
            self.sync_capture_loop(partner_mode, adventure_mode)
            return

        if enable_partner and self.auto.running:
            (self.capture_fixed_loop if partner_mode == 0 else self.capture_patrol_loop)(self.partner_profile)

        if enable_adventure and self.auto.running:
            (self.capture_fixed_loop if adventure_mode == 0 else self.capture_patrol_loop)(self.adventure_profile)

    # =========================================================
    # 启动页等待
    # =========================================================
    def wait_for_start_page(self, timeout_sec: float = 60.0) -> str:
        t = Timer(timeout_sec).start()
        warned_at = 0.0

        while not t.reached():
            self._refresh()

            if self.is_in_map_no_refresh():
                return "IN_MAP"

            if self.is_on_island_select_page_no_refresh():
                return "ISLAND_SELECT"

            now = time.monotonic()
            if now - warned_at >= 2.0:
                self.logger.warning("未检测到初始页面（伙伴岛选岛页/地图内任务图标）。请手动进入抓帕鲁初始页面后保持不动。")
                warned_at = now

            self.sleep_with_log(1.0)

        return "TIMEOUT"

    # =========================================================
    # 定点 / 巡逻
    # =========================================================
    def capture_fixed_loop(self, island: IslandProfile):
        self.logger.info(f"开始：{island.name} 定点抓帕鲁，间隔={island.fixed_interval_sec:.1f}s")

        if not self.enter_map(island):
            self.logger.error(f"{island.name}：进入地图失败，终止该岛抓帕鲁")
            return

        self.sleep_with_log(island.enter_wait_sec)

        no_collect_streak = 0
        while self.auto.running:
            result = self.capture_once(island)

            if result == "CAP_REACHED":
                self.logger.warn(f"{island.name}：检测到每日抓帕鲁上限，停止该岛定点抓帕鲁")
                break

            if result == "NO_COLLECT_HINT":
                no_collect_streak += 1
                self.logger.warning(
                    f"{island.name}：本轮未找到F抓帕鲁提示，可能在等待刷新。连续次数={no_collect_streak}/{self.FIXED_NO_COLLECT_MAX}"
                )
                if no_collect_streak >= self.FIXED_NO_COLLECT_MAX:
                    self.logger.error(
                        f"{island.name}：连续多个刷新周期都未出现F提示，可能站位/点位不正确。请调整位置后重试。停止定点模式。"
                    )
                    break
            else:
                no_collect_streak = 0

            self.sleep_with_log(island.fixed_interval_sec, f"{island.name} 等待刷新")

    def capture_patrol_loop(self, island: IslandProfile):
        self.logger.info(f"开始：{island.name} 巡逻抓帕鲁，刷新间隔={island.patrol_refresh_interval_sec:.1f}s")

        no_collect_streak = 0
        while self.auto.running:
            if not self.enter_map(island):
                self.logger.error(f"{island.name}：进入地图失败，终止该岛巡逻抓帕鲁")
                break

            self.sleep_with_log(island.enter_wait_sec)

            result = self.capture_once(island)

            if result == "CAP_REACHED":
                self.logger.warn(f"{island.name}：检测到每日抓帕鲁上限，停止该岛巡逻抓帕鲁")
                break

            if result == "NO_COLLECT_HINT":
                no_collect_streak += 1
                self.logger.warn(
                    f"{island.name}：本轮未找到F抓帕鲁提示，连续次数={no_collect_streak}/{self.PATROL_NO_COLLECT_MAX}"
                )
                if no_collect_streak >= self.PATROL_NO_COLLECT_MAX:
                    self.logger.error(f"{island.name}：连续多轮找不到抓帕鲁提示，可能站位/路线不对。停止该模式。")
                    break
            else:
                no_collect_streak = 0

            if not self.exit_map_to_island_select():
                self.logger.error(f"{island.name}：退出地图失败，停止")
                break

            self.sleep_with_log(island.patrol_refresh_interval_sec, f"{island.name} 巡逻刷新等待")

    # =========================================================
    # 同步抓帕鲁
    # =========================================================
    def sync_capture_loop(self, partner_mode: int, adventure_mode: int):
        partner = _SyncState("partner", self.partner_profile, int(partner_mode))
        adventure = _SyncState("adventure", self.adventure_profile, int(adventure_mode))

        sync_every_sec = max(partner.period_sec(), adventure.period_sec())
        self.logger.info(
            f"同步抓帕鲁：自动同步周期 sync_every_sec≈{sync_every_sec:.0f}s "
            f"(partner≈{partner.period_sec():.0f}s, adventure≈{adventure.period_sec():.0f}s)"
        )

        def available(st: _SyncState) -> bool:
            return not (st.done or st.error)

        def all_finished_or_error() -> bool:
            return (partner.done or partner.error) and (adventure.done or adventure.error)

        def mark_result(st: _SyncState, result: str) -> bool:
            if result == "CAP_REACHED":
                st.done = True
                self.logger.warn(f"{st.profile.name}：检测到每日抓帕鲁上限（同步模式将不再前往该岛）")
                return True

            if result == "NO_COLLECT_HINT":
                st.no_collect_streak += 1
                limit = self.PATROL_NO_COLLECT_MAX if st.mode == 1 else self.FIXED_NO_COLLECT_MAX
                self.logger.warning(
                    f"{st.profile.name}：未找到F抓帕鲁提示，连续次数={st.no_collect_streak}/{limit}"
                    + ("（巡逻）" if st.mode == 1 else "（定点，可能在等刷新）")
                )
                if st.no_collect_streak >= limit:
                    st.error = True
                    self.logger.error(
                        f"{st.profile.name}：连续多轮未出现F提示，标记该岛异常并停止前往。"
                        f"{'（巡逻可能路线/站位不对）' if st.mode == 1 else '（定点可能点位不对）'}"
                    )
                    return True
            else:
                st.no_collect_streak = 0
            return False

        def leave_to_select() -> bool:
            self._refresh()
            if self.is_on_island_select_page_no_refresh():
                return True
            return self.exit_map_to_island_select()

        def enter_island(st: _SyncState) -> bool:
            self._refresh()
            if not self.is_on_island_select_page_no_refresh():
                if not leave_to_select():
                    self.logger.error("同步抓帕鲁：切换/进入前退出地图失败")
                    st.error = True
                    return False

            if not self.enter_map(st.profile):
                self.logger.error(f"同步抓帕鲁：进入{st.profile.name}失败，标记异常")
                st.error = True
                return False

            self.sleep_with_log(st.profile.enter_wait_sec)
            return True

        def do_one_round(st: _SyncState) -> str:
            r = self.capture_once(st.profile)
            if not self.exit_map_to_island_select():
                self.logger.error(f"{st.profile.name}：轮次退出失败，标记异常")
                st.error = True
            return r

        # 起始策略：先长周期，再短周期常驻
        long_st, short_st = (partner, adventure) if partner.period_sec() >= adventure.period_sec() else (adventure, partner)
        self.logger.info(
            f"同步抓帕鲁：启动先处理周期更长的岛={long_st.profile.name} (period≈{long_st.period_sec():.0f}s)，常驻岛={short_st.profile.name}"
        )

        if enter_island(long_st):
            rr = do_one_round(long_st)
            mark_result(long_st, rr)

            if not leave_to_select():
                state = self.wait_for_start_page(timeout_sec=60.0)
                if state != "ISLAND_SELECT":
                    self.logger.error("等待用户回到选岛页面失败，停止抓帕鲁")
                    return

            if not enter_island(short_st):
                self.logger.error("同步抓帕鲁：常驻岛进入失败，终止")
                return
            current, other = short_st, long_st
        else:
            if not enter_island(short_st):
                self.logger.error("同步抓帕鲁：两岛均无法进入，终止")
                return
            current, other = short_st, long_st

        last_switch = time.time()

        while self.auto.running:
            if all_finished_or_error():
                self.logger.warn("同步抓帕鲁：两岛均已完成/异常，结束")
                return

            if not available(current):
                current, other = other, current
                if not available(current):
                    self.logger.warn("同步抓帕鲁：剩余可用岛不存在，结束")
                    return
                if not enter_island(current):
                    continue
                last_switch = time.time()

            r = self.capture_once(current.profile)
            stop_now = mark_result(current, r)
            if stop_now:
                if not leave_to_select():
                    self.logger.error("同步抓帕鲁：状态切换前退出地图失败，终止")
                    return
                continue

            need_switch = available(other) and ((time.time() - last_switch) >= sync_every_sec)

            if current.mode == 1:
                # 巡逻：每轮都退出
                if not leave_to_select():
                    self.logger.error(f"{current.profile.name}：退出地图失败，停止同步")
                    return

                if need_switch:
                    self.logger.info(f"同步抓帕鲁：到达周期，插入 {other.profile.name} 抓一轮")
                    if enter_island(other):
                        rr = do_one_round(other)
                        mark_result(other, rr)
                        last_switch = time.time()
                    if available(current):
                        if not enter_island(current):
                            continue
                else:
                    self.sleep_with_log(current.profile.patrol_refresh_interval_sec, f"{current.profile.name} 巡逻刷新等待")
                    if not enter_island(current):
                        continue
            else:
                # 定点：默认留在图内
                if need_switch:
                    self.logger.info(f"同步抓帕鲁：到达周期，插入 {other.profile.name} 抓一轮")
                    if not leave_to_select():
                        self.logger.error("同步抓帕鲁：定点切岛前退出地图失败，终止")
                        return
                    if enter_island(other):
                        rr = do_one_round(other)
                        mark_result(other, rr)
                        last_switch = time.time()
                    if available(current):
                        if not enter_island(current):
                            continue
                else:
                    self.sleep_with_log(current.profile.fixed_interval_sec, f"{current.profile.name} 等待刷新")

    # =========================================================
    # 进入地图 / 退出地图
    # =========================================================
    def _get_island_target(self, island: IslandProfile):
        if island.name == "伙伴岛":
            return self.partner_island_image, self.partner_island_crop
        return self.adventure_island_image, self.adventure_island_crop

    def enter_map(self, island: IslandProfile) -> bool:
        timeout = Timer(25).start()
        island_img, island_crop = self._get_island_target(island)

        while not timeout.reached():
            self._refresh()

            if self.is_in_map_no_refresh():
                self.logger.info(f"{island.name}：已进入地图（任务图标已出现）")
                return True

            # 点击岛（最多 N 次）
            self._click_image_repeat_if_present(island_img, crop=island_crop, threshold=0.5, max_times=self._RETRY_PER_ACTION, sleep_sec=1.0)
            self.sleep_with_log(1.0)

            # 点击“开始”（最多 N 次）
            self._refresh()
            self._click_text_repeat_if_present(self.start_battle_text, crop=self.start_battle_crop, max_times=self._RETRY_PER_ACTION, sleep_sec=1.0)

            # 等待任务图标出现（用短 wait，循环交回 timeout 控制）
            if self._wait_until(lambda: self.is_in_map_no_refresh(), timeout_sec=3.0, tick=1.0):
                self.logger.info(f"{island.name}：已进入地图")
                return True

        self.logger.error(
            f"{island.name}：进入地图超时（检查：岛按钮 crop、开始按钮 crop、任务图标 crop/threshold，以及是否确实处于选岛界面）"
        )
        return False

    def exit_map_to_island_select(self) -> bool:
        timeout = Timer(20).start()

        while not timeout.reached():
            self._refresh()

            # 若已在选岛，直接成功
            if self.is_on_island_select_page_no_refresh():
                self.logger.info("已回到选岛界面")
                return True

            # 只在地图内才执行退出链
            if self.is_in_map_no_refresh():
                self._right_click_repeat(656 / 1920, 497 / 1080)
                self.sleep_with_log(0.2)

                self.auto.press_key("esc")
                self.sleep_with_log(1.5)

                self.logger.info("尝试点击退出地图按钮")
                self._refresh()
                self._click_image_repeat_if_present(
                    self.btn_exit_map_image,
                    crop=self.btn_exit_map_crop,
                    threshold=self.btn_exit_map_threshold,
                    max_times=self._RETRY_PER_ACTION,
                    sleep_sec=1.0,
                )

                self.logger.info("尝试点击确认退出按钮")
                self._refresh()
                self._click_image_repeat_if_present(
                    self.btn_exit_confirm_image,
                    crop=self.btn_exit_confirm_crop,
                    threshold=0.5,
                    max_times=self._RETRY_PER_ACTION,
                    sleep_sec=1.0,
                )

            # 等一等再判定是否回到选岛（可中断）
            self.sleep_with_log(1.0)

        self.logger.error("退出地图超时（检查：退出按钮图片/crop/threshold、确认按钮crop、选岛判定）")
        return False

    def _wait_collect_state(self, want_present: bool, timeout_sec: float, interval: float = 0.1, stable_count: int = 3) -> bool:
        t = Timer(timeout_sec).start()
        streak = 0
        while not t.reached():
            present = self.is_collect_hint_present()
            if present == want_present:
                streak += 1
                if streak >= stable_count:
                    return True
            else:
                streak = 0
            self.sleep_with_log(interval)
        return False

    def _press_f_until_disappear(self, max_attempts: int, disappear_timeout: float = 1.5, stable_count: int = 3) -> bool:
        for _ in range(max_attempts):
            self.auto.press_key("f")
            self.sleep_with_log(self.FAILED_F_SLEEP)
            if self._wait_collect_state(False, disappear_timeout, interval=0.1, stable_count=stable_count):
                return True
        return False

    def capture_once(self, island: IslandProfile):
        self.auto.press_key("c")
        self.sleep_with_log(0.8)

        appeared = self._wait_collect_state(True, timeout_sec=3.0, interval=0.1, stable_count=3)
        if not appeared:
            return "NO_COLLECT_HINT"

        disappeared = self._press_f_until_disappear(self.MAX_FAILED_F_ATTEMPTS, disappear_timeout=1.5, stable_count=3)
        if not disappeared:
            self.logger.warning(f"{island.name}：按F后图标未消失（尝试{self.MAX_FAILED_F_ATTEMPTS}次），疑似到上限或交互失败")
            return "CAP_REACHED"

        reappeared = self._wait_collect_state(True, timeout_sec=6.5, interval=0.15, stable_count=3)
        if reappeared:
            self.logger.warning(f"{island.name}：F提示消失后又重新出现，疑似达到每日抓帕鲁上限")
            return "CAP_REACHED"

        self.logger.info(f"{island.name}：成功抓到帕鲁")
        return "OK"

    def is_collect_hint_present(self) -> bool:
        self._refresh()
        return bool(
            self.auto.find_element(
                self.collect_image,
                "image",
                threshold=self.collect_threshold,
                crop=self.collect_crop,
                is_log=self.is_log,
                match_method=cv2.TM_CCOEFF_NORMED,
            )
        )

    # =========================================================
    # Sleep（保留 atoms 触发点）
    # =========================================================
    def sleep_with_log(self, sec: float, msg: str = "", tick: float = 0.2):
        if sec <= 0:
            return
        if msg:
            self.logger.info(f"{msg}：{sec:.1f}s")

        end = time.monotonic() + float(sec)
        while True:
            self.auto.take_screenshot(is_interval=False)

            remaining = end - time.monotonic()
            if remaining <= 0:
                return

            time.sleep(min(float(tick), remaining))
