# -*- coding: utf-8 -*-
"""
模块名称: 心动水弹决策推荐
模块作者: polynya-code@outlook.com
最后修改日期: 2025-02-20
"""
from copy import deepcopy
from typing import List, Dict, Tuple


class Status:
    def __init__(
            self,
            maxhp: int,  # 最大生命上限
            shp: int,  # 我方hp
            ehp: int,  # 敌方hp
            live: int,  # 剩余实弹数
            blank: int,  # 剩余虚弹数
            fired: List[int],  # 已经射击的子弹类型 0:虚弹 1:实弹
            sitems: List[str],  # 我方道具列表
            eitems: List[str],  # 敌方道具列表
            power: int,  # 当前子弹威力
            bullet: int,  # 当前子弹类型 -1:未知 0:虚弹 1:实弹
            reversal: bool,  # 当前子弹伤害是否取反
            extra_opp: bool,  # 是否能够多一次额外的机会
            computer: bool,  # 当前操作玩家
    ):
        self._maxhp = maxhp
        self._shp = shp
        self._ehp = ehp
        self._live = live
        self._blank = blank
        self._fired = list(fired)
        self._sitems = list(sitems)
        self._eitems = list(eitems)
        self._power = power
        self._bullet = bullet
        self._reversal = reversal
        self._extra_opp = extra_opp
        self._computer = computer

    def __str__(self):
        return (
            f'[maxhp:{self._maxhp}'
            f'|shp:{self._shp}'
            f'|ehp:{self._ehp}'
            f'|live:{self._live}'
            f'|blank:{self._blank}'
            f'|fired:{self._fired}'
            f'|sitems:{sorted(self._sitems)}'
            f'|eitems:{sorted(self._eitems)}'
            f'|power:{self._power}'
            f'|bullet:{self._bullet}'
            f'|reversal:{self._reversal}'
            f'|extra_opp:{self._extra_opp}'
            f'|computer:{self._computer}]'
        )

    @property
    def maxhp(self) -> int:
        return self._maxhp

    @property
    def shp(self) -> int:
        return self._shp

    @property
    def ehp(self) -> int:
        return self._ehp

    @property
    def live(self) -> int:
        return self._live

    @property
    def blank(self) -> int:
        return self._blank

    @property
    def fired(self) -> Tuple[int]:
        return tuple(self._fired)

    @property
    def sitems(self) -> Tuple[str]:
        return tuple(self._sitems)

    @property
    def eitems(self) -> Tuple[str]:
        return tuple(self._eitems)

    @property
    def power(self) -> int:
        return self._power

    @property
    def bullet(self) -> int:
        return self._bullet

    @property
    def reversal(self) -> bool:
        return self._reversal

    @property
    def extra_opp(self) -> bool:
        return self._extra_opp

    @property
    def computer(self) -> bool:
        return self._computer

    @staticmethod
    def from_dict(status_dict: Dict):
        status = Status(4, 4, 4, 2, 2, [], [], [], 1, -1, False, False, False).copy()
        for key, value in status_dict.items():
            key = '_' + key
            if hasattr(status, key):
                setattr(status, key, value)
        return status

    def copy(self):
        return deepcopy(self)

    def gem_of_life(self):  # 生命宝石
        status = self.copy()
        status._shp += 1
        status._sitems.remove('gem_of_life')
        return status

    def handcuffs(self):  # 手铐
        status = self.copy()
        status._extra_opp = True
        status._sitems.remove('handcuffs')
        return status

    def hand_of_kaito(self, item: str):  # 怪盗之手
        status = self.copy()
        status._sitems.remove('hand_of_kaito')
        status._eitems.remove(item)
        status._sitems.append(item)
        return status

    def insight_sunglasses(self, bullet: int):  # 看破墨镜
        status = self.copy()
        status._bullet = bullet
        status._sitems.remove('insight_sunglasses')
        return status

    def reverse_magic(self):  # 反转魔法
        status = self.copy()
        status._reversal = (self.reversal == False)
        status._sitems.remove('reverse_magic')
        return status

    def advanced_barrel(self):  # 进阶枪管
        status = self.copy()
        status._power = 2
        status._sitems.remove('advanced_barrel')
        return status

    def unload_puppet(self, live: bool):  # 退弹布偶
        status = self.copy()
        if live:
            status._live -= 1
        else:
            status._blank -= 1
        status._sitems.remove('unload_puppet')
        status._bullet = -1  # 退弹后不知道最新的子弹类型
        if status.live == 0 and status.blank != 0:  # 可预知子弹情况
            status._bullet = 0
        elif status.blank == 0 and status.live != 0:
            status._bullet = 1
        status._reversal = False  # 退弹后反转重置
        return status

    def reset_hammer(self, old_items: List[str], new_items: List[str]):  # 重置之锤
        status = self.copy()
        for old_item, new_item in zip(old_items, new_items):
            status._sitems.remove(old_item)
            status._sitems.append(new_item)
        status._sitems.remove('reset_hammer')
        return status

    def shoot(self, enemy: bool, live: bool):
        fired = list(self.fired)
        fired.append(int(live))
        if self.reversal:  # 反转魔法
            power = self.power * int(live == False)
        else:
            power = self.power * int(live)

        if live:  # 处理子弹数量
            live = self.live - 1
            blank = self.blank
        else:
            live = self.live
            blank = self.blank - 1

        bullet = -1
        if live == 0 and blank != 0:  # 可预知子弹情况
            bullet = 0
        elif blank == 0 and live != 0:
            bullet = 1

        if enemy:  # 处理伤害
            shp = self.shp
            ehp = self.ehp - power
        else:
            shp = self.shp - power
            ehp = self.ehp

        if shp < 0:
            shp = 0
        if ehp < 0:
            ehp = 0

        extra_opp = False
        sitems = self.sitems
        eitems = self.eitems
        if self.extra_opp or (not enemy and power == 0):  # 处理回合交替 (额外机会或者打自己没事)
            computer = self.computer
            extra_opp = (self.extra_opp and (not enemy and power == 0))
        else:
            computer = (self.computer == False)
            sitems = self.eitems
            eitems = self.sitems
            thp = shp
            shp = ehp
            ehp = thp

        return Status(
            maxhp=self.maxhp,
            shp=shp,
            ehp=ehp,
            live=live,
            blank=blank,
            fired=fired,
            sitems=sitems,
            eitems=eitems,
            power=1,
            bullet=bullet,
            reversal=False,
            extra_opp=extra_opp,
            computer=computer
        ).copy()


