from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.guaci import GuaciManager
from backend.main import app


def test_guaci_manager_loads_complete_records():
    manager = GuaciManager(Path("backend/data"))

    guaci = manager.load_guaci(1)
    yaoci = manager.load_yaoci(1, 1)

    assert guaci["name"] == "乾为天"
    assert guaci["gua_ci"]
    assert isinstance(yaoci, str) and yaoci


def test_cidian_api_contract_and_path_validation():
    with TestClient(app) as client:
        assert client.get("/api/guaci/1").status_code == 200
        assert client.get("/api/yaoci/1/1").status_code == 200
        assert client.get("/api/guaci/0").status_code == 422
        assert client.get("/api/guaci/65").status_code == 422
        assert client.get("/api/yaoci/1/7").status_code == 422
