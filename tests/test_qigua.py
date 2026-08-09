import asyncio

from backend.api import qigua
from backend.models.gua import QiguaRequest


def _patch_coin_values(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr(qigua.random, "randint", lambda _a, _b: next(iterator))


def test_three_coin_old_yin(monkeypatch):
    _patch_coin_values(monkeypatch, [2, 2, 2])
    assert qigua._generate_random_yao() == (0, True)


def test_three_coin_young_yang(monkeypatch):
    _patch_coin_values(monkeypatch, [2, 2, 3])
    assert qigua._generate_random_yao() == (1, False)


def test_three_coin_young_yin(monkeypatch):
    _patch_coin_values(monkeypatch, [2, 3, 3])
    assert qigua._generate_random_yao() == (0, False)


def test_three_coin_old_yang(monkeypatch):
    _patch_coin_values(monkeypatch, [3, 3, 3])
    assert qigua._generate_random_yao() == (1, True)


def test_specify_defaults_to_static_lines():
    request = QiguaRequest(
        method="specify",
        yao_values=[1, 0, 1, 0, 1, 0],
        year=2026,
        month=8,
        day=9,
        hour=11,
    )
    response = asyncio.run(qigua.specify_qigua(request))
    assert response.changing_yao == [False] * 6
    assert response.timestamp == {"year": 2026, "month": 8, "day": 9, "hour": 11}
