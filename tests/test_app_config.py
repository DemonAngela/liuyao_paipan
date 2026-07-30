import pytest
from fastapi.testclient import TestClient

from backend.main import create_app


def test_default_app_is_same_origin_without_cors_wildcard():
    with TestClient(create_app(cors_origins=[])) as client:
        health = client.get("/healthz")
        preflight = client.options(
            "/api/qigua/auto",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert health.json() == {"status": "ok"}
    assert "access-control-allow-origin" not in preflight.headers


def test_explicit_cors_allowlist_only_allows_configured_origin():
    application = create_app(cors_origins=["https://trusted.example"])
    with TestClient(application) as client:
        trusted = client.options(
            "/api/qigua/auto",
            headers={
                "Origin": "https://trusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )
        untrusted = client.options(
            "/api/qigua/auto",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert trusted.status_code == 200
    assert (
        trusted.headers["access-control-allow-origin"]
        == "https://trusted.example"
    )
    assert "access-control-allow-origin" not in untrusted.headers


def test_cors_wildcard_is_rejected():
    with pytest.raises(ValueError, match="通配符"):
        create_app(cors_origins=["*"])
