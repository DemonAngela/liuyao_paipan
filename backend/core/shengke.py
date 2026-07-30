"""
生克冲合计算模块
包含六合、六冲、三合局、生旺墓绝识别
以及日月建对爻位状态的判定
"""

import sys
import os
from typing import List, Tuple, Dict, Set, Optional

# 处理直接运行时的路径问题
if __name__ == '__main__' and __package__ is None:
    # 将项目根目录添加到 sys.path，然后使用绝对导入
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.utils.constants import (
        DIZHI_WUXING,
        LIU_HE, LIU_CHONG, SAN_HE,
        SHENG_WANG_MU_JUE,
        NAJIA_TABLE, DIZHI_ORDER
    )
else:
    from ..utils.constants import (
        DIZHI_WUXING,
        LIU_HE, LIU_CHONG, SAN_HE,
        SHENG_WANG_MU_JUE,
        NAJIA_TABLE, DIZHI_ORDER
    )

# 为了兼容，如果未来有 models.gua 导入也需要处理
try:
    from ..models.gua import GuaData, YaoData
except ImportError:
    # 若直接运行且未定义 models，则定义一个简单的数据类用于测试
    class YaoData:
        def __init__(self, position, dizhi, wuxing, is_changing=False):
            self.position = position
            self.dizhi = dizhi
            self.wuxing = wuxing
            self.is_changing = is_changing
    class GuaData:
        def __init__(self, yao_list):
            self.yao_list = yao_list


