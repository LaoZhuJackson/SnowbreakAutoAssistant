import threading
from typing import Any, Callable, Optional

class Signal:
    """通用信号发射器 (支持 Qt 风格连接)"""
    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def connect(self, callback: Callable) -> None:
        """连接信号与槽函数"""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def disconnect(self, callback: Optional[Callable] = None) -> None:
        """断开连接 (None 时断开全部)"""
        with self._lock:
            if callback is None:
                self._subscribers.clear()
            elif callback in self._subscribers:
                self._subscribers.remove(callback)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        """发射信号"""
        with self._lock:
            subscribers = self._subscribers.copy()

        for sub in subscribers:
            sub(*args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """支持装饰器语法：@signalBus.signal_name"""
        def decorator(func: Callable):
            self.connect(func)
            return func
        return decorator


class SignalBus:
    """信号总线 (单例模式)"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # 初始化所有信号 (完全对应原始 Qt 信号参数)
            self.checkUpdateSig = Signal()         # type: Signal
            self.micaEnableChanged = Signal()      # type: Signal
            self.switchToSampleCard = Signal()     # type: Signal
            self.updatePiecesNum = Signal()        # type: Signal
            self.jigsawDisplaySignal = Signal()    # type: Signal
            self.showMessageBox = Signal()         # type: Signal
            self.updateFishKey = Signal()          # type: Signal
            self.showScreenshot = Signal()         # type: Signal
            self.sendHwnd = Signal()               # type: Signal
            self._initialized = True


# 全局单例信号总线 (保持与原始代码相同的调用方式)
signalBus = SignalBus()
