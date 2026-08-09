from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_openapi_is_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/qigua/specify" in schema["paths"]
    assert "/api/paipan/" in schema["paths"]


def test_specify_endpoint_accepts_reproducible_six_line_input():
    response = client.post(
        "/api/qigua/specify",
        json={
            "method": "specify",
            "yao_values": [1, 1, 1, 1, 1, 1],
            "changing_yao": [False, False, False, False, False, False],
            "year": 2026,
            "month": 8,
            "day": 9,
            "hour": 12,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["yao_list"] == [1, 1, 1, 1, 1, 1]
    assert data["changing_yao"] == [False] * 6
    assert data["timestamp"] == {"year": 2026, "month": 8, "day": 9, "hour": 12}


def test_specify_endpoint_rejects_invalid_line_count():
    response = client.post(
        "/api/qigua/specify",
        json={
            "method": "specify",
            "yao_values": [1, 1, 1, 1, 1],
            "changing_yao": [False] * 6,
        },
    )

    assert response.status_code == 422


def test_manual_complete_rejects_incomplete_hexagram():
    response = client.post(
        "/api/qigua/manual_complete",
        json=[{"yin_yang": 1, "is_changing": False}] * 5,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "必须提供6爻数据"


def test_paipan_endpoint_returns_structured_result():
    response = client.post(
        "/api/paipan/",
        json={
            "yao_list": [1, 1, 1, 1, 1, 1],
            "changing_yao": [False, False, False, False, False, False],
            "timestamp": {"year": 2026, "month": 8, "day": 9, "hour": 12},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ben_gua_name"]
    assert len(data["yao_list"]) == 6
    assert data["shi_yao"] in range(1, 7)
    assert data["ying_yao"] in range(1, 7)
