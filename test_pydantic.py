#!/usr/bin/env python3
"""
测试Pydantic解析功能
"""

from app.common.data_models import ApiResponse

# 测试数据
test_data = {
    "status": "ok",
    "data": {
        "version": "2.0.5",
        "redeemCodes": [
            {
                "code": "ACTIVE_CODE_2025",
                "expiredAt": "2025-12-31T23:59:59Z"
            },
            {
                "code": "ANOTHER_ACTIVE_CODE",
                "expiredAt": "2025-08-01T00:00:00Z"
            },
            {
                "code": "123",
                "expiredAt": "2025-08-03T08:37:00.000Z"
            }
        ],
        "updateData": {
            "questName": "理念求索",
            "onlineWidth": 2560,
            "linkId": 282,
            "linkCatId": 7131,
            "stuff": {
                "y2": 883,
                "x2": 270,
                "y1": 850,
                "x1": 209
            },
            "onlineHeight": 1440,
            "chasm": {
                "y2": 528,
                "x2": 1838,
                "y1": 476,
                "x1": 1713
            }
        }
    },
    "timestamp": "2025-07-30T08:58:40.784Z"
}

if __name__ == "__main__":
    try:
        # 直接用 Pydantic 解析
        response = ApiResponse(**test_data)
        
        print("✅ 解析成功!")
        print(f"状态: {response.status}")
        print(f"版本: {response.data.version}")
        print(f"任务名: {response.data.updateData.questName}")
        print(f"兑换码数量: {len(response.data.redeemCodes)}")
        print(f"第一个兑换码: {response.data.redeemCodes[0].code}")
        print(f"Stuff坐标: ({response.data.updateData.stuff.x1}, {response.data.updateData.stuff.y1})")
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
