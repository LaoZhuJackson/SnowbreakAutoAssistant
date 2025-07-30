"""
JSON解析工具
提供将字典/JSON自动转换为dataclass的功能
"""

from typing import TypeVar, Type, Dict, Any, get_type_hints, get_origin, get_args
import dataclasses

T = TypeVar('T')


def from_dict(data_class: Type[T], data: Dict[str, Any]) -> T:
    """
    将字典自动转换为dataclass实例
    支持嵌套的dataclass和List类型
    """
    if not dataclasses.is_dataclass(data_class):
        raise ValueError(f"{data_class} is not a dataclass")
    
    field_types = get_type_hints(data_class)
    kwargs = {}
    
    for field in dataclasses.fields(data_class):
        field_name = field.name
        field_type = field_types[field_name]
        
        if field_name not in data:
            if field.default != dataclasses.MISSING:
                kwargs[field_name] = field.default
            elif field.default_factory != dataclasses.MISSING:
                kwargs[field_name] = field.default_factory()
            else:
                raise ValueError(f"Missing required field: {field_name}")
            continue
            
        field_value = data[field_name]
        
        # 处理嵌套的dataclass
        if dataclasses.is_dataclass(field_type):
            kwargs[field_name] = from_dict(field_type, field_value)
        # 处理List类型
        elif get_origin(field_type) is list:
            list_type = get_args(field_type)[0]
            if dataclasses.is_dataclass(list_type):
                kwargs[field_name] = [from_dict(list_type, item) for item in field_value]
            else:
                kwargs[field_name] = field_value
        else:
            kwargs[field_name] = field_value
    
    return data_class(**kwargs)
