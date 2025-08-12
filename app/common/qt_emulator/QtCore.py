# coding:utf-8
"""
PyQt5 QtCore 模拟模块
提供 QLocale, QObject, pyqtSignal 的基础实现
"""

import threading
from typing import Any, Callable, List, Optional


class pyqtSignal:
    """PyQt5 信号模拟器"""
    
    def __init__(self, *arg_types):
        """
        初始化信号
        arg_types: 信号参数类型（在模拟器中忽略）
        """
        self.arg_types = arg_types
        self._subscribers: List[Callable] = []
        self._lock = threading.Lock()
        
    def connect(self, callback: Callable) -> None:
        """连接信号与槽函数"""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
    
    def disconnect(self, callback: Optional[Callable] = None) -> None:
        """断开连接（None 时断开全部）"""
        with self._lock:
            if callback is None:
                self._subscribers.clear()
            elif callback in self._subscribers:
                self._subscribers.remove(callback)
    
    def emit(self, *args: Any, **kwargs: Any) -> None:
        """发射信号"""
        with self._lock:
            subscribers = self._subscribers.copy()
        
        for subscriber in subscribers:
            try:
                subscriber(*args, **kwargs)
            except Exception as e:
                print(f"Error in signal slot: {e}")
    
    def __get__(self, instance, owner):
        """描述器协议支持"""
        if instance is None:
            return self
        
        # 为每个实例创建独立的信号
        attr_name = None
        for name, value in owner.__dict__.items():
            if value is self:
                attr_name = name
                break
        
        if attr_name:
            instance_attr_name = f"__{attr_name}_signal"
            if not hasattr(instance, instance_attr_name):
                signal_instance = pyqtSignal(*self.arg_types)
                setattr(instance, instance_attr_name, signal_instance)
            return getattr(instance, instance_attr_name)
        
        return self


class QObject:
    """PyQt5 QObject 模拟器"""
    
    def __init__(self, parent=None):
        """初始化 QObject"""
        self.parent = parent
        self._children: List['QObject'] = []
        if parent:
            parent._children.append(self)
    
    def setParent(self, parent: Optional['QObject']):
        """设置父对象"""
        if self.parent:
            try:
                self.parent._children.remove(self)
            except ValueError:
                pass
        
        self.parent = parent
        if parent:
            parent._children.append(self)
    
    def children(self) -> List['QObject']:
        """获取子对象列表"""
        return self._children.copy()
    
    def findChild(self, type_class, name: str = "") -> Optional['QObject']:
        """查找子对象"""
        for child in self._children:
            if isinstance(child, type_class):
                if not name or getattr(child, 'objectName', '') == name:
                    return child
            # 递归查找
            found = child.findChild(type_class, name)
            if found:
                return found
        return None
    
    def deleteLater(self):
        """延迟删除对象"""
        if self.parent:
            try:
                self.parent._children.remove(self)
            except ValueError:
                pass
        self.parent = None
        self._children.clear()


class QLocale:
    """QLocale 模拟类"""
    
    # 语言常量
    Chinese = "Chinese"
    English = "English"
    
    # 国家/地区常量
    China = "China"
    HongKong = "HongKong"
    
    def __init__(self, language=None, country=None):
        """初始化 QLocale"""
        self.language = language
        self.country = country
        
    def name(self):
        """返回语言环境名称"""
        if self.language == self.Chinese and self.country == self.China:
            return "zh_CN"
        elif self.language == self.Chinese and self.country == self.HongKong:
            return "zh_HK"
        elif self.language == self.English:
            return "en_US"
        else:
            return "Auto"
    
    def __str__(self):
        return self.name()
    
    def __repr__(self):
        return f"QLocale({self.language}, {self.country})"
