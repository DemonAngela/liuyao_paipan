import datetime as dt

import pytest
from fastapi.testclient import TestClient

from backend.api import paipan, qigua
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as value:
        yield value


@pytest.mark.parametrize(
    ("coins", "expected"),
    [
        ([0, 0, 0], (0, True)),
        ([1, 0, 0], (1, False)),
        ([1, 1, 0], (0, False)),
        ([1, 1, 1], (1, True)),
    ],
)
def test_three_coin_outcomes(coins, expected):
    values = iter(coins)
    assert qigua._generate_random_yao(lambda _: next(values)) == expected


def test_time_qigua_omitted_time_uses_current_time(client, monkeypatch):
    fixed = dt.datetime(2024, 2, 10, 13, 14, 15)
    monkeypatch.setattr(qigua, "_current_time", lambda: fixed)

    response = client.post("/api/qigua/time", json={})

    assert response.status_code == 200
    assert response.json()["timestamp"] == {
        "year": 2024,
        "month": 2,
        "day": 10,
        "hour": 13,
        "minute": 14,
        "second": 15,
    }


def test_specified_date_defaults_to_midnight(client):
    response = client.post(
        "/api/qigua/specify",
        json={
            "yao_values": [1, 0, 1, 0, 1, 0],
            "year": 2025,
            "month": 3,
            "day": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["changing_yao"] == [False] * 6
    assert body["timestamp"]["hour"] == 0


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        (
            "/api/qigua/specify",
            {"yao_values": [1, 0, 1, 0, 1]},
        ),
        (
            "/api/qigua/specify",
            {"yao_values": [1, 0, 2, 0, 1, 0]},
        ),
        (
            "/api/qigua/specify",
            {"yao_values": [1, 0, 1, 0, 1, 0], "year": 2025},
        ),
        (
            "/api/qigua/time",
            {"year": 2025, "month": 2, "day": 29},
        ),
        (
            "/api/qigua/manual_complete",
            [{"yin_yang": 1, "is_changing": False}] * 5,
        ),
        (
            "/api/qigua/manual_complete",
            [{"yin_yang": "1", "is_changing": False}] * 6,
        ),
    ],
)
def test_invalid_requests_return_422(client, path, payload):
    response = client.post(path, json=payload)

    assert response.status_code == 422


def test_valid_paipan_contract(client):
    response = client.post(
        "/api/paipan/",
        json={
            "yao_list": [1, 1, 1, 1, 1, 1],
            "changing_yao": [False] * 6,
            "timestamp": {
                "year": 2025,
                "month": 3,
                "day": 10,
                "hour": 10,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["ben_gua_name"] == "乾为天"


def test_paipan_hides_internal_exception_details(client, monkeypatch):
    def fail(_):
        raise RuntimeError("sensitive path and state")

    monkeypatch.setattr(paipan.engine, "paipan", fail)
    response = client.post(
        "/api/paipan/",
        json={
            "yao_list": [1, 1, 1, 1, 1, 1],
            "changing_yao": [False] * 6,
            "timestamp": {
                "year": 2025,
                "month": 3,
                "day": 10,
                "hour": 10,
            },
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "排盘失败"}
    assert "sensitive" not in response.text
