"""
纳甲装卦模块（修正版）
严格依照《增删卜易》及传统六爻规则
"""

from typing import List, Dict, Tuple

# ====================== 基础数据 ======================

# 八卦与三爻编码（初爻低位）
GUA_CODE_MAP = {
    '111': '乾',
    '110': '兑',
    '101': '离',
    '100': '震',
    '011': '巽',
    '010': '坎',
    '001': '艮',
    '000': '坤'
}

# 八卦五行
GUA_WUXING = {
    '乾': '金', '兑': '金',
    '离': '火',
    '震': '木', '巽': '木',
    '坎': '水',
    '艮': '土', '坤': '土'
}

# 纳甲表（严格按照纳甲歌）
# 格式：卦名 -> {'inner_start': 初爻地支, 'outer_start': 四爻地支, 'order': '顺'/'逆'}
NAJIA_TABLE = {
    '乾': {'inner_start': '子', 'outer_start': '午', 'order': '顺'},
    '坎': {'inner_start': '寅', 'outer_start': '申', 'order': '顺'},
    '震': {'inner_start': '子', 'outer_start': '午', 'order': '顺'},
    '艮': {'inner_start': '辰', 'outer_start': '戌', 'order': '顺'},
    '坤': {'inner_start': '未', 'outer_start': '丑', 'order': '逆'},
    '巽': {'inner_start': '丑', 'outer_start': '未', 'order': '逆'},
    '离': {'inner_start': '卯', 'outer_start': '酉', 'order': '逆'},
    '兑': {'inner_start': '巳', 'outer_start': '亥', 'order': '逆'}
}

# 十二地支标准顺序（用于顺逆排）
DIZHI_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


# ====================== 六十四卦世应表 ======================
# 键：(上卦名, 下卦名) -> (世爻位置, 卦宫, 卦名)
# 世爻位置：1-6，初爻为1

SHIYING_TABLE = {
    # 乾宫八卦
    ('乾', '乾'): (6, '乾', '乾为天'),
    ('乾', '巽'): (1, '乾', '天风姤'),
    ('乾', '艮'): (2, '乾', '天山遁'),
    ('乾', '坤'): (3, '乾', '天地否'),
    ('巽', '乾'): (4, '乾', '风地观'),
    ('艮', '乾'): (5, '乾', '山地剥'),
    ('离', '乾'): (4, '乾', '火地晋'),  # 游魂
    ('兑', '乾'): (3, '乾', '火天大有'), # 归魂
    # 坎宫八卦
    ('坎', '坎'): (6, '坎', '坎为水'),
    ('坎', '兑'): (1, '坎', '水泽节'),
    ('坎', '震'): (2, '坎', '水雷屯'),
    ('坎', '离'): (3, '坎', '水火既济'),
    ('兑', '坎'): (4, '坎', '泽火革'),
    ('震', '坎'): (5, '坎', '雷火丰'),
    ('坤', '坎'): (4, '坎', '地火明夷'), # 游魂
    ('艮', '坎'): (3, '坎', '地水师'),   # 归魂
    # 艮宫八卦
    ('艮', '艮'): (6, '艮', '艮为山'),
    ('艮', '离'): (1, '艮', '山火贲'),
    ('艮', '巽'): (2, '艮', '山天大畜'),
    ('艮', '乾'): (3, '艮', '山泽损'),
    ('离', '艮'): (4, '艮', '火泽睽'),
    ('巽', '艮'): (5, '艮', '天泽履'),
    ('兑', '艮'): (4, '艮', '风泽中孚'), # 游魂
    ('震', '艮'): (3, '艮', '风山渐'),   # 归魂
    # 震宫八卦
    ('震', '震'): (6, '震', '震为雷'),
    ('震', '坤'): (1, '震', '雷地豫'),
    ('震', '坎'): (2, '震', '雷水解'),
    ('震', '兑'): (3, '震', '雷泽归妹'),
    ('坤', '震'): (4, '震', '地风升'),
    ('坎', '震'): (5, '震', '水风井'),
    ('离', '震'): (4, '震', '火风鼎'),   # 游魂
    ('乾', '震'): (3, '震', '火雷噬嗑'), # 归魂
    # 巽宫八卦
    ('巽', '巽'): (6, '巽', '巽为风'),
    ('巽', '乾'): (1, '巽', '风天小畜'),
    ('巽', '离'): (2, '巽', '风火家人'),
    ('巽', '艮'): (3, '巽', '风雷益'),
    ('乾', '巽'): (4, '巽', '天雷无妄'),
    ('离', '巽'): (5, '巽', '火雷噬嗑'),
    ('坎', '巽'): (4, '巽', '水风井'),   # 游魂
    ('坤', '巽'): (3, '巽', '地风升'),   # 归魂
    # 离宫八卦
    ('离', '离'): (6, '离', '离为火'),
    ('离', '艮'): (1, '离', '火山旅'),
    ('离', '乾'): (2, '离', '火天大有'),
    ('离', '震'): (3, '离', '火雷噬嗑'),
    ('艮', '离'): (4, '离', '山火贲'),
    ('乾', '离'): (5, '离', '天火同人'),
    ('巽', '离'): (4, '离', '风火家人'), # 游魂
    ('坎', '离'): (3, '离', '水火既济'), # 归魂
    # 坤宫八卦
    ('坤', '坤'): (6, '坤', '坤为地'),
    ('坤', '震'): (1, '坤', '地雷复'),
    ('坤', '兑'): (2, '坤', '地泽临'),
    ('坤', '坎'): (3, '坤', '地天泰'),
    ('震', '坤'): (4, '坤', '雷天大壮'),
    ('兑', '坤'): (5, '坤', '泽天夬'),
    ('乾', '坤'): (4, '坤', '水天需'),   # 游魂
    ('巽', '坤'): (3, '坤', '水地比'),   # 归魂
    # 兑宫八卦
    ('兑', '兑'): (6, '兑', '兑为泽'),
    ('兑', '坎'): (1, '兑', '泽水困'),
    ('兑', '坤'): (2, '兑', '泽地萃'),
    ('兑', '乾'): (3, '兑', '泽山咸'),
    ('坎', '兑'): (4, '兑', '水山蹇'),
    ('坤', '兑'): (5, '兑', '地山谦'),
    ('震', '兑'): (4, '兑', '雷山小过'), # 游魂
    ('离', '兑'): (3, '兑', '雷泽归妹'), # 归魂
}


