"""
六爻排盘核心引擎（查表法修正版）
加载预先生成的六十四卦全量数据，保证卦宫、世应、纳甲、六亲准确无误。
动态计算部分：干支、六神、旬空、动变关系、生克冲合。
新增伏神计算功能。
"""

import sys
import os
import json
from typing import List, Dict, Tuple, Optional, Any

# 处理直接运行时的路径问题
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.core.ganzhi import get_ganzhi_by_date
    from backend.core.liushen import assign_liushen
    from backend.core.xunkong import mark_xunkong
    from backend.core.shengke import ShengKeCalculator
    from backend.utils.constants import DIZHI_WUXING, GUA_WUXING
else:
    from .ganzhi import get_ganzhi_by_date
    from .liushen import assign_liushen
    from .xunkong import mark_xunkong
    from .shengke import ShengKeCalculator
    from ..utils.constants import DIZHI_WUXING, GUA_WUXING

# 类型定义
try:
    from ..models.gua import GuaData, YaoData, BianguaYaoData
except ImportError:
    class YaoData:
        def __init__(self, position: int, yin_yang: int, is_changing: bool = False,
                     dizhi: str = '', wuxing: str = '', liuqin: str = '',
                     liushen: str = '', is_kong: bool = False,
                     biangua_yao: Optional['BianguaYaoData'] = None,
                     biangua_info: Optional['BianguaYaoData'] = None,
                     shengke: str = '',
                     fushen: Optional[str] = None,
                     # 新增日月关系字段
                     ri_zhi: bool = False, ri_sheng: bool = False, ri_ke: bool = False,
                     ri_chong: bool = False, ri_he: bool = False,
                     yue_zhi: bool = False, yue_sheng: bool = False, yue_ke: bool = False,
                     yue_chong: bool = False, yue_he: bool = False,
                     is_andong: bool = False, is_ripo: bool = False, is_yuepo: bool = False,
                     ri_lin: bool = False, yue_lin: bool = False):
            self.position = position
            self.yin_yang = yin_yang
            self.is_changing = is_changing
            self.dizhi = dizhi
            self.wuxing = wuxing
            self.liuqin = liuqin
            self.liushen = liushen
            self.is_kong = is_kong
            self.biangua_yao = biangua_yao
            self.biangua_info = biangua_info
            self.shengke = shengke
            self.fushen = fushen
            # 新增属性赋值
            self.ri_zhi = ri_zhi
            self.ri_sheng = ri_sheng
            self.ri_ke = ri_ke
            self.ri_chong = ri_chong
            self.ri_he = ri_he
            self.yue_zhi = yue_zhi
            self.yue_sheng = yue_sheng
            self.yue_ke = yue_ke
            self.yue_chong = yue_chong
            self.yue_he = yue_he
            self.is_andong = is_andong
            self.is_ripo = is_ripo
            self.is_yuepo = is_yuepo
            self.ri_lin = ri_lin
            self.yue_lin = yue_lin

    class BianguaYaoData:
        def __init__(self, yin_yang: int, dizhi: str, wuxing: str, liuqin: str, is_kong: bool = False):
            self.yin_yang = yin_yang
            self.dizhi = dizhi
            self.wuxing = wuxing
            self.liuqin = liuqin
            self.is_kong = is_kong

    class GuaData:
        def __init__(self, ben_gua_name: str, bian_gua_name: str,
                     yao_list: List[YaoData], shi_yao: int, ying_yao: int,
                     gan_zhi: Dict[str, str], xunkong: Tuple[str, str],
                     relations: Dict[str, Any], special_attr: Optional[str] = None,
                     bian_special_attr: Optional[str] = None):   # 新增参数
            self.ben_gua_name = ben_gua_name
            self.bian_gua_name = bian_gua_name
            self.yao_list = yao_list
            self.shi_yao = shi_yao
            self.ying_yao = ying_yao
            self.gan_zhi = gan_zhi
            self.xunkong = xunkong
            self.relations = relations
            self.special_attr = special_attr
            self.bian_special_attr = bian_special_attr


