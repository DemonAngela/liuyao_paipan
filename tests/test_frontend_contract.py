import shutil
import subprocess
from pathlib import Path

import pytest

FRONTEND = Path("frontend")


def test_frontend_javascript_syntax():
    node = shutil.which("node")
    if node is None:
        pytest.skip("未安装 Node.js，跳过 JavaScript 语法检查")

    for script in sorted((FRONTEND / "js").glob("*.js")):
        result = subprocess.run(
            [node, "--check", str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_all_qigua_flows_use_their_backend_contracts():
    qigua = (FRONTEND / "js" / "qigua.js").read_text(encoding="utf-8")
    utils = (FRONTEND / "js" / "utils.js").read_text(encoding="utf-8")

    for endpoint in (
        "/api/qigua/auto",
        "/api/qigua/manual_step",
        "/api/qigua/manual_complete",
        "/api/qigua/specify",
        "/api/qigua/time",
        "/api/paipan/",
    ):
        assert endpoint in qigua
    assert "alert(" not in qigua
    assert "await renderPaipan" not in qigua
    assert "return renderPaipan(paipanData)" in qigua
    assert "response.ok" in utils
    assert qigua.count(
        "'click',\n        handleSpecifySelection"
    ) == 1


def test_frontend_has_no_hardcoded_64gua_mapping():
    config = (FRONTEND / "js" / "config.js").read_text(encoding="utf-8")
    paipan = (FRONTEND / "js" / "paipan.js").read_text(encoding="utf-8")

    assert "GUA_NAME_TO_ID" not in config
    assert "getGuaIdByName" not in paipan
    assert "/api/guaci/name/" in paipan
    assert "/api/yaoci/name/" in paipan


def test_initial_ui_is_hidden_and_accessible():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")

    assert 'id="result-section" class="result-section hidden"' in html
    assert 'id="app-status"' in html
    assert 'aria-live="polite"' in html
    assert 'rel="icon" href="favicon.svg"' in html
    assert '<html lang="zh-CN">' in html
    assert 'for="time-input"' in html
    assert 'for="specify-time-input"' in html
