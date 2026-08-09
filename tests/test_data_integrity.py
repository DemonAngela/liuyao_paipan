import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"


def _load_json(name):
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_full_hexagram_table_contains_64_hexagrams_and_384_lines():
    data = _load_json("64gua_full.json")
    assert set(data) == {str(i) for i in range(1, 65)}

    line_count = 0
    for gua in data.values():
        assert gua["name"]
        assert gua["gong"]
        assert 1 <= gua["shi"] <= 6
        assert 1 <= gua["ying"] <= 6
        assert len(gua["yao_list"]) == 6
        assert [yao["pos"] for yao in gua["yao_list"]] == [1, 2, 3, 4, 5, 6]
        assert all(yao["yin_yang"] in (0, 1) for yao in gua["yao_list"])
        assert all(yao["dizhi"] for yao in gua["yao_list"])
        assert all(yao["liuqin"] for yao in gua["yao_list"])
        line_count += len(gua["yao_list"])

    assert line_count == 384


def test_line_text_table_contains_384_entries():
    data = _load_json("yaoci.json")
    assert set(data) == {str(i) for i in range(1, 65)}
    assert sum(len(lines) for lines in data.values()) == 384
    for lines in data.values():
        assert set(lines) == {str(i) for i in range(1, 7)}
        assert all(text.strip() for text in lines.values())


def test_hexagram_text_table_contains_all_64_hexagrams():
    data = _load_json("64gua.json")
    assert set(data) == {str(i) for i in range(1, 65)}
