"""
数据模型定义
用于定义API响应的数据结构
"""

from pydantic import BaseModel
from typing import List, Optional


class Coordinates(BaseModel):
    """坐标数据结构"""
    x1: int
    y1: int
    x2: int
    y2: int


class UpdateData(BaseModel):
    """更新数据结构"""
    questName: str
    onlineWidth: int
    linkId: int
    linkCatId: int
    stuff: Coordinates
    onlineHeight: int
    chasm: Coordinates


class RedeemCode(BaseModel):
    """兑换码数据结构"""
    code: str
    expiredAt: str


class ApiData(BaseModel):
    """API数据结构"""
    version: str
    redeemCodes: List[RedeemCode]
    updateData: UpdateData


class ApiResponse(BaseModel):
    """API响应结构"""
    status: str
    data: ApiData
    timestamp: str


def parse_config_update_data(config_value) -> Optional[ApiResponse]:
    """
    安全地解析配置中的update_data
    :param config_value: config.update_data.value
    :return: 解析后的ApiResponse对象，如果解析失败则返回None
    """
    if not config_value:
        return None
    
    try:
        if isinstance(config_value, dict):
            return ApiResponse(**config_value)
        else:
            # 如果是旧格式的字符串，返回None让调用方处理
            return None
    except Exception:
        return None
