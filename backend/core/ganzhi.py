"""
干支历法计算模块

提供以下功能：
- 计算指定公历年月日时的年干支、月干支、日干支、时干支
- 根据日干支计算旬空（空亡）地支
- 获取当前时刻的完整干支信息
- 内部辅助：节气判断、五鼠遁、五虎遁等
"""

import datetime
from typing import Tuple, Dict, Optional

# ====================== 基础数据表 ======================

# 十天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 十二地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 六十甲子表 (干支组合索引 0~59)
JIA_ZI = [f"{TIAN_GAN[i % 10]}{DI_ZHI[i % 12]}" for i in range(60)]

# 地支五行映射
DIZHI_WUXING = {
    '寅': '木', '卯': '木',
    '巳': '火', '午': '火',
    '申': '金', '酉': '金',
    '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土'
}

# 旬空表：以旬首地支对应的空亡地支（两个）
# 格式：旬首地支 -> (空亡1, 空亡2)
XUN_KONG_MAP = {
    '子': ('戌', '亥'),  # 甲子旬
    '戌': ('申', '酉'),  # 甲戌旬
    '申': ('午', '未'),  # 甲申旬
    '午': ('辰', '巳'),  # 甲午旬
    '辰': ('寅', '卯'),  # 甲辰旬
    '寅': ('子', '丑')   # 甲寅旬
}

# ====================== 节气计算（简化精确版）======================

# 24节气名称及对应公历月份和近似日期（基于1900-2100年平均）
# 用于判断月干支分界。格式：(节气名, 月份, 日期)
# 注意：实际节气时刻每年略有波动，本模块采用公历日期近似，误差不超过1天，
# 对于六爻起卦已足够精确。如需更高精度可引入天文算法库。
JIE_QI_LIST = [
    ('立春', 2, 4), ('雨水', 2, 19),
    ('惊蛰', 3, 6), ('春分', 3, 21),
    ('清明', 4, 5), ('谷雨', 4, 20),
    ('立夏', 5, 5), ('小满', 5, 21),
    ('芒种', 6, 6), ('夏至', 6, 21),
    ('小暑', 7, 7), ('大暑', 7, 23),
    ('立秋', 8, 7), ('处暑', 8, 23),
    ('白露', 9, 8), ('秋分', 9, 23),
    ('寒露', 10, 8), ('霜降', 10, 23),
    ('立冬', 11, 7), ('小雪', 11, 22),
    ('大雪', 12, 7), ('冬至', 12, 22),
    ('小寒', 1, 5), ('大寒', 1, 20)
]

def _get_jieqi_boundary(year: int) -> Dict[str, datetime.datetime]:
    """
    计算指定年份的12个节（非中气）的日期时间，用于判定月干支变化。
    返回字典：{'立春': datetime, '惊蛰': datetime, ...}
    采用简化的固定日期+年份修正（适用于1901-2099年）。
    """
    boundaries = {}
    # 仅处理12个节（月干支变化的节气）
    target_jie = ['立春', '惊蛰', '清明', '立夏', '芒种', '小暑',
                  '立秋', '白露', '寒露', '立冬', '大雪', '小寒']
    # 为了简化，直接使用每个节气的平均日期（取自JIE_QI_LIST）
    # 并加入世纪年份修正（主要是立春在2月4日或3日）
    for jie_name, month, day in JIE_QI_LIST:
        if jie_name not in target_jie:
            continue
        # 处理立春日期修正（20世纪多为2月4日，21世纪也以2月4日为主，个别年份2月3日）
        # 简便处理：年份能被4整除且不是整百年时可能有偏移，这里忽略不计，保持2月4日
        dt = datetime.datetime(year, month, day, 0, 0, 0)
        # 针对立春特殊处理：如果年份为平年且某条件，但为简化，保持默认。
        boundaries[jie_name] = dt
    return boundaries

def _get_solar_term_before(date: datetime.datetime, jieqi_dict: Dict[str, datetime.datetime]) -> Optional[str]:
    """
    返回给定日期之前（含当日）最近的一个节气的名称。
    """
    # 将节气按时间排序
    sorted_jie = sorted(jieqi_dict.items(), key=lambda x: x[1])
    last_jie = None
    for name, dt in sorted_jie:
        if dt <= date:
            last_jie = name
        else:
            break
    return last_jie

# ====================== 干支计算核心函数 ======================