def _get_shang_xia_gua(liuyao: List[int]) -> Tuple[str, str]:
    """获取上下卦名称"""
    xia_code = ''.join(str(x) for x in liuyao[0:3])
    shang_code = ''.join(str(x) for x in liuyao[3:6])
    xia = GUA_CODE_MAP[xia_code]
    shang = GUA_CODE_MAP[shang_code]
    return shang, xia


def determine_gua_gong(liuyao: List[int]) -> Dict:
    """
    根据六爻确定卦宫、世应、卦名（使用查表法保证准确）
    """
    shang, xia = _get_shang_xia_gua(liuyao)
    key = (shang, xia)
    if key not in SHIYING_TABLE:
        raise ValueError(f"未找到卦象：上{shang}下{xia}")
    shi_yao, gong, gua_name = SHIYING_TABLE[key]
    ying_yao = (shi_yao + 2) % 6
    if ying_yao == 0:
        ying_yao = 6
    return {
        'gua_name': gua_name,
        'gong': gong,
        'shi_yao': shi_yao,
        'ying_yao': ying_yao,
        'shang_gua': shang,
        'xia_gua': xia
    }


def na_dizhi(liuyao: List[int], gong: str) -> List[str]:
    """
    纳地支（严格按纳甲歌）
    """
    shang, xia = _get_shang_xia_gua(liuyao)
    inner_config = NAJIA_TABLE[xia]
    outer_config = NAJIA_TABLE[shang]

    def get_three(start_zhi: str, direction: str) -> List[str]:
        idx = DIZHI_ORDER.index(start_zhi)
        result = []
        for i in range(3):
            if direction == '顺':
                cur = DIZHI_ORDER[(idx + i) % 12]
            else:  # 逆
                cur = DIZHI_ORDER[(idx - i) % 12]
            result.append(cur)
        return result

    inner = get_three(inner_config['inner_start'], inner_config['order'])
    outer = get_three(outer_config['outer_start'], outer_config['order'])

    # 返回顺序：初、二、三、四、五、上
    return [inner[0], inner[1], inner[2], outer[0], outer[1], outer[2]]


def install_gua_base(liuyao: List[int]) -> Dict:
    """安装卦象基础信息"""
    base = determine_gua_gong(liuyao)
    base['dizhi_list'] = na_dizhi(liuyao, base['gong'])
    return base


# ====================== 测试 ======================
if __name__ == '__main__':
    # 天风姤：初阴，其余阳
    gua = [0, 1, 1, 1, 1, 1]
    res = install_gua_base(gua)
    print(res['gua_name'], res['gong'], '世', res['shi_yao'], '应', res['ying_yao'])
    print('地支:', res['dizhi_list'])