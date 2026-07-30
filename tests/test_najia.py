import json
from pathlib import Path

import pytest

from backend.core.najia import install_gua_base, na_dizhi
from backend.data.generate_64gua_table import generate_all

DATA_FILE = Path("backend/data/64gua_full.json")


def test_generated_64gua_artifact_is_current():
    actual = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    assert actual == generate_all()
    assert len(actual) == 64


def test_najia_matches_all_64gua_records():
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    for gua in records.values():
        values = [yao["yin_yang"] for yao in gua["yao_list"]]
        result = install_gua_base(values)

        assert result["gua_name"] == gua["name"]
        assert result["gong"] == gua["gong"]
        assert result["shi_yao"] == gua["shi"]
        assert result["ying_yao"] == gua["ying"]
        assert result["dizhi_list"] == [
            yao["dizhi"] for yao in gua["yao_list"]
        ]


@pytest.mark.parametrize(
    "values",
    [
        [1, 1, 1],
        [1, 1, 1, 1, 1, 2],
        [True, 1, 1, 1, 1, 1],
    ],
)
def test_najia_rejects_invalid_yao_values(values):
    with pytest.raises(ValueError):
        install_gua_base(values)


def test_najia_rejects_mismatched_gong():
    with pytest.raises(ValueError, match="卦宫不匹配"):
        na_dizhi([1, 1, 1, 1, 1, 1], "坤")

