import asyncio

from backend.api import qigua
from backend.models.gua import SpecifyQiguaRequest


def _coin_source(values):
    iterator = iter(values)
    return lambda _n: next(iterator)


def test_three_coin_old_yin():
    assert qigua._generate_random_yao(_coin_source([0, 0, 0])) == (0, True)


def test_three_coin_young_yang():
    assert qigua._generate_random_yao(_coin_source([0, 0, 1])) == (1, False)


def test_three_coin_young_yin():
    assert qigua._generate_random_yao(_coin_source([0, 1, 1])) == (0, False)


def test_three_coin_old_yang():
    assert qigua._generate_random_yao(_coin_source([1, 1, 1])) == (1, True)


def test_specify_defaults_to_static_lines():
    request = SpecifyQiguaRequest(
        yao_values=[1, 0, 1, 0, 1, 0],
        year=2026,
        month=8,
        day=9,
        hour=11,
    )
    response = asyncio.run(qigua.specify_qigua(request))
    assert response.changing_yao == [False] * 6
    assert response.timestamp.year == 2026
    assert response.timestamp.month == 8
    assert response.timestamp.day == 9
    assert response.timestamp.hour == 11
