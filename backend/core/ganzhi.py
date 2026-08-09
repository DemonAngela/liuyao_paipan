"""干支历法计算。

年柱与月柱使用 ``lunar_python==1.4.8`` 的精确节气交接时刻作为
可复现基准。项目对晚子时采用“民用日期不换日”约定：23:00-23:59
仍使用当日的日柱（lunar-python 的 Exact2 / sect 2 语义），时柱天干
也据此日干计算。

这是一项明确的项目约定，不声称覆盖所有术数流派。
"""

import datetime
from typing import Dict, Tuple, Union

from lunar_python import Solar

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
JIA_ZI = [f"{TIAN_GAN[i % 10]}{DI_ZHI[i % 12]}" for i in range(60)]

XUN_KONG_MAP = {
    "子": ("戌", "亥"),
    "戌": ("申", "酉"),
    "申": ("午", "未"),
    "午": ("辰", "巳"),
    "辰": ("寅", "卯"),
    "寅": ("子", "丑"),
}


def _reference_lunar(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
):
    """返回指定公历时刻对应的 lunar-python Lunar 对象。"""
    return Solar.fromYmdHms(year, month, day, hour, minute, 0).getLunar()


def _year_ganzhi(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
) -> str:
    """按立春精确交接时刻计算年柱。"""
    return _reference_lunar(year, month, day, hour, minute).getYearInGanZhiExact()


def _month_ganzhi(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
) -> str:
    """按每月“节”的精确交接时刻计算月柱。"""
    return _reference_lunar(year, month, day, hour, minute).getMonthInGanZhiExact()


def _day_ganzhi(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
) -> str:
    """计算日柱；晚子时采用民用日期不换日（sect 2）约定。"""
    return _reference_lunar(year, month, day, hour, minute).getDayInGanZhiExact2()


def _hour_ganzhi(hour: int, day_gan: str) -> str:
    """按五鼠遁，以项目所采用的当日日干计算时柱。"""
    if not 0 <= hour <= 23:
        raise ValueError("hour must be between 0 and 23")
    if day_gan not in TIAN_GAN:
        raise ValueError(f"unknown day stem: {day_gan}")

    if hour in (23, 0):
        zhi = "子"
    else:
        zhi = DI_ZHI[((hour + 1) // 2) % 12]

    start_gan_map = {
        "甲": "甲", "己": "甲",
        "乙": "丙", "庚": "丙",
        "丙": "戊", "辛": "戊",
        "丁": "庚", "壬": "庚",
        "戊": "壬", "癸": "壬",
    }
    start_gan_index = TIAN_GAN.index(start_gan_map[day_gan])
    zhi_index = DI_ZHI.index(zhi)
    return TIAN_GAN[(start_gan_index + zhi_index) % 10] + zhi


def get_xunkong(day_ganzhi: str) -> Tuple[str, str]:
    """根据日干支返回旬空（空亡）地支。"""
    try:
        index = JIA_ZI.index(day_ganzhi)
    except ValueError:
        return ("", "")
    xun_shou_zhi = JIA_ZI[(index // 10) * 10][1]
    return XUN_KONG_MAP[xun_shou_zhi]


GanzhiValue = Union[str, Tuple[str, str]]


def get_ganzhi_by_date(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
) -> Dict[str, GanzhiValue]:
    """返回年、月、日、时干支及旬空。

    - 年柱：以立春的精确交接时刻为界。
    - 月柱：以十二“节”的精确交接时刻为界。
    - 日柱：23:00-23:59 不提前换到次日日柱（sect 2）。
    - 时柱：按上述日柱的日干使用五鼠遁。

    REST 起卦接口目前只提供小时粒度，因此会使用 ``minute=0``；Python
    调用方可以显式传入分钟，用于节气边界验证和更精细的排盘工具。
    """
    datetime.datetime(year, month, day, hour, minute)

    year_gz = _year_ganzhi(year, month, day, hour, minute)
    month_gz = _month_ganzhi(year, month, day, hour, minute)
    day_gz = _day_ganzhi(year, month, day, hour, minute)
    hour_gz = _hour_ganzhi(hour, day_gz[0])
    return {
        "year": year_gz,
        "month": month_gz,
        "day": day_gz,
        "hour": hour_gz,
        "xunkong": get_xunkong(day_gz),
    }


def get_current_ganzhi() -> Dict[str, GanzhiValue]:
    """获取当前本机时刻的完整干支信息。"""
    now = datetime.datetime.now()
    return get_ganzhi_by_date(
        now.year, now.month, now.day, now.hour, now.minute
    )