class ShengKeCalculator:
    """生克冲合计算器"""

    def __init__(self):
        pass

    @staticmethod
    def _is_liuhe(zhi1: str, zhi2: str) -> bool:
        """判断两个地支是否六合"""
        return (zhi1, zhi2) in LIU_HE

    @staticmethod
    def _is_liuchong(zhi1: str, zhi2: str) -> bool:
        """判断两个地支是否六冲"""
        return (zhi1, zhi2) in LIU_CHONG

    def find_liuhe(self, yao_list) -> List[Tuple[str, str, int, int]]:
        """
        查找六合关系，仅当两爻均动（含暗动）时才计入。
        返回列表，每个元素为 (地支1, 地支2, 爻位1, 爻位2)
        """
        result = []
        n = len(yao_list)
        for i in range(n):
            for j in range(i + 1, n):
                yao1 = yao_list[i]
                yao2 = yao_list[j]
                # 判断两爻是否动爻或暗动
                dong1 = yao1.is_changing or yao1.is_andong
                dong2 = yao2.is_changing or yao2.is_andong
                if not (dong1 or dong2):
                    continue
                if self._is_liuhe(yao1.dizhi, yao2.dizhi):
                    result.append((yao1.dizhi, yao2.dizhi, i + 1, j + 1))
        return result

    def find_liuchong(self, yao_list) -> List[Tuple[str, str, int, int]]:
        """
        查找六冲关系，仅当两爻均动（含暗动）时才计入。
        返回列表，每个元素为 (地支1, 地支2, 爻位1, 爻位2)
        """
        result = []
        n = len(yao_list)
        for i in range(n):
            for j in range(i + 1, n):
                yao1 = yao_list[i]
                yao2 = yao_list[j]
                dong1 = yao1.is_changing or yao1.is_andong
                dong2 = yao2.is_changing or yao2.is_andong
                if not (dong1 or dong2):
                    continue
                if self._is_liuchong(yao1.dizhi, yao2.dizhi):
                    result.append((yao1.dizhi, yao2.dizhi, i + 1, j + 1))
        return result

    def find_sanhe(self, yao_list) -> List[Dict]:
        """
        严格按照《增删卜易》三合规则：
        1. 三爻皆动（明动或暗动），本支成局。
        2. 两爻动，一爻静，本支成局。
        3. 内卦(初、三)中有爻发动，其变爻参与，与初、三爻的本支组成三合。
        4. 外卦(四、六)中有爻发动，其变爻参与，与四、六爻的本支组成三合。
        返回的每个合局包含 items 列表，每项有 pos, dizhi, is_bian, src_pos (变爻来源)。
        """
        combo_order = {
            ('申','子','辰'): '水',
            ('巳','酉','丑'): '金',
            ('寅','午','戌'): '火',
            ('亥','卯','未'): '木'
        }
        n = len(yao_list)
        # 构建爻信息
        infos = []
        for yao in yao_list:
            info = {
                'pos': yao.position,
                'ben': yao.dizhi,
                'bian': yao.biangua_info.dizhi if (yao.is_changing and yao.biangua_info) else None,
                'is_dong': yao.is_changing or yao.is_andong,
                'is_changing': yao.is_changing
            }
            infos.append(info)

        results = []
        seen = set()

        # 辅助函数：检查三个地支是否构成三合，并返回五行和顺序
        def match_combo(d1,d2,d3):
            s = {d1,d2,d3}
            for combo, wuxing in combo_order.items():
                if set(combo) == s:
                    return wuxing, combo
            return None, None

        # 规则1和2：三爻本支组合，要求至少两动 (规则2) 或三动 (规则1)
        for i in range(n):
            for j in range(i+1, n):
                for k in range(j+1, n):
                    d1, d2, d3 = infos[i]['ben'], infos[j]['ben'], infos[k]['ben']
                    wuxing, order = match_combo(d1,d2,d3)
                    if not wuxing:
                        continue
                    dong_count = sum([infos[i]['is_dong'], infos[j]['is_dong'], infos[k]['is_dong']])
                    if dong_count >= 2:  # 规则1或2
                        key = (wuxing, frozenset([i+1,j+1,k+1]), 'ben')
                        if key not in seen:
                            seen.add(key)
                            items = []
                            # 按 order 顺序构建 items
                            for zhi in order:
                                if zhi == d1:
                                    items.append({'pos': i+1, 'dizhi': zhi, 'is_bian': False})
                                elif zhi == d2:
                                    items.append({'pos': j+1, 'dizhi': zhi, 'is_bian': False})
                                else:
                                    items.append({'pos': k+1, 'dizhi': zhi, 'is_bian': False})
                            results.append({'wuxing': wuxing, 'items': items})

        # 规则3：内卦初爻(1)、三爻(3)参与，且至少一爻发动，使用变支
        for dong_pos in [1, 3]:
            static_pos = 4 - dong_pos  # 1->3, 3->1
            dong_idx = dong_pos - 1
            static_idx = static_pos - 1
            dong_info = infos[dong_idx]
            static_info = infos[static_idx]
            if not dong_info['is_dong'] or not dong_info['is_changing'] or dong_info['bian'] is None:
                continue
            # 候选地支：dong 本支、dong 变支、static 本支
            d1, d2, d3 = dong_info['ben'], dong_info['bian'], static_info['ben']
            wuxing, order = match_combo(d1, d2, d3)
            if wuxing:
                key = (wuxing, frozenset([dong_pos, static_pos]), 'bian3_inner')
                if key not in seen:
                    seen.add(key)
                    items = []
                    for zhi in order:
                        if zhi == d1:
                            items.append({'pos': dong_pos, 'dizhi': zhi, 'is_bian': False})
                        elif zhi == d2:
                            items.append({'pos': dong_pos, 'dizhi': zhi, 'is_bian': True, 'src_pos': dong_pos})
                        else:
                            items.append({'pos': static_pos, 'dizhi': zhi, 'is_bian': False})
                    results.append({'wuxing': wuxing, 'items': items})

        # 规则4：外卦四爻(4)、六爻(6)参与，类似
        for dong_pos in [4, 6]:
            static_pos = 10 - dong_pos  # 4->6, 6->4
            dong_idx = dong_pos - 1
            static_idx = static_pos - 1
            dong_info = infos[dong_idx]
            static_info = infos[static_idx]
            if not dong_info['is_dong'] or not dong_info['is_changing'] or dong_info['bian'] is None:
                continue
            d1, d2, d3 = dong_info['ben'], dong_info['bian'], static_info['ben']
            wuxing, order = match_combo(d1, d2, d3)
            if wuxing:
                key = (wuxing, frozenset([dong_pos, static_pos]), 'bian4_outer')
                if key not in seen:
                    seen.add(key)
                    items = []
                    for zhi in order:
                        if zhi == d1:
                            items.append({'pos': dong_pos, 'dizhi': zhi, 'is_bian': False})
                        elif zhi == d2:
                            items.append({'pos': dong_pos, 'dizhi': zhi, 'is_bian': True, 'src_pos': dong_pos})
                        else:
                            items.append({'pos': static_pos, 'dizhi': zhi, 'is_bian': False})
                    results.append({'wuxing': wuxing, 'items': items})

        return results

    def calc_shengwangmujue_for_yao(self, yao_wuxing: str, yao_dizhi: str,
                                    ri_ganzhi: str, yue_ganzhi: str) -> Dict[str, Optional[str]]:
        """
        计算单个爻在日月建下的生旺墓绝状态
        参数：
            yao_wuxing: 爻的五行
            yao_dizhi: 爻的地支
            ri_ganzhi: 日干支（如 '丁卯'）
            yue_ganzhi: 月干支（如 '癸巳'）
        返回：
            {'日建': '长生'/'旺'/'墓'/'绝'/None, '月建': '长生'/'旺'/'墓'/'绝'/None}
        """
        ri_zhi = ri_ganzhi[1]
        yue_zhi = yue_ganzhi[1]

        result = {'日建': None, '月建': None}

        if yao_wuxing not in SHENG_WANG_MU_JUE:
            return result

        swmj = SHENG_WANG_MU_JUE[yao_wuxing]

        # 检查日建
        if ri_zhi == swmj['生']:
            result['日建'] = '长生'
        elif ri_zhi == swmj['旺']:
            result['日建'] = '帝旺'
        elif ri_zhi == swmj['墓']:
            result['日建'] = '墓'
        elif ri_zhi == swmj['绝']:
            result['日建'] = '绝'

        # 检查月建
        if yue_zhi == swmj['生']:
            result['月建'] = '长生'
        elif yue_zhi == swmj['旺']:
            result['月建'] = '帝旺'
        elif yue_zhi == swmj['墓']:
            result['月建'] = '墓'
        elif yue_zhi == swmj['绝']:
            result['月建'] = '绝'

        return result

    def calc_all_relations(self, gua_data) -> Dict:
        """
        综合计算卦中的所有生克冲合关系
        参数：
            gua_data: GuaData 对象，包含完整的六爻数据
        返回：
            字典，包含六合、六冲、三合、各爻生旺墓绝等信息
        """
        dizhi_list = [yao.dizhi for yao in gua_data.yao_list]

        liuhe = self.find_liuhe(gua_data.yao_list)      # ✅ 传递爻对象列表
        liuchong = self.find_liuchong(gua_data.yao_list)

        # 获取动爻标志（如果有）
        changing_flags = [yao.is_changing for yao in gua_data.yao_list]
        sanhe = self.find_sanhe(dizhi_list, changing_flags)

        # 假设 gua_data 包含日建月建信息，这里需要从外部传入
        # 实际使用时，应由引擎传入，此处先留空
        shengwangmujue_list = []
        # for yao in gua_data.yao_list:
        #     status = self.calc_shengwangmujue_for_yao(yao.wuxing, yao.dizhi, ri, yue)
        #     shengwangmujue_list.append(status)

        return {
            'liuhe': liuhe,
            'liuchong': liuchong,
            'sanhe': sanhe,
            'shengwangmujue': shengwangmujue_list
        }

    def calc_shengwangmujue_details(self, yao_list, day_ganzhi, month_ganzhi=None):
        """
        计算每个爻的生旺墓绝触发详情（入日、入动、动化）。
        返回字符串列表，每项如 "[初爻申金]长生在巳[日建巳火]"。
        """
        table = {
            '金': {'长生': '巳', '旺': '酉', '墓': '丑', '绝': '寅'},
            '木': {'长生': '亥', '旺': '卯', '墓': '未', '绝': '申'},
            '火': {'长生': '寅', '旺': '午', '墓': '戌', '绝': '亥'},
            '水': {'长生': '申', '旺': '子', '墓': '辰', '绝': '巳'},
            '土': {'长生': '申', '旺': '子', '墓': '辰', '绝': '巳'}
        }
        pos_names = {1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上'}
        day_zhi = day_ganzhi[1]  # 日支
        results = []

        for yao in yao_list:
            wuxing = yao.wuxing
            if wuxing not in table:
                continue
            states = table[wuxing]
            # 遍历状态：长生、旺、墓、绝
            for state, target_zhi in states.items():
                # 入日
                if day_zhi == target_zhi:
                    results.append(
                        f"[{pos_names[yao.position]}爻{yao.dizhi}{wuxing}]{state}在{target_zhi}[日建{day_zhi}火]")  # 日建五行固定火？需要根据日干定，简单用日支五行
                    # 实际日建五行通过 DIZHI_WUXING 取得，完善一下
                    day_wuxing = DIZHI_WUXING[day_zhi]
                    results[
                        -1] = f"[{pos_names[yao.position]}爻{yao.dizhi}{wuxing}]{state}在{target_zhi}[日建{day_zhi}{day_wuxing}]"
                # 入动：其他明动爻
                for other in yao_list:
                    if other is yao or not (other.is_changing or other.is_andong):
                        continue
                    if other.dizhi == target_zhi:
                        results.append(
                            f"[{pos_names[yao.position]}爻{yao.dizhi}{wuxing}]{state}在{target_zhi}[{pos_names[other.position]}爻{other.dizhi}{other.wuxing}]")
                # 动化：自身明动且变爻
                if yao.is_changing and yao.biangua_info:
                    bian_dizhi = yao.biangua_info.dizhi
                    if bian_dizhi == target_zhi:
                        bian_wuxing = DIZHI_WUXING.get(bian_dizhi, '')
                        results.append(
                            f"[{pos_names[yao.position]}爻{yao.dizhi}{wuxing}]{state}在{target_zhi}[变爻{bian_dizhi}{bian_wuxing}]")
        return results

    def _is_wang_single(self, yao_wuxing: str, yue_zhi: str) -> bool:
        """简化的旺衰判断：爻临月建或得月建生扶为旺"""
        from backend.utils.constants import DIZHI_WUXING
        yue_wuxing = DIZHI_WUXING[yue_zhi]
        if yao_wuxing == yue_wuxing:
            return True
        # 月建生爻
        if (yue_wuxing, yao_wuxing) in [('木','火'), ('火','土'), ('土','金'), ('金','水'), ('水','木')]:
            return True
        return False

    def calc_riyue_status(self, yao, ri_ganzhi: str, yue_ganzhi: str):
        """
        为单个爻精确计算日月建的各种关系（临、生、合、冲、克、破、暗动）
        直接修改 yao 对象的属性。
        """
        from backend.utils.constants import LIU_CHONG, LIU_HE, DIZHI_WUXING

        ri_zhi = ri_ganzhi[1]   # 日支
        yue_zhi = yue_ganzhi[1] # 月支

        yao_wuxing = yao.wuxing
        yao_dizhi = yao.dizhi

        ri_wuxing = DIZHI_WUXING[ri_zhi]
        yue_wuxing = DIZHI_WUXING[yue_zhi]

        # 日建关系
        yao.ri_zhi = (yao_dizhi == ri_zhi)
        # 日建五行相同（临） —— 地支不同但五行相同
        yao.ri_lin = (ri_wuxing == yao_wuxing) and not yao.ri_zhi
        yao.ri_he = (yao_dizhi, ri_zhi) in LIU_HE
        yao.ri_chong = (yao_dizhi, ri_zhi) in LIU_CHONG
        yao.ri_sheng = (ri_wuxing, yao_wuxing) in [('木','火'), ('火','土'), ('土','金'), ('金','水'), ('水','木')]
        yao.ri_ke = (ri_wuxing, yao_wuxing) in [('木','土'), ('火','金'), ('土','水'), ('金','木'), ('水','火')]

        # 月建关系
        yao.yue_zhi = (yao_dizhi == yue_zhi)
        # 月建五行相同（临）
        yao.yue_lin = (yue_wuxing == yao_wuxing) and not yao.yue_zhi
        yao.yue_he = (yao_dizhi, yue_zhi) in LIU_HE
        yao.yue_chong = (yao_dizhi, yue_zhi) in LIU_CHONG
        yao.yue_sheng = (yue_wuxing, yao_wuxing) in [('木','火'), ('火','土'), ('土','金'), ('金','水'), ('水','木')]
        yao.yue_ke = (yue_wuxing, yao_wuxing) in [('木','土'), ('火','金'), ('土','水'), ('金','木'), ('水','火')]

        yao.is_yuepo = yao.yue_chong

        # 暗动/日破判断（需先有日冲，且非动爻）
        if not yao.is_changing and yao.ri_chong:
            # 若爻月破，则不论旺衰，均视为日破（月破之爻逢冲更破）
            if yao.is_yuepo:
                yao.is_andong = False
                yao.is_ripo = True
            else:
                # 判断旺衰：临月或月生为旺；被月克或休囚为衰（此处不考虑动爻生扶，因为引擎中不易获取全局关系）
                # 简化：用月建关系，若得月建生/临则旺，否则衰
                is_wang = yao.yue_zhi or yao.yue_sheng or yao.yue_lin
                # 若爻旬空且旺相，冲空则实，为暗动
                if yao.is_kong and is_wang:
                    yao.is_andong = True
                    yao.is_ripo = False
                elif not yao.is_kong and is_wang:
                    yao.is_andong = True
                    yao.is_ripo = False
                else:
                    yao.is_ripo = True
                    yao.is_andong = False
        else:
            yao.is_andong = False
            yao.is_ripo = False

    def _is_wang_single(self, yao_wuxing: str, yue_zhi: str) -> bool:
        """简化的旺衰判断：爻临月建或得月建生扶为旺"""
        from backend.utils.constants import DIZHI_WUXING
        yue_wuxing = DIZHI_WUXING[yue_zhi]
        if yao_wuxing == yue_wuxing:
            return True
        if (yue_wuxing, yao_wuxing) in [('木','火'), ('火','土'), ('土','金'), ('金','水'), ('水','木')]:
            return True
        return False



# ====================== 测试代码 ======================
if __name__ == '__main__':
    # 模拟测试数据
    test_dizhi = ['子', '丑', '寅', '午', '申', '辰']
    calc = ShengKeCalculator()

    print("测试六合：")
    he = calc.find_liuhe(test_dizhi)
    for h in he:
        print(f"  {h[0]}与{h[1]}合，爻位{h[2]}-{h[3]}")

    print("\n测试六冲：")
    chong = calc.find_liuchong(test_dizhi)
    for c in chong:
        print(f"  {c[0]}冲{c[1]}，爻位{c[2]}-{c[3]}")

    print("\n测试三合：")
    san = calc.find_sanhe(test_dizhi)
    for s in san:
        print(f"  三合{s['wuxing']}局：{s['zhi_set']}，爻位{s['positions']}")

    print("\n测试生旺墓绝（假设爻五行金，日建酉，月建子）：")
    status = calc.calc_shengwangmujue_for_yao('金', '酉', '丁酉', '甲子')
    print(f"  日建状态：{status['日建']}，月建状态：{status['月建']}")


    def find_liuhe_with_dong(self, dizhi_list: List[str], dong_flags: List[bool]) -> List[Tuple[str, str, int, int]]:
        """
        查找六合关系，仅当两个爻均动（明动或暗动）时才计入。
        返回列表，元素为 (地支1, 地支2, 爻位1, 爻位2)
        """
        result = []
        n = len(dizhi_list)
        for i in range(n):
            for j in range(i + 1, n):
                if dong_flags[i] and dong_flags[j] and self._is_liuhe(dizhi_list[i], dizhi_list[j]):
                    result.append((dizhi_list[i], dizhi_list[j], i + 1, j + 1))
        return result


    def find_liuchong_with_dong(self, dizhi_list: List[str], dong_flags: List[bool]) -> List[Tuple[str, str, int, int]]:
        """
        查找六冲关系，仅当两个爻均动时才计入。
        """
        result = []
        n = len(dizhi_list)
        for i in range(n):
            for j in range(i + 1, n):
                if dong_flags[i] and dong_flags[j] and self._is_liuchong(dizhi_list[i], dizhi_list[j]):
                    result.append((dizhi_list[i], dizhi_list[j], i + 1, j + 1))
        return result