from pathlib import Path


def test_one_click_script_keeps_uvicorn_in_its_console():
    script = Path("liuyao_start&stop.bat").read_text(encoding="ascii")

    assert 'start "Liuyao backend" /B' in script
    assert "-m uvicorn backend.main:app" in script
    assert "/healthz" in script
    assert "Keep this CMD window open" in script
    assert 'if /i not "%~1"=="/no-browser"' in script
    assert "server.ps1" not in script
