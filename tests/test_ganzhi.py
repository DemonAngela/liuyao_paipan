import pytest

from backend.core.ganzhi import get_ganzhi_by_date, get_xunkong


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

