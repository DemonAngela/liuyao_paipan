import datetime as dt

import pytest

from backend.core.ganzhi import (
    get_calendar_summary,
    get_ganzhi_by_date,
    get_xunkong,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            (1900, 1, 1, 0, 0, 0),
            {
                "year": "己亥",
                "month": "丙子",
                "day": "甲戌",
                "hour": "甲子",
                "xunkong": ("申", "酉"),
            },
        ),
        (
            (2020, 2, 10, 12, 0, 0),
            {
                "year": "庚子",
                "month": "戊寅",
                "day": "癸未",
                "hour": "戊午",
                "xunkong": ("申", "酉"),
            },
        ),
        (
            (2025, 3, 10, 10, 0, 0),
            {
                "year": "乙巳",
                "month": "己卯",
                "day": "戊寅",
                "hour": "丁巳",
                "xunkong": ("申", "酉"),
            },
        ),
        (
            (2026, 7, 30, 12, 0, 0),
            {
                "year": "丙午",
                "month": "乙未",
                "day": "乙巳",
                "hour": "壬午",
                "xunkong": ("寅", "卯"),
            },
        ),
    ],
)
def test_ganzhi_authoritative_samples(value, expected):
    assert get_ganzhi_by_date(*value) == expected


def test_lichun_uses_exact_solar_term_time():
    before = get_ganzhi_by_date(2025, 2, 3, 22, 10, 27)
    after = get_ganzhi_by_date(2025, 2, 3, 22, 10, 28)

    assert (before["year"], before["month"]) == ("甲辰", "丁丑")
    assert (after["year"], after["month"]) == ("乙巳", "戊寅")


def test_invalid_calendar_and_xunkong_inputs_are_rejected():
    with pytest.raises(ValueError):
        get_ganzhi_by_date(2025, 2, 29)
    with pytest.raises(ValueError, match="无效日干支"):
        get_xunkong("甲甲")


def test_calendar_summary_matches_reference_sample():
    value = dt.datetime(2026, 7, 21, 12, 0, 0)

    assert get_calendar_summary(value) == {
        "ganzhi": "丙午年 乙未月 丙申日",
        "solar": "2026年7月21日 星期二",
        "lunar": "二零二六年 六月(大) 初八",
    }


def test_calendar_summary_includes_selected_time_and_hour_pillar():
    value = dt.datetime(2026, 7, 21, 23, 30, 0)

    assert get_calendar_summary(value, include_time=True) == {
        "ganzhi": "丙午年 乙未月 丙申日 庚子时",
        "solar": "2026年7月21日 23:30 星期二",
        "lunar": "二零二六年 六月(大) 初八",
    }