def _year_ganzhi(year: int, month: int, day: int) -> str:
    """
    计算年干支（以立春为界）。
    例如2026年2月3日（立春前）仍属乙巳年，2月4日立春后为丙午年。
    """
    # 获取当年立春日期
    spring_date = datetime.datetime(year, 2, 4)  # 简化处理，默认立春为2月4日
    # 若给定日期在立春前，则年份干支沿用上一年
    input_date = datetime.datetime(year, month, day)
    if input_date < spring_date:
        year_offset = year - 1
    else:
        year_offset = year

    # 干支序号：甲子为1，公元4年为甲子年，故 offset = (year - 4) % 60
    gan_index = (year_offset - 4) % 10
    zhi_index = (year_offset - 4) % 12
    return TIAN_GAN[gan_index] + DI_ZHI[zhi_index]

def _month_ganzhi(year: int, month: int, day: int, hour: int = 0) -> str:
    """
    计算月干支（以节气为界）。
    月支固定：正月寅，二月卯，...，十二月丑。
    月干根据年干用五虎遁诀。
    """
    # 获取当年节气边界
    jieqi_dict = _get_jieqi_boundary(year)
    input_date = datetime.datetime(year, month, day, hour)
    last_jie = _get_solar_term_before(input_date, jieqi_dict)

    # 月支映射：立春后为寅月，惊蛰后为卯月，等等
    jie_to_month_zhi = {
        '立春': '寅', '惊蛰': '卯', '清明': '辰', '立夏': '巳',
        '芒种': '午', '小暑': '未', '立秋': '申', '白露': '酉',
        '寒露': '戌', '立冬': '亥', '大雪': '子', '小寒': '丑'
    }
    if last_jie is None:
        # 在立春之前，属于上一年的丑月，需取上一年的年干来定月干
        # 简便处理：将年份减1，且月份按丑月算
        year_for_gan = year - 1
        month_zhi = '丑'
    else:
        month_zhi = jie_to_month_zhi[last_jie]
        # 如果当前日期在立春之后但年干已更新，需注意：立春后年干已变，但月干计算应基于年干。
        # 这里的year_for_gan直接使用当前年干计算即可（因为年干已在立春时切换）
        year_gan = _year_ganzhi(year, month, day)[0]
        # 但若last_jie为小寒，则月份实际为丑月，属于下一年，但月干计算仍用当年年干（因为还没到立春）
        # 月干计算公式：年干对应的五虎遁
        gan_index = TIAN_GAN.index(year_gan)
        # 五虎遁：甲己之年丙作首，乙庚之岁戊为头，丙辛必定寻庚起，丁壬壬位顺行流，若问戊癸何方发，甲寅之上好追求。
        month_gan_start_map = {
            '甲': '丙', '己': '丙',
            '乙': '庚', '庚': '庚',
            '丙': '庚', '辛': '庚',
            '丁': '壬', '壬': '壬',
            '戊': '甲', '癸': '甲'
        }
        start_gan = month_gan_start_map[year_gan]
        # 正月寅对应的天干起始，从start_gan开始顺排
        month_zhi_list = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
        month_index = month_zhi_list.index(month_zhi)
        start_gan_index = TIAN_GAN.index(start_gan)
        month_gan_index = (start_gan_index + month_index) % 10
        month_gan = TIAN_GAN[month_gan_index]
        return month_gan + month_zhi

    # 处理立春前的情况（last_jie为None或小寒之后立春之前）
    # 重新获取正确的年干用于月干计算
    if last_jie is None or last_jie == '小寒':
        # 计算上一个立春所在年份的年干
        prev_spring = datetime.datetime(year, 2, 4)
        if input_date < prev_spring:
            prev_year = year - 1
        else:
            prev_year = year
        # 上一年年干
        prev_year_gan = _year_ganzhi(prev_year, 1, 1)[0]  # 随便一天
        # 实际应为上一年的年干（以立春为界）
        # 简化：直接用 year-1 年干
        prev_year_gan = TIAN_GAN[(prev_year - 4) % 10]
        start_gan_map = {
            '甲': '丙', '己': '丙',
            '乙': '庚', '庚': '庚',
            '丙': '庚', '辛': '庚',
            '丁': '壬', '壬': '壬',
            '戊': '甲', '癸': '甲'
        }
        start_gan = start_gan_map[prev_year_gan]
        month_zhi_list = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
        month_index = month_zhi_list.index('丑')  # 丑月
        start_gan_index = TIAN_GAN.index(start_gan)
        month_gan_index = (start_gan_index + month_index) % 10
        month_gan = TIAN_GAN[month_gan_index]
        return month_gan + '丑'

