import pytest

from backend import calculate_ganzhi, paipan


def test_python_ganzhi_api():
    result = calculate_ganzhi(1986, 5, 29, 0, 0)
    assert result["year"] == "丙寅"
    assert result["month"] == "癸巳"
    assert result["day"] == "癸酉"
    assert result["hour"] == "壬子"


def test_python_paipan_api_returns_plain_data():
    result = paipan(
        [1, 1, 1, 1, 1, 1],
        year=2026,
        month=4,
        day=23,
        hour=10,
    )
    assert result["ben_gua_name"] == "乾为天"
    assert result["bian_gua_name"] == ""
    assert len(result["yao_list"]) == 6
    assert result["gan_zhi"]["year"] == "丙午"


def test_python_paipan_api_exposes_transformed_hexagram_when_a_line_moves():
    result = paipan(
        [1, 1, 1, 1, 1, 1],
        changing_yao=[True, False, False, False, False, False],
        year=2026,
        month=4,
        day=23,
        hour=10,
    )
    assert result["bian_gua_name"]


def test_python_paipan_api_validates_inputs():
    with pytest.raises(ValueError):
        paipan([1, 1, 1], year=2026, month=4, day=23)

    with pytest.raises(ValueError):
        paipan([1, 1, 1, 1, 1, 2], year=2026, month=4, day=23)