class LiuyaoEngine:
    """六爻排盘核心引擎（查表法）"""

    def __init__(self):
        # 加载六十四卦全量数据
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', '64gua_full.json')
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"未找到卦象数据文件：{json_path}，请先运行生成脚本。")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.gua_dict = json.load(f)
        self.shengke_calc = ShengKeCalculator()

    def _find_gua_by_yao_list(self, yao_list: List[int]) -> Dict:
        code_str = ''.join(str(x) for x in yao_list)
        for gua_id, gua_info in self.gua_dict.items():
            gua_code = ''.join(str(yao['yin_yang']) for yao in gua_info['yao_list'])
            if gua_code == code_str:
                return gua_info
        raise ValueError(f"未找到匹配的卦象，阴阳序列：{code_str}")

    def _find_gong_gua(self, gong_name: str) -> Dict:
        name_mapping = {
            '乾': '乾为天', '兑': '兑为泽', '离': '离为火', '震': '震为雷',
            '巽': '巽为风', '坎': '坎为水', '艮': '艮为山', '坤': '坤为地'
        }
        pure_name = name_mapping.get(gong_name, f"{gong_name}为{gong_name}")
        for gua_id, gua_info in self.gua_dict.items():
            if gua_info['name'] == pure_name:
                return gua_info
        for gua_id, gua_info in self.gua_dict.items():
            if gua_info.get('gong') == gong_name and gua_info.get('shi') == 6:
                return gua_info
        raise ValueError(f"未找到宫{gong_name}的本宫卦")

    def _get_fushen_for_yao(self, ben_yao_pre: Dict, ben_gua_info: Dict, ben_gong_gua_info: Dict) -> Optional[str]:
        """
        计算某一爻的伏神。
        规则：
        1. 若本卦六亲齐全（5种），则所有爻无伏神返回 None。
        2. 若本卦六亲不全，则仅当本宫同位爻的六亲属于本卦缺失的六亲时，才返回伏神字符串；
           否则返回 None（前端显示“—”）。
        """
        # 本卦实际出现的六亲集合
        ben_liuqin_set = {yao['liuqin'].strip() for yao in ben_gua_info['yao_list']}
        all_liuqin = {'父母', '兄弟', '官鬼', '妻财', '子孙'}

        # 六亲齐全 → 无伏神
        if ben_liuqin_set == all_liuqin:
            return None

        # 计算缺失的六亲
        missing_liuqin = all_liuqin - ben_liuqin_set

        # 本宫同位爻信息
        pos_index = ben_yao_pre['pos'] - 1
        gong_yao = ben_gong_gua_info['yao_list'][pos_index]
        gong_liuqin = gong_yao['liuqin'].strip()

        # 仅当同位爻的六亲是本卦缺失的六亲时，才显示伏神
        if gong_liuqin in missing_liuqin:
            gong_dizhi = gong_yao['dizhi']
            wuxing = DIZHI_WUXING.get(gong_dizhi, '')
            return f"{gong_liuqin}{gong_dizhi}{wuxing}"
        else:
            return None

    def paipan(self, qigua_result: Dict) -> GuaData:
        yao_list = qigua_result['yao_list']
        changing_flags = qigua_result.get('changing_yao', [False] * 6)
        year = qigua_result['year']
        month = qigua_result['month']
        day = qigua_result['day']
        hour = qigua_result.get('hour', 0)

        ganzhi_info = get_ganzhi_by_date(year, month, day, hour)
        day_gan = ganzhi_info['day'][0]
        xunkong = ganzhi_info['xunkong']
        ganzhi_info.pop('xunkong', None)

        bian_yao_list = []
        for i in range(6):
            if changing_flags[i]:
                bian_yao_list.append(1 - yao_list[i])
            else:
                bian_yao_list.append(yao_list[i])

        ben_gua_info = self._find_gua_by_yao_list(yao_list)
        bian_gua_info = self._find_gua_by_yao_list(bian_yao_list)

        ben_gua_name = ben_gua_info['name']
        bian_gua_name = bian_gua_info['name']
        gong = ben_gua_info['gong']
        shi_yao = ben_gua_info['shi']
        ying_yao = ben_gua_info['ying']

        ben_gong_gua_info = self._find_gong_gua(gong)
        liushen_list = assign_liushen(day_gan)

        yao_data_list = []
        for i in range(6):
            pos = i + 1
            ben_yao_pre = ben_gua_info['yao_list'][i]
            ben_yin_yang = ben_yao_pre['yin_yang']
            ben_dizhi = ben_yao_pre['dizhi']
            ben_liuqin = ben_yao_pre['liuqin']
            ben_wuxing = DIZHI_WUXING.get(ben_dizhi, '')
            is_changing = changing_flags[i]
            is_kong = (ben_dizhi in xunkong)

            fushen = self._get_fushen_for_yao(ben_yao_pre, ben_gua_info, ben_gong_gua_info)

            biangua_yao = None
            shengke_relation = ''
            if is_changing:
                bian_yao_pre = bian_gua_info['yao_list'][i]
                bian_dizhi = bian_yao_pre['dizhi']
                bian_wuxing = DIZHI_WUXING.get(bian_dizhi, '')
                bian_liuqin = bian_yao_pre['liuqin']
                bian_is_kong = bian_dizhi in xunkong
                biangua_yao = BianguaYaoData(
                    yin_yang=bian_yao_pre['yin_yang'],
                    dizhi=bian_dizhi,
                    wuxing=bian_wuxing,
                    liuqin=bian_liuqin,
                    is_kong=bian_is_kong
                )
                shengke_relation = self._calc_dongbian_relation(
                    ben_dizhi, ben_wuxing, bian_dizhi, bian_wuxing
                )

            bian_yao_pre = bian_gua_info['yao_list'][i]
            bian_dizhi = bian_yao_pre['dizhi']
            bian_is_kong = bian_dizhi in xunkong
            biangua_info_data = BianguaYaoData(
                yin_yang=bian_yao_pre['yin_yang'],
                dizhi=bian_dizhi,
                wuxing=DIZHI_WUXING.get(bian_dizhi, ''),
                liuqin=bian_yao_pre['liuqin'],
                is_kong=bian_is_kong
            )

            yao = YaoData(
                position=pos,
                yin_yang=ben_yin_yang,
                is_changing=is_changing,
                dizhi=ben_dizhi,
                wuxing=ben_wuxing,
                liuqin=ben_liuqin,
                liushen=liushen_list[i],
                is_kong=is_kong,
                biangua_yao=biangua_yao,
                biangua_info=biangua_info_data,
                shengke=shengke_relation,
                fushen=fushen
            )

            # 计算日月冲合暗动
            ri_zhi = ganzhi_info['day'][1]
            yue_zhi = ganzhi_info['month'][1]
            # 计算日月关系（传入完整干支以便取地支）
            self.shengke_calc.calc_riyue_status(
                yao,
                ganzhi_info['day'],  # 日干支，如 '丁巳'
                ganzhi_info['month']  # 月干支，如 '壬辰'
            )

            yao_data_list.append(yao)

        relations = self.shengke_calc.calc_all_relations_from_yao_list(
            yao_data_list, ganzhi_info['day'], ganzhi_info['month']
        )

        # 获取本卦的特殊属性（六冲、六合、归魂、游魂）
        from backend.utils.constants import SPECIAL_GUA
        special_attr = SPECIAL_GUA.get(ben_gua_name)
        bian_special_attr = SPECIAL_GUA.get(bian_gua_name) if bian_gua_name else None

        return GuaData(
            ben_gua_name=ben_gua_name,
            bian_gua_name=bian_gua_name if any(changing_flags) else '',
            yao_list=yao_data_list,
            shi_yao=shi_yao,
            ying_yao=ying_yao,
            gan_zhi=ganzhi_info,
            xunkong=xunkong,
            relations=relations,
            special_attr=special_attr,
            bian_special_attr=bian_special_attr  # 新增
        )

    def _calc_dongbian_relation(self, ben_dizhi: str, ben_wuxing: str,
                                bian_dizhi: str, bian_wuxing: str) -> str:
        if (ben_dizhi, bian_dizhi) in self.shengke_calc._get_liuhe_set():
            return '化合'
        if (ben_dizhi, bian_dizhi) in self.shengke_calc._get_liuchong_set():
            return '化冲'
        if bian_wuxing == self._get_sheng_relation(ben_wuxing):
            return '回头生'
        elif bian_wuxing == self._get_ke_relation(ben_wuxing):
            return '回头克'
        return ''

    def _get_sheng_relation(self, wuxing: str) -> str:
        mapping = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
        return mapping.get(wuxing, '')

    def _get_ke_relation(self, wuxing: str) -> str:
        mapping = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
        return mapping.get(wuxing, '')


