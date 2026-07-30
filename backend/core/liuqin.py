"""
六亲配置模块（修正版）
严格按照：地支五行与卦宫五行生克关系定六亲
"""

from typing import List

# 地支五行
DIZHI_WUXING = {
    '寅': '木', '卯': '木',
    '巳': '火', '午': '火',
    '申': '金', '酉': '金',
    '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土'
}

# 八卦五行
GUA_WUXING = {
    '乾': '金', '兑': '金',
    '离': '火',
    '震': '木', '巽': '木',
    '坎': '水',
    '艮': '土', '坤': '土'
}


def assign_liuqin(gong: str, dizhi_list: List[str]) -> List[str]:
    """
    分配六亲
    同我者为兄弟，生我者为父母，我生者为子孙，我克者为妻财，克我者为官鬼
    """
    gong_wuxing = GUA_WUXING[gong]
    result = []
    for zhi in dizhi_list:
        yao_wuxing = DIZHI_WUXING[zhi]

        if gong_wuxing == yao_wuxing:
            liuqin = '兄弟'
        elif (gong_wuxing, yao_wuxing) in [('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')]:
            liuqin = '子孙'  # 我生
        elif (gong_wuxing, yao_wuxing) in [('木', '土'), ('火', '金'), ('土', '水'), ('金', '木'), ('水', '火')]:
            liuqin = '妻财'  # 我克
        elif (yao_wuxing, gong_wuxing) in [('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')]:
            liuqin = '父母'  # 生我
        elif (yao_wuxing, gong_wuxing) in [('木', '土'), ('火', '金'), ('土', '水'), ('金', '木'), ('水', '火')]:
            liuqin = '官鬼'  # 克我
        else:
            raise ValueError(f"无法判断：宫{gong_wuxing} 爻{yao_wuxing}")

        result.append(liuqin)
    return result


if __name__ == '__main__':
    # 测试天风姤（乾宫金）地支：初丑、二亥、三酉、四午、五申、上戌
    test = ['丑', '亥', '酉', '午', '申', '戌']
    print(assign_liuqin('乾', test))
    # 应输出：['父母', '子孙', '兄弟', '官鬼', '兄弟', '父母']