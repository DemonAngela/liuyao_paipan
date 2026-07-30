from backend.core.interpretation import (
    calculate_transformation_relations,
)
from backend.core.liuyao_engine import LiuyaoEngine
from backend.models.gua import GuaDataModel


def gua_values(engine: LiuyaoEngine, name: str) -> list[int]:
    gua = next(
        item for item in engine.gua_dict.values() if item["name"] == name
    )
    return [yao["yin_yang"] for yao in gua["yao_list"]]


def paipan_from_names(
    engine: LiuyaoEngine,
    ben_name: str,
    bian_name: str | None = None,
):
    ben_values = gua_values(engine, ben_name)
    bian_values = (
        gua_values(engine, bian_name) if bian_name else ben_values
    )
    return engine.paipan(
        {
            "yao_list": ben_values,
            "changing_yao": [
                ben != bian
                for ben, bian in zip(
                    ben_values,
                    bian_values,
                    strict=True,
                )
            ],
            "year": 2025,
            "month": 3,
            "day": 1,
            "hour": 10,
            "minute": 0,
            "second": 0,
        }
    )


def test_changed_liuqin_uses_original_palace_and_schema_is_valid():
    engine = LiuyaoEngine()

    result = paipan_from_names(engine, "水天需", "天水讼")

    assert [
        yao.biangua_info.liuqin
        for yao in result.yao_list
        if yao.biangua_info is not None
    ] == ["官鬼", "兄弟", "父母", "父母", "子孙", "兄弟"]
    model = GuaDataModel.model_validate(result)
    assert model.analysis is not None
    assert model.analysis.version == "zengshan-v1-experimental"


def test_transformation_keeps_all_simultaneous_relations():
    labels = calculate_transformation_relations(
        "子",
        "丑",
        xunkong=("子", "丑"),
        month_zhi="未",
    )

    assert labels == ["回头克", "化合", "化空", "化破"]

    progress = calculate_transformation_relations(
        "申",
        "酉",
        xunkong=("戌", "亥"),
        month_zhi="卯",
    )
    assert "化进神" in progress
    assert "化帝旺" in progress


def test_yongshen_profile_maps_four_roles_and_timing_rules():
    result = paipan_from_names(LiuyaoEngine(), "水天需", "天水讼")
    profile = result.analysis["yongshen_profiles"]["妻财"]
    roles = {
        item["role"]: item["liuqin"] for item in profile["roles"]
    }

    assert roles == {
        "用神": "妻财",
        "元神": "子孙",
        "忌神": "兄弟",
        "仇神": "父母",
    }
    assert profile["timing_hints"]
    assert all(
        hint["rule_ids"] == ["ZS-YINGQI-01"]
        and hint["branches"]
        for hint in profile["timing_hints"]
    )


def test_hidden_god_is_included_in_yongshen_candidates():
    result = paipan_from_names(LiuyaoEngine(), "天山遁")
    profile = result.analysis["yongshen_profiles"]["子孙"]
    yongshen_role = next(
        role for role in profile["roles"] if role["role"] == "用神"
    )

    assert profile["summary"] == "子孙不上本卦，伏神见1处"
    assert any(
        candidate["is_hidden"]
        and candidate["position"] == 1
        and candidate["dizhi"] == "子"
        for candidate in yongshen_role["candidates"]
    )


def test_fanyin_fuyin_and_special_transition_are_explained():
    engine = LiuyaoEngine()
    fanyin = paipan_from_names(engine, "乾为天", "巽为风")
    fuyin = paipan_from_names(engine, "乾为天", "震为雷")
    special = paipan_from_names(engine, "乾为天", "天地否")

    assert "内外卦反吟" in {
        item["title"] for item in fanyin.analysis["structure_findings"]
    }
    assert "内外卦伏吟" in {
        item["title"] for item in fuyin.analysis["structure_findings"]
    }
    assert "六冲变六合" in {
        item["title"] for item in special.analysis["structure_findings"]
    }


def test_rule_traces_have_unique_ids_and_sources():
    result = paipan_from_names(LiuyaoEngine(), "水天需")
    traces = result.analysis["rule_traces"]
    rule_ids = [trace["rule_id"] for trace in traces]

    assert len(rule_ids) == len(set(rule_ids))
    assert {"ZS-QIN-01", "ZS-YONG-01", "ZS-YINGQI-01"} <= set(
        rule_ids
    )
    assert all(
        trace["source"].startswith("《增删卜易")
        and trace["source_url"].startswith("https://")
        for trace in traces
    )