# ====================== ShengKeCalculator 补充方法 ======================
def _ensure_shengke_methods():
    if not hasattr(ShengKeCalculator, '_get_liuhe_set'):
        def _get_liuhe_set(self):
            from backend.utils.constants import LIU_HE
            return LIU_HE
        ShengKeCalculator._get_liuhe_set = _get_liuhe_set

    if not hasattr(ShengKeCalculator, '_get_liuchong_set'):
        def _get_liuchong_set(self):
            from backend.utils.constants import LIU_CHONG
            return LIU_CHONG
        ShengKeCalculator._get_liuchong_set = _get_liuchong_set

    if not hasattr(ShengKeCalculator, 'calc_all_relations_from_yao_list'):
        def calc_all_relations_from_yao_list(self, yao_list, day_ganzhi, month_ganzhi):
            dizhi_list = [yao.dizhi for yao in yao_list]
            liuhe = self.find_liuhe(yao_list)
            liuchong = self.find_liuchong(yao_list)
            sanhe = self.find_sanhe(yao_list)
            shengwangmujue = []
            for yao in yao_list:
                status = self.calc_shengwangmujue_for_yao(yao.wuxing, yao.dizhi, day_ganzhi, month_ganzhi)
                shengwangmujue.append(status)
            # 新增生旺墓绝详情
            shengwangmujue_details = self.calc_shengwangmujue_details(yao_list, day_ganzhi)
            return {
                'liuhe': liuhe,
                'liuchong': liuchong,
                'sanhe': sanhe,
                'shengwangmujue': shengwangmujue,
                'shengwangmujue_details': shengwangmujue_details
            }
        ShengKeCalculator.calc_all_relations_from_yao_list = calc_all_relations_from_yao_list

