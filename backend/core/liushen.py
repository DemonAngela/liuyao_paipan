"""
六神排布模块
根据日干确定初爻六神，并循环排布至六爻。
"""

from typing import List

# 六神顺序（固定循环）
LIUSHEN_ORDER = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

# 日干与初爻六神对应表（甲乙→青龙，丙丁→朱雀，戊→勾陈，己→螣蛇，庚辛→白虎，壬癸→玄武）
DAY_GAN_TO_FIRST_LIUSHEN = {
    '甲': '青龙', '乙': '青龙',
    '丙': '朱雀', '丁': '朱雀',
    '戊': '勾陈',
    '己': '螣蛇',
    '庚': '白虎', '辛': '白虎',
    '壬': '玄武', '癸': '玄武'
}


def assign_liushen(day_gan: str) -> List[str]:
    """
    根据日干返回六爻对应的六神列表（索引0为初爻）。
    """
    first = DAY_GAN_TO_FIRST_LIUSHEN[day_gan]
    start_idx = LIUSHEN_ORDER.index(first)
    result = []
    for i in range(6):
        idx = (start_idx + i) % 6
        result.append(LIUSHEN_ORDER[idx])
    return result


# ====================== 测试 ======================
if __name__ == '__main__':
    day_gan = '甲'
    liushen = assign_liushen(day_gan)
    print("六神 (初->上):", liushen)
    # 输出: ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']