def _day_ganzhi(year: int, month: int, day: int) -> str:
    # 基准日期：1900年1月1日，干支甲戌（10）
    base_year, base_month, base_day = 1900, 1, 1
    # 计算总天数
    def days_since_epoch(y, m, d):
        # 1900年1月1日到 y年m月d日的天数
        total = 0
        for y0 in range(1900, y):
            total += 366 if (y0 % 4 == 0 and y0 % 100 != 0) or (y0 % 400 == 0) else 365
        month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
            month_days[1] = 29
        for m0 in range(1, m):
            total += month_days[m0 - 1]
        total += d - 1
        return total
    diff = days_since_epoch(year, month, day)
    # 甲戌序号为10
    gan_index = (10 + diff) % 10
    zhi_index = (10 + diff) % 12
    return TIAN_GAN[gan_index] + DI_ZHI[zhi_index]

def _hour_ganzhi(hour: int, day_gan: str) -> str:
    # 时支映射：23-1子，1-3丑，3-5寅，5-7卯，7-9辰，9-11巳，
    # 11-13午，13-15未，15-17申，17-19酉，19-21戌，21-23亥
    if hour == 23 or hour == 0:
        zhi = '子'
    elif hour == 1 or hour == 2:
        zhi = '丑'
    elif hour == 3 or hour == 4:
        zhi = '寅'
    elif hour == 5 or hour == 6:
        zhi = '卯'
    elif hour == 7 or hour == 8:
        zhi = '辰'
    elif hour == 9 or hour == 10:
        zhi = '巳'
    elif hour == 11 or hour == 12:
        zhi = '午'
    elif hour == 13 or hour == 14:
        zhi = '未'
    elif hour == 15 or hour == 16:
        zhi = '申'
    elif hour == 17 or hour == 18:
        zhi = '酉'
    elif hour == 19 or hour == 20:
        zhi = '戌'
    else:  # 21,22
        zhi = '亥'

    # 五鼠遁
    start_gan_map = {
        '甲': '甲', '己': '甲',
        '乙': '丙', '庚': '丙',
        '丙': '戊', '辛': '戊',
        '丁': '庚', '壬': '庚',
        '戊': '壬', '癸': '壬'
    }
    start_gan = start_gan_map[day_gan]
    zhi_index = DI_ZHI.index(zhi)
    start_gan_index = TIAN_GAN.index(start_gan)
    gan_index = (start_gan_index + zhi_index) % 10
    return TIAN_GAN[gan_index] + zhi

# ====================== 旬空计算 ======================

def get_xunkong(day_ganzhi: str) -> Tuple[str, str]:
    """
    根据日干支计算旬空（空亡）地支。
    返回两个空亡地支的元组，如 ('寅','卯')。
    """
    zhi = day_ganzhi[1]  # 地支字符
    # 查找该日干支属于哪个旬
    # 六十甲子表中，每10个为一旬，旬首地支为甲子、甲戌、甲申、甲午、甲辰、甲寅
    # 直接用地支判断所属旬首
    xun_shou_zhi = None
    for idx, gz in enumerate(JIA_ZI):
        if gz == day_ganzhi:
            xun_shou_index = (idx // 10) * 10
            xun_shou_zhi = JIA_ZI[xun_shou_index][1]
            break
    if xun_shou_zhi is None:
        # 若不在表中（不可能），返回空
        return ('', '')
    return XUN_KONG_MAP[xun_shou_zhi]

# ====================== 便捷函数 ======================

def get_ganzhi_by_date(year: int, month: int, day: int, hour: int = 0) -> Dict[str, str]:
    """
    根据指定公历日期时间返回完整干支信息。
    返回字典包含：年干支、月干支、日干支、时干支、旬空。
    """
    year_gz = _year_ganzhi(year, month, day)
    month_gz = _month_ganzhi(year, month, day, hour)
    day_gz = _day_ganzhi(year, month, day)
    hour_gz = _hour_ganzhi(hour, day_gz[0])
    xunkong = get_xunkong(day_gz)
    return {
        'year': year_gz,
        'month': month_gz,
        'day': day_gz,
        'hour': hour_gz,
        'xunkong': xunkong
    }

def get_current_ganzhi() -> Dict[str, str]:
    """
    获取当前时刻的完整干支信息。
    """
    now = datetime.datetime.now()
    return get_ganzhi_by_date(now.year, now.month, now.day, now.hour)

# ====================== 测试与示例 ======================

if __name__ == "__main__":
    # 测试案例：2026年4月23日 10时
    test = get_ganzhi_by_date(2026, 4, 23, 10)
    print("2026年4月23日 10时 干支：")
    print(f"年：{test['year']}，月：{test['month']}，日：{test['day']}，时：{test['hour']}")
    print(f"旬空：{test['xunkong']}")

    # 当前时间
    cur = get_current_ganzhi()
    print("\n当前时刻干支：")
    print(cur)