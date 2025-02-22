status = {'maxhp': 4,
          'shp': 4,
          'ehp': 3,
          'live': 0,
          'blank': 1,
          'fired': [],
          'sitems': ['handcuffs'],
          'eitems': [],
          'power': 1,
          'bullet': -1,
          'reversal': False,
          'extra_opp': False,
          'computer': False
          }
# >>当前最佳操作为：shoot_enemy, 胜率为：1.0
# 只剩一个虚弹，玩家有手铐，不是打自己或者用道具，却是打对面

status = {
    'maxhp': 4,
    'shp': 4,
    'ehp': 3,
    'live': 0,
    'blank': 3,
    'fired': [],
    'sitems': ['reset_hammer', 'handcuffs', 'insight_sunglasses'],
    'eitems': [],
    'power': 1,
    'bullet': -1,
    'reversal': False, 'extra_opp': False, 'computer': False
}
# >>当前最佳操作为：shoot_enemy, 胜率为：1.0
# 全是虚弹情况下理想状况应该是对着自己把虚弹开完，但是结果是朝对面开

status = {'maxhp': 2, 'shp': 2, 'ehp': 2, 'live': 1, 'blank': 2, 'fired': [],
          'sitems': ['reset_hammer', 'reset_hammer'], 'eitems': ['insight_sunglasses'], 'power': 1, 'bullet': -1,
          'reversal': False, 'extra_opp': False, 'computer': False}
# >>当前最佳操作为：shoot_enemy, 胜率为：0.8333333333333333
# 直观上应该是赌下一发是虚弹，射自己延续回合，剩下一实一虚打对面（高概率中）


status = {'maxhp': 4,
          'shp': 4,
          'ehp': 4,
          'live': 1,
          'blank': 1,
          'fired': [],
          'sitems': ['reverse_magic', 'reverse_magic'],
          'eitems': ['unload_puppet', 'gem_of_life'],
          'power': 1, 'bullet': -1,
          'reversal': False,
          'extra_opp': False,
          'computer': False}
# 第一次使用反转：当前最佳操作为：reverse_magic, 胜率为：0.5
status = {'maxhp': 4,
          'shp': 4,
          'ehp': 4,
          'live': 1,
          'blank': 1,
          'fired': [],
          'sitems': ['reverse_magic'],
          'eitems': ['unload_puppet', 'gem_of_life'],
          'power': 1, 'bullet': -1,
          'reversal': True,
          'extra_opp': False,
          'computer': False}
# 第二次使用反转：当前最佳操作为：reverse_magic, 胜率为：0.5
status = {'maxhp': 4,
          'shp': 4,
          'ehp': 4,
          'live': 1,
          'blank': 1,
          'fired': [],
          'sitems': [],
          'eitems': ['unload_puppet', 'gem_of_life'],
          'power': 1,
          'bullet': -1,
          'reversal': True,
          'extra_opp': False,
          'computer': False}
# 当前最佳操作为：shoot_self, 胜率为：0.3
