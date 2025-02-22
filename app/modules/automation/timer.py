import time


class Timer:
    def __init__(self, limit, count=0):
        """
        计时器，用于截图频率自动限时
        :param limit: 限制的时间间隔
        :param count: limit时间运行reached所需的次数，reached超过count返回true
        """
        self.limit = limit
        self.count = count
        self._current = 0
        self._reach_count = count

    def started(self):
        return bool(self._current)

    def start(self):
        """
        启动计时器
        :return:
        """
        if not self.started():
            self._current = time.time()
            self._reach_count = 0
        return self

    def current(self):
        """返回当前经过了多久的时间间隔"""
        if self.started():
            return time.time() - self._current
        else:
            return 0.

    def reached(self):
        self._reach_count += 1
        # 返回是否大于时间限制且达到次数是否达标的bool
        return time.time() - self._current > self.limit and self._reach_count > self.count

    def reset(self):
        """重置计时"""
        self._current = time.time()
        self._reach_count = 0
        return self

    def clear(self):
        """恢复出厂设置"""
        self._current = 0
        self._reach_count = self.count
        return self

    def reached_and_reset(self):
        """
        Returns:
            bool:
        """
        if self.reached():
            # 达到一次计时限制后重新计时
            self.reset()
            return True
        else:
            return False

    def wait(self):
        """
        等待一段时间到计时器到计时结束，等待时间会根据limit自动计算
        假如limit=0.3秒，截图耗时 50ms 处理耗时 10ms，会 sleep 240ms 再进行下一次截图
        """
        diff = self._current + self.limit - time.time()
        if diff > 0:
            time.sleep(diff)

    def show(self):
        from app.common.logger import logger
        logger.info(str(self))

    def __str__(self):
        return f'Timer(limit={round(self.current(), 3)}/{self.limit}, count={self._reach_count}/{self.count})'

    __repr__ = __str__
