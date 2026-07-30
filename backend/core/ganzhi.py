"""精确干支历法适配层。

采用 ``lunar-python`` 的节气时刻和八字实现。项目统一使用本地民用时间，
日柱采用该库的 sect=2 约定：民用午夜换日。
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from lunar_python import Solar

TIAN_GAN = list("甲乙丙丁戊己庚辛壬癸")
DI_ZHI = list("子丑寅卯辰巳午未申酉戌亥")
JIA_ZI = [
    TIAN_GAN[index % 10] + DI_ZHI[index % 12]
    for index in range(60)
]
XUN_KONG_MAP = {
    "子": ("戌", "亥"),
    "戌": ("申", "酉"),
    "申": ("午", "未"),
    "午": ("辰", "巳"),
    "辰": ("寅", "卯"),
    "寅": ("子", "丑"),
}


def _to_datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> dt.datetime:
    """先用标准库验证公历输入，避免底层库产生模糊错误。"""

    return dt.datetime(year, month, day, hour, minute, second)


def _get_eight_char(value: dt.datetime):
    solar = Solar.fromYmdHms(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
    )
    eight_char = solar.getLunar().getEightChar()
    eight_char.setSect(2)
    return eight_char


def _year_ganzhi(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> str:
    return _get_eight_char(
        _to_datetime(year, month, day, hour, minute, second)
    ).getYear()


def _month_ganzhi(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> str:
    return _get_eight_char(
        _to_datetime(year, month, day, hour, minute, second)
    ).getMonth()


def _day_ganzhi(year: int, month: int, day: int) -> str:
    return _get_eight_char(_to_datetime(year, month, day)).getDay()


def _hour_ganzhi(
    hour: int,
    day_gan: str | None = None,
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    minute: int = 0,
    second: int = 0,
) -> str:
    """计算时柱。

    精确模式应传入年月日；仅传 ``day_gan`` 时保留旧公共函数的兼容计算。
    """

    if year is not None and month is not None and day is not None:
        return _get_eight_char(
            _to_datetime(year, month, day, hour, minute, second)
        ).getTime()
    if day_gan not in TIAN_GAN:
        raise ValueError("兼容时柱计算必须提供有效日干")
    zhi_index = ((hour + 1) // 2) % 12
    start_gan_map = {
        "甲": "甲",
        "己": "甲",
        "乙": "丙",
        "庚": "丙",
        "丙": "戊",
        "辛": "戊",
        "丁": "庚",
        "壬": "庚",
        "戊": "壬",
        "癸": "壬",
    }
    gan_index = (TIAN_GAN.index(start_gan_map[day_gan]) + zhi_index) % 10
    return TIAN_GAN[gan_index] + DI_ZHI[zhi_index]


def get_xunkong(day_ganzhi: str) -> tuple[str, str]:
    """根据日干支返回旬空。"""

    try:
        index = JIA_ZI.index(day_ganzhi)
    except ValueError as exc:
        raise ValueError(f"无效日干支：{day_ganzhi}") from exc
    xun_start_zhi = JIA_ZI[(index // 10) * 10][1]
    return XUN_KONG_MAP[xun_start_zhi]


def get_ganzhi_by_date(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> dict[str, Any]:
    """返回指定本地民用时间的年、月、日、时柱和旬空。"""

    value = _to_datetime(year, month, day, hour, minute, second)
    eight_char = _get_eight_char(value)
    day_ganzhi = eight_char.getDay()
    return {
        "year": eight_char.getYear(),
        "month": eight_char.getMonth(),
        "day": day_ganzhi,
        "hour": eight_char.getTime(),
        "xunkong": get_xunkong(day_ganzhi),
    }


def get_current_ganzhi(now: dt.datetime | None = None) -> dict[str, Any]:
    value = (now or dt.datetime.now()).replace(microsecond=0)
    return get_ganzhi_by_date(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
    )
