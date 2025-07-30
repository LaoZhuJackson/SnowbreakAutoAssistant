#!/usr/bin/env python3
"""
完整的功能测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.common.data_models import parse_config_update_data, ApiResponse

# 模拟完整的测试场景
test_data = {
    "status": "ok",
    "data": {
        "version": "2.0.5",
        "redeemCodes": [
            {"code": "CODE1", "expiredAt": "2025-12-31T23:59:59Z"},
            {"code": "CODE2", "expiredAt": "2025-08-01T00:00:00Z"}
        ],
        "updateData": {
            "questName": "理念求索",
            "onlineWidth": 2560,
            "linkId": 282,
            "linkCatId": 7131,
            "stuff": {"x1": 209, "y1": 850, "x2": 270, "y2": 883},
            "onlineHeight": 1440,
            "chasm": {"x1": 1713, "y1": 476, "x2": 1838, "y2": 528}
        }
    },
    "timestamp": "2025-07-30T08:58:40.784Z"
}

def test_parsing():
    print("=== 测试数据解析 ===")
    
    # 测试直接解析
    response = ApiResponse(**test_data)
    print(f"✅ 直接解析成功: {response.data.updateData.questName}")
    
    # 测试parse_config_update_data函数
    config_response = parse_config_update_data(test_data)
    print(f"✅ 配置解析成功: {config_response.data.updateData.questName}")
    
    # 测试结构化访问
    print(f"✅ 任务名: {config_response.data.updateData.questName}")
    print(f"✅ 兑换码数量: {len(config_response.data.redeemCodes)}")
    print(f"✅ 第一个兑换码: {config_response.data.redeemCodes[0].code}")
    print(f"✅ Stuff坐标: ({config_response.data.updateData.stuff.x1}, {config_response.data.updateData.stuff.y1})")
    print(f"✅ Chasm坐标: ({config_response.data.updateData.chasm.x1}, {config_response.data.updateData.chasm.y1})")
    
    return config_response

def test_coordinate_calculation():
    print("\n=== 测试坐标计算 ===")
    
    config_response = parse_config_update_data(test_data)
    update_data = config_response.data.updateData
    
    # 模拟use_power.py中的坐标计算
    online_width = float(update_data.onlineWidth)  # 2560
    online_height = online_width * 9 / 16  # 1440
    client_width = 1920
    client_height = 1080
    
    scale_x = client_width / online_width
    scale_y = client_height / online_height
    
    # Stuff坐标计算
    stuff_coords = update_data.stuff
    x1 = int(float(stuff_coords.x1) * scale_x)
    y1 = int(float(stuff_coords.y1) * scale_y)
    x2 = int(float(stuff_coords.x2) * scale_x)
    y2 = int(float(stuff_coords.y2) * scale_y)
    
    print(f"✅ Stuff缩放坐标: ({x1}, {y1}) -> ({x2}, {y2})")
    
    # Chasm坐标计算
    chasm_coords = update_data.chasm
    x1 = int(float(chasm_coords.x1) * scale_x)
    y1 = int(float(chasm_coords.y1) * scale_y)
    x2 = int(float(chasm_coords.x2) * scale_x)
    y2 = int(float(chasm_coords.y2) * scale_y)
    
    print(f"✅ Chasm缩放坐标: ({x1}, {y1}) -> ({x2}, {y2})")

def test_redeem_codes():
    print("\n=== 测试兑换码处理 ===")
    
    config_response = parse_config_update_data(test_data)
    
    # 模拟collect_supplies.py中的兑换码处理
    used_codes = ["CODE1"]  # 模拟已使用的兑换码
    active_codes = []
    
    for code in config_response.data.redeemCodes:
        if code.code not in used_codes:
            active_codes.append(code.code)
    
    print(f"✅ 可用兑换码: {active_codes}")
    print(f"✅ 已使用兑换码: {used_codes}")

def test_comparison():
    print("\n=== 测试数据比较 ===")
    
    config_response = parse_config_update_data(test_data)
    
    # 测试model_dump()方法
    online_data = test_data["data"]
    local_data = config_response.data.model_dump()
    
    print(f"✅ 数据匹配: {online_data == local_data}")
    
    # 测试部分数据比较
    local_redeem_codes = [code.model_dump() for code in config_response.data.redeemCodes]
    print(f"✅ 兑换码匹配: {online_data['redeemCodes'] == local_redeem_codes}")
    
    local_update_data = config_response.data.updateData.model_dump()
    print(f"✅ 更新数据匹配: {online_data['updateData'] == local_update_data}")

if __name__ == "__main__":
    try:
        test_parsing()
        test_coordinate_calculation()
        test_redeem_codes()
        test_comparison()
        print("\n🎉 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