_ensure_shengke_methods()



# ====================== 测试 ======================
if __name__ == '__main__':
    test_qigua = {
        'yao_list': [1, 0, 1, 0, 0, 1],
        'changing_yao': [False, False, False, True, False, False],
        'year': 2026,
        'month': 4,
        'day': 23,
        'hour': 10
    }

    engine = LiuyaoEngine()
    result = engine.paipan(test_qigua)

    print(f"本卦：{result.ben_gua_name}")
    print(f"变卦：{result.bian_gua_name}")
    print(f"世爻：{result.shi_yao}  应爻：{result.ying_yao}")
    print(f"干支：年{result.gan_zhi['year']} 月{result.gan_zhi['month']} 日{result.gan_zhi['day']} 时{result.gan_zhi['hour']}")
    print(f"旬空：{result.xunkong}")
    print("\n爻位详情（从上爻到初爻）：")
    for yao in reversed(result.yao_list):
        print(f"  {yao.position}爻：{yao.liushen} {yao.liuqin} {yao.dizhi} {'○' if yao.is_changing else ''} {'(空)' if yao.is_kong else ''} 伏神：{yao.fushen or '—'}")
        if yao.biangua_yao:
            print(f"      变：{yao.biangua_yao.liuqin} {yao.biangua_yao.dizhi} {yao.shengke}")
    print("\n六合：", result.relations['liuhe'])
    print("六冲：", result.relations['liuchong'])
    print("三合：", result.relations['sanhe'])