# coding:utf-8
"""
qfluentwidgets 模拟模块
提供配置管理相关类的基础实现
"""

import json
import os
from typing import Any, List, Optional, Union
from enum import Enum


class Theme(Enum):
    """主题枚举"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ConfigSerializer:
    """配置序列化器基类"""
    
    def serialize(self, value: Any) -> str:
        """序列化值"""
        if hasattr(value, 'value') and hasattr(value.value, 'name'):
            return value.value.name()
        return str(value)
    
    def deserialize(self, value: str) -> Any:
        """反序列化值"""
        return value


class BoolValidator:
    """布尔值验证器"""
    
    def validate(self, value: Any) -> bool:
        """验证值是否为有效的布尔值"""
        return isinstance(value, bool)
    
    def correct(self, value: Any) -> bool:
        """纠正值为布尔类型"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)


class OptionsValidator:
    """选项验证器"""
    
    def __init__(self, options: List[Any]):
        """初始化选项验证器"""
        self.options = options
    
    def validate(self, value: Any) -> bool:
        """验证值是否在选项中"""
        return value in self.options
    
    def correct(self, value: Any) -> Any:
        """纠正值，如果不在选项中则返回第一个选项"""
        if value in self.options:
            return value
        return self.options[0] if self.options else None


class ConfigItem:
    """配置项基类"""
    
    def __init__(self, group: str, name: str, default: Any = None, 
                 validator: Optional[Any] = None, serializer: Optional[ConfigSerializer] = None,
                 restart: bool = False):
        """初始化配置项"""
        self.group = group
        self.name = name
        self.default = default
        self.validator = validator
        self.serializer = serializer or ConfigSerializer()
        self.restart = restart
        self._value = default
    
    @property
    def value(self) -> Any:
        """获取配置值"""
        return self._value
    
    @value.setter
    def value(self, val: Any):
        """设置配置值"""
        if self.validator:
            if hasattr(self.validator, 'validate') and not self.validator.validate(val):
                if hasattr(self.validator, 'correct'):
                    val = self.validator.correct(val)
                else:
                    val = self.default
        self._value = val
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"ConfigItem({self.group}.{self.name}={self.value})"


class OptionsConfigItem(ConfigItem):
    """选项配置项"""
    
    def __init__(self, group: str, name: str, default: Any = None,
                 validator: Optional[OptionsValidator] = None,
                 serializer: Optional[ConfigSerializer] = None,
                 restart: bool = False):
        """初始化选项配置项"""
        super().__init__(group, name, default, validator, serializer, restart)


class QConfig:
    """配置管理器"""
    
    def __init__(self):
        """初始化配置"""
        self.themeMode = ConfigItem("theme", "mode", Theme.AUTO)
        self._config_items = {}
        self._file_path = None
        
        # 收集所有配置项
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigItem):
                key = f"{attr.group}.{attr.name}"
                self._config_items[key] = attr
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if key in self._config_items:
            return self._config_items[key].value
        return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """设置配置值"""
        if key in self._config_items:
            self._config_items[key].value = value
            if save and self._file_path:
                self.save()
    
    def save(self, file_path: Optional[str] = None):
        """保存配置到文件"""
        if file_path:
            self._file_path = file_path
        
        if not self._file_path:
            return
        
        config_dict = {}
        for key, item in self._config_items.items():
            group, name = key.split('.', 1)
            if group not in config_dict:
                config_dict[group] = {}
            
            # 序列化值
            try:
                serialized_value = item.serializer.serialize(item.value)
            except:
                serialized_value = item.value
            
            config_dict[group][name] = serialized_value
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        
        # 保存到文件
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def load(self, file_path: str):
        """从文件加载配置"""
        self._file_path = file_path
        
        if not os.path.exists(file_path):
            # 如果文件不存在，使用默认值并保存
            self.save()
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 加载配置值
            for key, item in self._config_items.items():
                group, name = key.split('.', 1)
                if group in config_dict and name in config_dict[group]:
                    try:
                        # 反序列化值
                        value = item.serializer.deserialize(config_dict[group][name])
                        item.value = value
                    except:
                        # 如果反序列化失败，使用原始值
                        item.value = config_dict[group][name]
        
        except Exception as e:
            print(f"Failed to load config: {e}")
            # 如果加载失败，保存默认配置
            self.save()
    
    def toDict(self) -> dict:
        """将配置转换为字典格式"""
        config_dict = {}
        for key, item in self._config_items.items():
            group, name = key.split('.', 1)
            if group not in config_dict:
                config_dict[group] = {}
            
            # 直接使用当前值，不进行序列化
            config_dict[group][name] = item.value
        
        return config_dict


class QConfigMock:
    """qconfig 模拟对象"""
    
    def __init__(self):
        self._current_config = None
    
    def load(self, file_path: str, config: QConfig):
        """加载配置"""
        self._current_config = config
        config.load(file_path)
    
    def save(self):
        """保存配置"""
        if self._current_config:
            self._current_config.save()


# 创建全局 qconfig 实例
qconfig = QConfigMock()
