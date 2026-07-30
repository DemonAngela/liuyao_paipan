"""
旬空标注模块
根据日干支计算的旬空地支，标注卦中各爻是否旬空。
"""

from typing import List, Tuple


def mark_xunkong(dizhi_list: List[str], xunkong: Tuple[str, str]) -> List[bool]:
    """
    为六爻标注旬空。
    参数：
        dizhi_list: 六爻地支列表（初至上）
        xunkong: 空亡地支元组，如 ('戌','亥')
    返回：
        布尔列表，True表示该爻旬空。
    """
    return [zhi in xunkong for zhi in dizhi_list]


# ====================== 测试 ======================
if __name__ == '__main__':
    dizhi = ['子', '丑', '寅', '卯', '辰', '巳']
    xk = ('寅', '卯')
    print(mark_xunkong(dizhi, xk))  # [False, False, True, True, False, False]