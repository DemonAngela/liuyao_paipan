import datetime as dt
import json
from pathlib import Path

from lunar_python import Solar

from backend.core.ganzhi import get_ganzhi_by_date


FIXTURE = Path(__file__).parent / "fixtures" / "ganzhi_reference_cases.json"
JIE = [
    "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
    "立秋", "白露", "寒露", "立冬", "大雪", "小寒",
]


def _reference(moment: dt.datetime):
    lunar = Solar.fromYmdHms(
        moment.year,
        moment.month,
        moment.day,
        moment.hour,
        moment.minute,
        moment.second,
    ).getLunar()
    return {
        "year": lunar.getYearInGanZhiExact(),
        "month": lunar.getMonthInGanZhiExact(),
        "day": lunar.getDayInGanZhiExact2(),
    }


def test_fixed_reference_corpus():
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for case in cases:
        moment = dt.datetime.fromisoformat(case["datetime"])
        result = get_ganzhi_by_date(
            moment.year, moment.month, moment.day, moment.hour, moment.minute
        )
        for field, expected in case["expected"].items():
            assert result[field] == expected, f"{case['id']} {field}"


def test_january_cross_year_cases_match_pinned_reference():
    # January is the historical failure area because it belongs to the
    # pre-Lichun year and usually the Chou month.
    for year in range(2020, 2030):
        for day in (1, 15, 31):
            moment = dt.datetime(year, 1, day, 12, 0)
            expected = _reference(moment)
            actual = get_ganzhi_by_date(year, 1, day, 12, 0)
            assert actual["year"] == expected["year"]
            assert actual["month"] == expected["month"]
            assert actual["day"] == expected["day"]


def test_real_jie_transition_minutes_match_reference():
    # The upstream library exposes the computed solar-term instants. Probe one
    # minute on each side so this test protects against reverting to fixed dates.
    for year in (2024, 2025, 2026):
        lunar = Solar.fromYmd(year, 7, 1).getLunar()
        table = lunar.getJieQiTable()
        for name in JIE:
            solar = table[name]
            boundary = dt.datetime(
                solar.getYear(),
                solar.getMonth(),
                solar.getDay(),
                solar.getHour(),
                solar.getMinute(),
                solar.getSecond(),
            )
            for moment in (boundary - dt.timedelta(minutes=1), boundary + dt.timedelta(minutes=1)):
                expected = _reference(moment)
                actual = get_ganzhi_by_date(
                    moment.year,
                    moment.month,
                    moment.day,
                    moment.hour,
                    moment.minute,
                )
                assert actual["year"] == expected["year"], (name, moment)
                assert actual["month"] == expected["month"], (name, moment)


def test_late_zi_hour_uses_same_civil_day_convention():
    moment = dt.datetime(2026, 4, 23, 23, 30)
    lunar = Solar.fromYmdHms(2026, 4, 23, 23, 30, 0).getLunar()
    actual = get_ganzhi_by_date(2026, 4, 23, 23, 30)

    assert actual["day"] == lunar.getDayInGanZhiExact2()
    # lunar-python's Exact variant is the alternative sect-1 convention that
    # advances the day at late Zi hour; this assertion makes our choice explicit.
    assert actual["day"] != lunar.getDayInGanZhiExact()


def test_decade_daily_noon_reference_has_zero_mismatches():
    current = dt.date(2020, 1, 1)
    end = dt.date(2029, 12, 31)
    mismatches = []
    samples = 0

    while current <= end:
        moment = dt.datetime.combine(current, dt.time(12, 0))
        expected = _reference(moment)
        actual = get_ganzhi_by_date(
            current.year, current.month, current.day, 12, 0
        )
        samples += 1
        if any(actual[key] != expected[key] for key in ("year", "month", "day")):
            mismatches.append((current.isoformat(), actual, expected))
        current += dt.timedelta(days=1)

    assert samples == 3653
    assert mismatches == []
