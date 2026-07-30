"""梅花易数年月日时起卦。"""

from __future__ import annotations

import datetime as dt

from lunar_python import Solar

from .ganzhi import DI_ZHI

NUM_TO_GUA_CODE = {
    1: "111",  # 乾
    2: "110",  # 兑
    3: "101",  # 离
    4: "100",  # 震
    5: "011",  # 巽
    6: "010",  # 坎
    7: "001",  # 艮
    0: "000",  # 坤
}


def qigua_from_numbers(
    year_number: int,
    month_number: int,
    day_number: int,
    hour_number: int,
) -> tuple[list[int], list[bool]]:
    """按原典的年支、农历月日、时支序数起卦。"""

    values = (year_number, month_number, day_number, hour_number)
    if not all(isinstance(value, int) and value > 0 for value in values):
        raise ValueError("年月日时序数必须为正整数")
    upper_sum = year_number + month_number + day_number
    total_sum = upper_sum + hour_number
    upper_code = NUM_TO_GUA_CODE[upper_sum % 8]
    lower_code = NUM_TO_GUA_CODE[total_sum % 8]
    yao_list = [int(value) for value in lower_code + upper_code]
    changing = [False] * 6
    changing[(total_sum - 1) % 6] = True
    return yao_list, changing


def qigua_by_datetime(value: dt.datetime) -> tuple[list[int], list[bool]]:
    """把公历本地时间转换为传统序数后起卦。"""

    solar = Solar.fromYmdHms(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
    )
    lunar = solar.getLunar()
    year_number = DI_ZHI.index(lunar.getYearZhi()) + 1
    month_number = abs(lunar.getMonth())
    day_number = lunar.getDay()
    hour_number = DI_ZHI.index(lunar.getTimeZhi()) + 1
    return qigua_from_numbers(
        year_number,
        month_number,
        day_number,
        hour_number,
    )
