"""《增删卜易》规则化解卦辅助。

本模块只输出可由排盘事实触发的规则和候选，不代选用神，也不直接
给出吉凶终局或具体应期日期。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..models.gua import YaoData
from ..utils.constants import (
    DIZHI_WUXING,
    GUA_WUXING,
    LIU_CHONG,
    LIU_HE,
    SHENG_WANG_MU_JUE,
)
from .shengke import (
    WUXING_KE,
    WUXING_SHENG,
    branch_riyue_relations,
)

POSITION_NAMES = {
    1: "初",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "上",
}
TRIGRAM_BY_CODE = {
    "111": "乾",
    "110": "兑",
    "101": "离",
    "100": "震",
    "011": "巽",
    "010": "坎",
    "001": "艮",
    "000": "坤",
}
FANYIN_TRIGRAM = {
    "乾": "巽",
    "巽": "乾",
    "坎": "离",
    "离": "坎",
    "震": "兑",
    "兑": "震",
    "坤": "艮",
    "艮": "坤",
}
LIUHE_PARTNER = {
    "子": "丑",
    "丑": "子",
    "寅": "亥",
    "亥": "寅",
    "卯": "戌",
    "戌": "卯",
    "辰": "酉",
    "酉": "辰",
    "巳": "申",
    "申": "巳",
    "午": "未",
    "未": "午",
}
LIUCHONG_PARTNER = {
    "子": "午",
    "午": "子",
    "丑": "未",
    "未": "丑",
    "寅": "申",
    "申": "寅",
    "卯": "酉",
    "酉": "卯",
    "辰": "戌",
    "戌": "辰",
    "巳": "亥",
    "亥": "巳",
}
JINSHEN_PAIRS = {
    ("亥", "子"),
    ("寅", "卯"),
    ("巳", "午"),
    ("申", "酉"),
    ("丑", "辰"),
    ("辰", "未"),
    ("未", "戌"),
}
TUISHEN_PAIRS = {
    ("子", "亥"),
    ("卯", "寅"),
    ("午", "巳"),
    ("酉", "申"),
    ("辰", "丑"),
    ("未", "辰"),
    ("戌", "未"),
}
ROLE_MAP = {
    "兄弟": {"元神": "父母", "忌神": "官鬼", "仇神": "妻财"},
    "父母": {"元神": "官鬼", "忌神": "妻财", "仇神": "子孙"},
    "官鬼": {"元神": "妻财", "忌神": "子孙", "仇神": "兄弟"},
    "妻财": {"元神": "子孙", "忌神": "兄弟", "仇神": "父母"},
    "子孙": {"元神": "兄弟", "忌神": "父母", "仇神": "官鬼"},
}
ROLE_RELATIONSHIP = {
    "用神": "占问所取的主事六亲",
    "元神": "生用神",
    "忌神": "克用神",
    "仇神": "克元神并生忌神",
}

RULE_TRACES = {
    "ZS-QIN-01": {
        "rule_id": "ZS-QIN-01",
        "category": "装卦",
        "title": "变爻六亲仍从本宫",
        "source": "《增删卜易·动变章第七》",
        "source_text": "变出之爻安六亲者，仍照正卦而推。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/7",
        "confidence": "明确规则",
    },
    "ZS-ANDONG-01": {
        "rule_id": "ZS-ANDONG-01",
        "category": "动静",
        "title": "日冲静爻分暗动与日破",
        "source": "《增删卜易·暗动章第二十二》",
        "source_text": "旺相静爻，日辰冲之为暗动；休囚静爻，日辰冲之为日破。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/22",
        "confidence": "明确规则",
    },
    "ZS-SANHE-01": {
        "rule_id": "ZS-SANHE-01",
        "category": "冲合",
        "title": "内外卦边爻动化成三合",
        "source": "《增删卜易·三合章》",
        "source_text": "内卦初爻、三爻动，或外卦四爻、六爻动，动而变出之爻成三合。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/21",
        "confidence": "明确规则",
    },
    "ZS-YONG-01": {
        "rule_id": "ZS-YONG-01",
        "category": "取用",
        "title": "用神、元神、忌神、仇神",
        "source": "《增删卜易·用神元神忌神仇神章第九》",
        "source_text": "元神生用神；忌神克用神；仇神克元神而生忌神。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/9",
        "confidence": "明确规则",
    },
    "ZS-FUSHEN-01": {
        "rule_id": "ZS-FUSHEN-01",
        "category": "飞伏",
        "title": "伏神须合看飞神与日月",
        "source": "《增删卜易·飞伏神章第二十八》",
        "source_text": (
            "伏神得日月、飞神、动爻生扶，或飞神空破休囚墓绝，"
            "方有得出之机；野鹤另主张用神不现可再占求现。"
        ),
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/28",
        "confidence": "条件提示",
    },
    "ZS-DONG-01": {
        "rule_id": "ZS-DONG-01",
        "category": "动变",
        "title": "变爻回头作用本动爻",
        "source": "《增删卜易·动变生克冲合章》",
        "source_text": "用神自动变出之爻，能生克冲合用神。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/15",
        "confidence": "明确规则",
    },
    "ZS-ACTION-01": {
        "rule_id": "ZS-ACTION-01",
        "category": "生克",
        "title": "动静爻作用边界",
        "source": "《增删卜易·动静生克章第十四、动变生克冲合章第十五》",
        "source_text": (
            "旺相静爻可以生克休囚之爻，动爻亦能生克他爻；"
            "变爻只生克冲合本位动爻。"
        ),
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/14",
        "confidence": "条件提示",
    },
    "ZS-JINTUI-01": {
        "rule_id": "ZS-JINTUI-01",
        "category": "动变",
        "title": "进神退神",
        "source": "《增删卜易·进神退神章第二十九》",
        "source_text": "亥化子、寅化卯、巳化午、申化酉及丑辰未戌顺行为进，逆行为退。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/29",
        "confidence": "明确规则",
    },
    "ZS-HUABIAN-01": {
        "rule_id": "ZS-HUABIAN-01",
        "category": "动变",
        "title": "化空破墓绝与生旺",
        "source": "《增删卜易·生旺墓绝章》",
        "source_text": "用神、元神动化回头生、长生、帝旺为化吉；化回头克、绝、墓、空、退神为化凶。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/26又2",
        "confidence": "条件提示",
    },
    "ZS-FANFU-01": {
        "rule_id": "ZS-FANFU-01",
        "category": "卦体",
        "title": "反吟伏吟",
        "source": "《增删卜易·反伏章第二十五》",
        "source_text": "反吟为卦变、爻变冲克；伏吟为动变后相应区域六爻地支五行不变。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/25",
        "confidence": "明确规则",
    },
    "ZS-GUABIAN-01": {
        "rule_id": "ZS-GUABIAN-01",
        "category": "卦体",
        "title": "卦变生克与特殊卦象",
        "source": "《增删卜易·卦变生克墓绝章第二十四》",
        "source_text": "卦变有变生、变克、变墓、变绝、比和；仍须结合具体占问与用神。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/24",
        "confidence": "条件提示",
    },
    "ZS-YINGQI-01": {
        "rule_id": "ZS-YINGQI-01",
        "category": "应期",
        "title": "应期候选总则",
        "source": "《增删卜易·各门类应期总注》",
        "source_text": "静而逢值逢冲，动而逢合逢值；月破喜填，旬空爱填冲，合者待冲开。",
        "source_url": "https://www.zhonghuashu.com/wiki/增刪卜易/26又3",
        "confidence": "条件提示",
    },
}

TRANSFORMATION_RULE = {
    "回头生": "ZS-DONG-01",
    "回头克": "ZS-DONG-01",
    "化合": "ZS-DONG-01",
    "化冲": "ZS-DONG-01",
    "爻反吟": "ZS-FANFU-01",
    "化进神": "ZS-JINTUI-01",
    "化退神": "ZS-JINTUI-01",
    "化空": "ZS-HUABIAN-01",
    "化破": "ZS-HUABIAN-01",
    "化墓": "ZS-HUABIAN-01",
    "化绝": "ZS-HUABIAN-01",
    "化长生": "ZS-HUABIAN-01",
    "化帝旺": "ZS-HUABIAN-01",
}


def calculate_transformation_relations(
    ben_dizhi: str,
    bian_dizhi: str,
    *,
    xunkong: Sequence[str],
    month_zhi: str,
) -> list[str]:
    """返回一个明动爻可同时成立的全部动化关系。"""

    ben_wuxing = DIZHI_WUXING[ben_dizhi]
    bian_wuxing = DIZHI_WUXING[bian_dizhi]
    result: list[str] = []

    def add(label: str) -> None:
        if label not in result:
            result.append(label)

    if (bian_wuxing, ben_wuxing) in WUXING_SHENG:
        add("回头生")
    if (bian_wuxing, ben_wuxing) in WUXING_KE:
        add("回头克")
    if (ben_dizhi, bian_dizhi) in LIU_HE:
        add("化合")
    if (ben_dizhi, bian_dizhi) in LIU_CHONG:
        add("化冲")
        add("爻反吟")
    if (ben_dizhi, bian_dizhi) in JINSHEN_PAIRS:
        add("化进神")
    if (ben_dizhi, bian_dizhi) in TUISHEN_PAIRS:
        add("化退神")
    if bian_dizhi in xunkong:
        add("化空")
    if (bian_dizhi, month_zhi) in LIU_CHONG:
        add("化破")

    stages = SHENG_WANG_MU_JUE[ben_wuxing]
    stage_labels = {
        "生": "化长生",
        "旺": "化帝旺",
        "墓": "化墓",
        "绝": "化绝",
    }
    for stage, target_zhi in stages.items():
        if bian_dizhi == target_zhi:
            add(stage_labels[stage])
    return result


def _finding(
    category: str,
    title: str,
    detail: str,
    rule_ids: Sequence[str],
    positions: Sequence[int] = (),
) -> dict[str, Any]:
    return {
        "category": category,
        "title": title,
        "detail": detail,
        "positions": list(positions),
        "rule_ids": list(dict.fromkeys(rule_ids)),
    }


def _build_transformation_findings(
    yao_list: Sequence[YaoData],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for yao in yao_list:
        if not yao.is_changing or yao.biangua_info is None:
            continue
        bian = yao.biangua_info
        labels = yao.transformation_relations
        relation_text = "、".join(labels) if labels else "无额外动化标签"
        rule_ids = [
            TRANSFORMATION_RULE[label]
            for label in labels
            if label in TRANSFORMATION_RULE
        ]
        if not rule_ids:
            rule_ids = ["ZS-DONG-01"]
        findings.append(
            _finding(
                "动变",
                f"{POSITION_NAMES[yao.position]}爻动化",
                (
                    f"{yao.liuqin}{yao.dizhi}{yao.wuxing} → "
                    f"{bian.liuqin}{bian.dizhi}{bian.wuxing}；"
                    f"{relation_text}。"
                ),
                rule_ids,
                [yao.position],
            )
        )
    return findings


def _trigram_name(values: Sequence[int]) -> str:
    return TRIGRAM_BY_CODE["".join(str(value) for value in values)]


def _build_fanfu_findings(
    yao_list: Sequence[YaoData],
) -> list[dict[str, Any]]:
    ben_values = [yao.yin_yang for yao in yao_list]
    bian_values = [
        (
            yao.biangua_info.yin_yang
            if yao.biangua_info is not None
            else yao.yin_yang
        )
        for yao in yao_list
    ]
    matches: dict[str, list[tuple[str, str, str, list[int]]]] = {
        "反吟": [],
        "伏吟": [],
    }
    for region, indexes in (
        ("内卦", range(0, 3)),
        ("外卦", range(3, 6)),
    ):
        indexes = list(indexes)
        if not any(yao_list[index].is_changing for index in indexes):
            continue
        ben_trigram = _trigram_name([ben_values[index] for index in indexes])
        bian_trigram = _trigram_name(
            [bian_values[index] for index in indexes]
        )
        positions = [index + 1 for index in indexes]
        if FANYIN_TRIGRAM[ben_trigram] == bian_trigram:
            matches["反吟"].append(
                (region, ben_trigram, bian_trigram, positions)
            )
        if all(
            yao_list[index].biangua_info is not None
            and yao_list[index].dizhi
            == yao_list[index].biangua_info.dizhi
            for index in indexes
        ):
            matches["伏吟"].append(
                (region, ben_trigram, bian_trigram, positions)
            )

    findings: list[dict[str, Any]] = []
    for kind, items in matches.items():
        if not items:
            continue
        title = f"内外卦{kind}" if len(items) == 2 else f"{items[0][0]}{kind}"
        detail = "；".join(
            f"{region}{ben_trigram}变{bian_trigram}"
            for region, ben_trigram, bian_trigram, _ in items
        )
        positions = [
            position
            for _, _, _, item_positions in items
            for position in item_positions
        ]
        findings.append(
            _finding(
                "卦体",
                title,
                f"{detail}；仅标示反复/伏滞结构，须结合用神旺衰。",
                ["ZS-FANFU-01"],
                positions,
            )
        )
    return findings


def _build_structure_findings(
    ben_gua: Mapping[str, Any],
    bian_gua: Mapping[str, Any] | None,
    yao_list: Sequence[YaoData],
    special_attr: str | None,
    bian_special_attr: str | None,
) -> list[dict[str, Any]]:
    findings = _build_fanfu_findings(yao_list)
    ben_name = str(ben_gua["name"])
    if bian_gua is None:
        if special_attr:
            findings.append(
                _finding(
                    "特殊卦",
                    f"本卦{special_attr}",
                    f"{ben_name}为{special_attr}卦；该属性只作卦体参考。",
                    ["ZS-GUABIAN-01"],
                )
            )
        return findings

    bian_name = str(bian_gua["name"])
    ben_label = special_attr or "普通卦"
    bian_label = bian_special_attr or "普通卦"
    if special_attr or bian_special_attr:
        findings.append(
            _finding(
                "特殊卦",
                f"{ben_label}变{bian_label}",
                (
                    f"{ben_name}（{ben_label}）→ "
                    f"{bian_name}（{bian_label}）；"
                    "不脱离用神单独定吉凶。"
                ),
                ["ZS-GUABIAN-01"],
            )
        )

    ben_values = [yao.yin_yang for yao in yao_list]
    bian_values = [
        yao.biangua_info.yin_yang
        if yao.biangua_info is not None
        else yao.yin_yang
        for yao in yao_list
    ]
    ben_lower = _trigram_name(ben_values[:3])
    ben_upper = _trigram_name(ben_values[3:])
    bian_lower = _trigram_name(bian_values[:3])
    bian_upper = _trigram_name(bian_values[3:])
    if ben_lower == ben_upper and bian_lower == bian_upper:
        ben_wuxing = GUA_WUXING[ben_lower]
        bian_wuxing = GUA_WUXING[bian_lower]
        if (bian_wuxing, ben_wuxing) in WUXING_SHENG:
            title = "卦化回头生"
        elif (bian_wuxing, ben_wuxing) in WUXING_KE:
            title = "卦化回头克"
        elif bian_wuxing == ben_wuxing:
            title = "卦化比和"
        else:
            title = "卦体五行变化"
        findings.append(
            _finding(
                "卦体",
                title,
                (
                    f"{ben_lower}{ben_wuxing}变"
                    f"{bian_lower}{bian_wuxing}；"
                    "此为八纯卦卦体关系，仍须核对主事用神。"
                ),
                ["ZS-GUABIAN-01"],
            )
        )
    return findings


def _parse_fushen(value: str | None) -> tuple[str, str, str] | None:
    if not value or len(value) < 4:
        return None
    liuqin, dizhi, wuxing = value[:2], value[2], value[3]
    if liuqin not in ROLE_MAP or DIZHI_WUXING.get(dizhi) != wuxing:
        return None
    return liuqin, dizhi, wuxing


def _candidate_for_yao(yao: YaoData) -> dict[str, Any]:
    if yao.is_changing:
        activity = "明动"
    elif yao.is_andong:
        activity = "暗动"
    else:
        activity = "静"
    statuses = list(
        dict.fromkeys(
            (["旬空"] if yao.is_kong else [])
            + yao.day_relations
            + yao.month_relations
        )
    )
    return {
        "position": yao.position,
        "dizhi": yao.dizhi,
        "wuxing": yao.wuxing,
        "is_hidden": False,
        "activity": activity,
        "statuses": statuses,
    }


def _hidden_candidate(
    yao: YaoData,
    dizhi: str,
    wuxing: str,
    *,
    xunkong: Sequence[str],
    day_zhi: str,
    month_zhi: str,
) -> dict[str, Any]:
    relations = branch_riyue_relations(dizhi, day_zhi, month_zhi)
    statuses = (
        (["旬空"] if dizhi in xunkong else [])
        + relations["day"]
        + relations["month"]
    )
    if (yao.wuxing, wuxing) in WUXING_SHENG:
        statuses.append("飞神生伏")
    if (yao.wuxing, wuxing) in WUXING_KE:
        statuses.append("飞神克伏")
    if yao.is_kong:
        statuses.append("飞神旬空")
    if yao.is_yuepo:
        statuses.append("飞神月破")
    return {
        "position": yao.position,
        "dizhi": dizhi,
        "wuxing": wuxing,
        "is_hidden": True,
        "activity": "伏神",
        "statuses": list(dict.fromkeys(statuses)),
    }


def _timing_hints_for_yao(
    yao: YaoData,
    *,
    day_zhi: str,
    month_zhi: str,
) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()

    def add(trigger: str, branches: Sequence[str], detail: str) -> None:
        unique_branches = list(dict.fromkeys(branches))
        key = (trigger, tuple(unique_branches))
        if key in seen:
            return
        seen.add(key)
        hints.append(
            {
                "trigger": trigger,
                "detail": detail,
                "branches": unique_branches,
                "positions": [yao.position],
                "rule_ids": ["ZS-YINGQI-01"],
            }
        )

    position = POSITION_NAMES[yao.position]
    moving = yao.is_changing or yao.is_andong
    if moving:
        add(
            "动而逢值逢合",
            [yao.dizhi, LIUHE_PARTNER[yao.dizhi]],
            f"{position}爻发动，候值{yao.dizhi}或合{yao.dizhi}之支。",
        )
    else:
        add(
            "静而逢值逢冲",
            [yao.dizhi, LIUCHONG_PARTNER[yao.dizhi]],
            f"{position}爻安静，候值{yao.dizhi}或冲{yao.dizhi}之支。",
        )
    if yao.is_kong:
        add(
            "旬空待填冲",
            [yao.dizhi, LIUCHONG_PARTNER[yao.dizhi]],
            f"{position}爻旬空，列填实与冲空地支。",
        )
    if yao.is_yuepo:
        add(
            "月破待填合",
            [yao.dizhi, LIUHE_PARTNER[yao.dizhi]],
            f"{position}爻月破，列填实与逢合地支。",
        )

    for is_he, partner, source in (
        (yao.ri_he, day_zhi, "日合"),
        (yao.yue_he, month_zhi, "月合"),
    ):
        if is_he:
            add(
                "合待冲开",
                [
                    LIUCHONG_PARTNER[yao.dizhi],
                    LIUCHONG_PARTNER[partner],
                ],
                f"{position}爻受{source}，列冲开双方的地支。",
            )

    if yao.is_changing and yao.biangua_info is not None:
        bian_zhi = yao.biangua_info.dizhi
        add(
            "动爻与变爻",
            [yao.dizhi, bian_zhi],
            f"{position}爻由{yao.dizhi}化{bian_zhi}，两支均列为线索。",
        )
        relations = yao.transformation_relations
        if "化合" in relations:
            add(
                "化合待冲开",
                [
                    LIUCHONG_PARTNER[yao.dizhi],
                    LIUCHONG_PARTNER[bian_zhi],
                ],
                f"{position}爻动而化合，列冲开本支与变支的地支。",
            )
        if "化进神" in relations:
            add(
                "进神逢值逢合",
                [yao.dizhi, LIUHE_PARTNER[yao.dizhi]],
                f"{position}爻化进神，按本支及其六合支列候选。",
            )
        if "化退神" in relations:
            add(
                "退神忌值忌冲",
                [bian_zhi, LIUCHONG_PARTNER[bian_zhi]],
                f"{position}爻化退神，按退后之支及其冲支列候选。",
            )
        if "化墓" in relations:
            add(
                "入墓待冲开",
                [LIUCHONG_PARTNER[bian_zhi]],
                f"{position}爻化墓，列冲开墓支之地支。",
            )
    return hints


def _timing_hints_for_hidden(
    flying_yao: YaoData,
    hidden_dizhi: str,
    *,
    xunkong: Sequence[str],
) -> list[dict[str, Any]]:
    """列出伏神逢值、冲飞及出空候选，不直接判定伏神必然有用。"""

    position = POSITION_NAMES[flying_yao.position]
    hints = [
        {
            "trigger": "伏神得出候选",
            "detail": (
                f"{position}爻下伏神{hidden_dizhi}，候伏神逢值，"
                f"或飞神{flying_yao.dizhi}受冲；仍须合看旺衰生克。"
            ),
            "branches": list(
                dict.fromkeys(
                    [
                        hidden_dizhi,
                        LIUCHONG_PARTNER[flying_yao.dizhi],
                    ]
                )
            ),
            "positions": [flying_yao.position],
            "rule_ids": ["ZS-FUSHEN-01", "ZS-YINGQI-01"],
        }
    ]
    if hidden_dizhi in xunkong:
        hints.append(
            {
                "trigger": "伏神旬空待填冲",
                "detail": (
                    f"{position}爻下伏神{hidden_dizhi}旬空，"
                    "列填实与冲空地支。"
                ),
                "branches": [
                    hidden_dizhi,
                    LIUCHONG_PARTNER[hidden_dizhi],
                ],
                "positions": [flying_yao.position],
                "rule_ids": ["ZS-FUSHEN-01", "ZS-YINGQI-01"],
            }
        )
    return hints


def _source_activity(yao: YaoData) -> str | None:
    if yao.is_changing:
        return "明动"
    if yao.is_andong:
        return "暗动"
    supported = any(
        label in {"值日", "日扶", "日生", "值月", "月扶", "月生"}
        for label in (*yao.day_relations, *yao.month_relations)
    )
    if (
        supported
        and not yao.is_kong
        and not yao.is_ripo
        and not yao.is_yuepo
    ):
        return "得日月扶静"
    return None


def _direct_action_labels(
    source_wuxing: str,
    source_dizhi: str,
    target_wuxing: str,
    target_dizhi: str,
) -> list[str]:
    labels: list[str] = []
    if (source_wuxing, target_wuxing) in WUXING_SHENG:
        labels.append("生")
    elif (source_wuxing, target_wuxing) in WUXING_KE:
        labels.append("克")
    elif source_wuxing == target_wuxing:
        labels.append("比扶")
    if (source_dizhi, target_dizhi) in LIU_HE:
        labels.append("合")
    if (source_dizhi, target_dizhi) in LIU_CHONG:
        labels.append("冲")
    return labels


def _build_action_findings(
    yao_list: Sequence[YaoData],
    yongshen: str,
) -> list[dict[str, Any]]:
    """围绕所选用神列作用候选；变爻跨位作用由设计上排除。"""

    targets: list[tuple[YaoData, str, str, bool]] = [
        (yao, yao.dizhi, yao.wuxing, False)
        for yao in yao_list
        if yao.liuqin == yongshen
    ]
    for flying_yao in yao_list:
        fushen = _parse_fushen(flying_yao.fushen)
        if fushen is not None and fushen[0] == yongshen:
            targets.append((flying_yao, fushen[1], fushen[2], True))

    role_by_liuqin = {
        yongshen: "用神",
        **{
            liuqin: role
            for role, liuqin in ROLE_MAP[yongshen].items()
        },
    }
    findings: list[dict[str, Any]] = []
    for source in yao_list:
        activity = _source_activity(source)
        if activity is None:
            continue
        actions: list[str] = []
        target_positions: list[int] = []
        includes_hidden = False
        for target, target_dizhi, target_wuxing, is_hidden in targets:
            if not is_hidden and source.position == target.position:
                continue
            labels = _direct_action_labels(
                source.wuxing,
                source.dizhi,
                target_wuxing,
                target_dizhi,
            )
            if not labels:
                continue
            place = (
                f"{POSITION_NAMES[target.position]}爻下伏神"
                if is_hidden
                else f"{POSITION_NAMES[target.position]}爻"
            )
            actions.append(
                f"{'、'.join(labels)}{place}{yongshen}{target_dizhi}"
            )
            target_positions.append(target.position)
            includes_hidden = includes_hidden or is_hidden
        if not actions:
            continue
        role = role_by_liuqin.get(source.liuqin, source.liuqin)
        rule_ids = ["ZS-ACTION-01"]
        if includes_hidden:
            rule_ids.append("ZS-FUSHEN-01")
        findings.append(
            _finding(
                "作用链",
                (
                    f"{POSITION_NAMES[source.position]}爻"
                    f"{role}{source.liuqin} · {activity}"
                ),
                (
                    f"{source.dizhi}{source.wuxing}"
                    f"{'；'.join(actions)}。"
                    "此处只列作用候选，效力须再核空破墓绝与日月旺衰。"
                ),
                rule_ids,
                [source.position, *target_positions],
            )
        )
    return findings


def _build_yongshen_profiles(
    yao_list: Sequence[YaoData],
    *,
    xunkong: Sequence[str],
    day_zhi: str,
    month_zhi: str,
) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for yongshen in ROLE_MAP:
        role_qin = {"用神": yongshen, **ROLE_MAP[yongshen]}
        roles: list[dict[str, Any]] = []
        for role in ("用神", "元神", "忌神", "仇神"):
            liuqin = role_qin[role]
            candidates = [
                _candidate_for_yao(yao)
                for yao in yao_list
                if yao.liuqin == liuqin
            ]
            for yao in yao_list:
                fushen = _parse_fushen(yao.fushen)
                if fushen is None or fushen[0] != liuqin:
                    continue
                candidates.append(
                    _hidden_candidate(
                        yao,
                        fushen[1],
                        fushen[2],
                        xunkong=xunkong,
                        day_zhi=day_zhi,
                        month_zhi=month_zhi,
                    )
                )
            roles.append(
                {
                    "role": role,
                    "liuqin": liuqin,
                    "relationship": ROLE_RELATIONSHIP[role],
                    "candidates": candidates,
                }
            )

        visible_yongshen = [
            yao for yao in yao_list if yao.liuqin == yongshen
        ]
        hidden_yongshen = [
            (yao, fushen)
            for yao in yao_list
            if (fushen := _parse_fushen(yao.fushen)) is not None
            and fushen[0] == yongshen
        ]
        timing_hints = [
            hint
            for yao in visible_yongshen
            for hint in _timing_hints_for_yao(
                yao,
                day_zhi=day_zhi,
                month_zhi=month_zhi,
            )
        ]
        timing_hints.extend(
            hint
            for yao, fushen in hidden_yongshen
            for hint in _timing_hints_for_hidden(
                yao,
                fushen[1],
                xunkong=xunkong,
            )
        )
        if visible_yongshen:
            summary = f"本卦见{len(visible_yongshen)}处{yongshen}"
        elif hidden_yongshen:
            summary = (
                f"{yongshen}不上本卦，伏神见{len(hidden_yongshen)}处"
                "；宜核飞伏，必要时再占"
            )
        else:
            summary = f"本卦与伏神均未见{yongshen}"
        rule_ids = ["ZS-YONG-01", "ZS-YINGQI-01"]
        if hidden_yongshen:
            rule_ids.append("ZS-FUSHEN-01")
        action_findings = _build_action_findings(yao_list, yongshen)
        if action_findings:
            rule_ids.append("ZS-ACTION-01")
        profiles[yongshen] = {
            "yongshen": yongshen,
            "summary": summary,
            "roles": roles,
            "action_findings": action_findings,
            "timing_hints": timing_hints,
            "rule_ids": rule_ids,
        }
    return profiles


def build_interpretation(
    *,
    ben_gua: Mapping[str, Any],
    bian_gua: Mapping[str, Any] | None,
    yao_list: Sequence[YaoData],
    ganzhi: Mapping[str, str],
    xunkong: Sequence[str],
    special_attr: str | None,
    bian_special_attr: str | None,
) -> dict[str, Any]:
    """构建可追溯的解卦辅助响应。"""

    day_zhi = ganzhi["day"][1]
    month_zhi = ganzhi["month"][1]
    return {
        "version": "zengshan-v1-experimental",
        "notice": (
            "以下为《增删卜易》规则触发事实与候选线索；"
            "用神取舍、吉凶轻重及年月日时远近仍须结合占问语境。"
        ),
        "transformation_findings": _build_transformation_findings(
            yao_list
        ),
        "structure_findings": _build_structure_findings(
            ben_gua,
            bian_gua,
            yao_list,
            special_attr,
            bian_special_attr,
        ),
        "yongshen_profiles": _build_yongshen_profiles(
            yao_list,
            xunkong=xunkong,
            day_zhi=day_zhi,
            month_zhi=month_zhi,
        ),
        "rule_traces": list(RULE_TRACES.values()),
    }