class Round:
    def __init__(self):
        self.memo = {}

    def optimal_strategy(self, status: Status):
        # 基本情况处理
        if status.shp == 0:  # 己方死亡
            return 0.0, 'end'
        elif status.ehp == 0:  # 敌方死亡
            return 1.0, 'end'
        elif status.live + status.blank == 0:
            if status.shp == status.ehp:  # 血量相同 (当前谁操作，当前谁胜率就高)
                return 0.6, 'feed'
            else:  # 血量不同 先验胜率为血量之比
                return (status.shp / (status.shp + status.ehp)), 'feed'

        # 记忆化检查
        if str(status) in self.memo:
            return self.memo[str(status)]

        # 子弹情况
        total = status.live + status.blank
        live_prob = status.live / total  # 实弹概率
        blank_prob = status.blank / total  # 虚弹概率
        if status.bullet == 1:  # 已知当前为实弹
            live_prob = 1.0
            blank_prob = 0.0
        elif status.bullet == 0:  # 已知当前为虚弹
            live_prob = 0.0
            blank_prob = 1.0

        # 当前最好操作
        strategy = ''
        win_prob = 0

        # 生命宝石 (优先使用)
        if 'gem_of_life' in status.sitems and status.shp < status.maxhp:
            gem_of_life = self.optimal_strategy(status.gem_of_life())[0]
            return gem_of_life, 'gem_of_life'

        # 拘束手铐 (优先使用)
        if 'handcuffs' in status.sitems and not status.extra_opp:
            handcuffs = self.optimal_strategy(status.handcuffs())[0]
            return handcuffs, 'handcuffs'

        # 怪盗之手 (对面有怪盗之手优先使用)
        if 'hand_of_kaito' in status.sitems:
            for item in status.eitems:
                hand_of_kaito = self.optimal_strategy(status.hand_of_kaito(item))[0]
                if item == 'hand_of_kaito':
                    return hand_of_kaito, 'hand_of_kaito.hand_of_kaito'
                if hand_of_kaito > win_prob:
                    win_prob = hand_of_kaito
                    strategy = f'hand_of_kaito.{item}'

        # 看破墨镜
        if 'insight_sunglasses' in status.sitems and (status.bullet == -1 or 'hand_of_kaito' in status.eitems):
            bullet_blank = blank_prob * self.optimal_strategy(status.insight_sunglasses(0))[0]
            bullet_live = live_prob * self.optimal_strategy(status.insight_sunglasses(1))[0]
            insight = bullet_blank + bullet_live
            if insight > win_prob:
                win_prob = insight
                strategy = 'insight_sunglasses'

        # 反转魔术
        if 'reverse_magic' in status.sitems and (not status.reversal or 'hand_of_kaito' in status.eitems):
            reverse_magic = self.optimal_strategy(status.reverse_magic())[0]
            if reverse_magic > win_prob:
                win_prob = reverse_magic
                strategy = 'reverse_magic'

        # 进阶枪管
        if 'advanced_barrel' in status.sitems and status.power == 1:
            advanced_barrel = self.optimal_strategy(status.advanced_barrel())[0]
            if advanced_barrel > win_prob:
                win_prob = advanced_barrel
                strategy = 'advanced_barrel'

        # 退弹布偶
        if 'unload_puppet' in status.sitems and ((status.live + status.blank) > 1):
            if status.bullet != 0 or not (status.bullet == 1 and status.reversal):  # 已知虚弹一定不退弹或者反转实弹不退弹
                unload_live = live_prob * self.optimal_strategy(status.unload_puppet(True))[0]
                unload_blank = blank_prob * self.optimal_strategy(status.unload_puppet(False))[0]
                unload = unload_live + unload_blank
                if unload > win_prob:
                    win_prob = unload
                    strategy = 'unload_puppet'

        # 重置之锤
        if 'reset_hammer' in status.sitems:
            pass

        # 如果射击
        shoot_enemy = 0.0  # 射击敌人胜率
        shoot_self = 0.0  # 射击自己胜率

        # 实弹分支
        if status.live > 0 and (status.bullet != 0):
            # 射击敌方的情况
            if status.extra_opp:  # 有额外机会一定回合不换
                shoot_enemy += live_prob * self.optimal_strategy(status.shoot(True, True))[0]
            else:  # 没额外机会一定会回合切换
                shoot_enemy += live_prob * (1 - self.optimal_strategy(status.shoot(True, True))[0])
            # 射击自己的情况
            if status.extra_opp or status.reversal:
                shoot_self += live_prob * self.optimal_strategy(status.shoot(False, True))[0]
            else:
                shoot_self += live_prob * (1 - self.optimal_strategy(status.shoot(False, True))[0])

        # 虚弹分支
        if status.blank > 0 and (status.bullet != 1):
            # 射击敌方的情况
            if status.extra_opp:  # 有额外机会一定回合不换
                shoot_enemy += blank_prob * self.optimal_strategy(status.shoot(True, False))[0]
            else:  # 没额外机会一定会回合切换
                shoot_enemy += blank_prob * (1 - self.optimal_strategy(status.shoot(True, False))[0])
            # 射击自己的情况
            if status.reversal and not status.extra_opp:  # 反转且没有保持
                shoot_self += blank_prob * (1 - self.optimal_strategy(status.shoot(False, False))[0])
            else:
                shoot_self += blank_prob * self.optimal_strategy(status.shoot(False, False))[0]

        # 取最优策略并记忆化
        if shoot_enemy < shoot_self or (blank_prob > live_prob and not status.reversal and status.power == 1) or (
                live_prob > blank_prob and status.reversal and status.power == 1):
            shoot = 'shoot_self'
        else:
            shoot = 'shoot_enemy'
        if max(shoot_enemy, shoot_self) > win_prob or max(shoot_enemy, shoot_self) == 1:
            win_prob = max(shoot_enemy, shoot_self)
            strategy = shoot

        self.memo[str(status)] = win_prob, strategy
        return win_prob, strategy