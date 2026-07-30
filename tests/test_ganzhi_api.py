import datetime as dt

from fastapi.testclient import TestClient

from backend.api import ganzhi
from backend.main import app


def test_today_ganzhi_api_uses_server_local_date(monkeypatch):
    monkeypatch.setattr(
        ganzhi,
        "_current_time",
        lambda: dt.datetime(2026, 7, 30, 12, 0, 0),
    )

    with TestClient(app) as client:
        response = client.get("/api/ganzhi/today")

    assert response.status_code == 200
    assert response.json() == {
        "ganzhi": "丙午年 乙未月 乙巳日",
        "solar": "2026年7月30日 星期四",
        "lunar": "二零二六年 六月(大) 十七",
    }


def test_custom_ganzhi_api_returns_selected_time_and_hour_pillar():
    with TestClient(app) as client:
        response = client.post(
            "/api/ganzhi/query",
            json={
                "year": 2026,
                "month": 7,
                "day": 21,
                "hour": 23,
                "minute": 30,
                "second": 0,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "ganzhi": "丙午年 乙未月 丙申日 庚子时",
        "solar": "2026年7月21日 23:30 星期二",
        "lunar": "二零二六年 六月(大) 初八",
    }


def test_custom_ganzhi_api_rejects_invalid_calendar_date():
    with TestClient(app) as client:
        response = client.post(
            "/api/ganzhi/query",
            json={
                "year": 2026,
                "month": 2,
                "day": 29,
                "hour": 12,
            },
        )

    assert response.status_code == 422
