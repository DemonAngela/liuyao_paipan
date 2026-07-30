"""纳甲、卦宫和世应查询。

六十四卦元数据以 ``backend/data/64gua_full.json`` 为唯一运行时来源，
避免手写六十四项映射与生成器长期漂移；八个经卦的纳支步长为两位地支。
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

GUA_CODE_MAP = {
    "111": "乾",
    "110": "兑",
    "101": "离",
    "100": "震",
    "011": "巽",
    "010": "坎",
    "001": "艮",
    "000": "坤",
}
GUA_WUXING = {
    "乾": "金",
    "兑": "金",
    "离": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "艮": "土",
    "坤": "土",
}
NAJIA_TABLE = {
    "乾": {"inner_start": "子", "outer_start": "午", "order": "顺"},
    "坎": {"inner_start": "寅", "outer_start": "申", "order": "顺"},
    "震": {"inner_start": "子", "outer_start": "午", "order": "顺"},
    "艮": {"inner_start": "辰", "outer_start": "戌", "order": "顺"},
    "坤": {"inner_start": "未", "outer_start": "丑", "order": "逆"},
    "巽": {"inner_start": "丑", "outer_start": "未", "order": "逆"},
    "离": {"inner_start": "卯", "outer_start": "酉", "order": "逆"},
    "兑": {"inner_start": "巳", "outer_start": "亥", "order": "逆"},
}
DIZHI_ORDER = list("子丑寅卯辰巳午未申酉戌亥")
GUA_DATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "64gua_full.json"
)


def _validate_liuyao(liuyao: Sequence[int]) -> tuple[int, ...]:
    if isinstance(liuyao, (str, bytes)) or len(liuyao) != 6:
        raise ValueError("六爻必须恰好包含六个阴阳值")
    values = tuple(liuyao)
    if any(type(value) is not int or value not in (0, 1) for value in values):
        raise ValueError("阴阳值只能是整数 0 或 1")
    return values


def _gua_code(liuyao: Sequence[int]) -> str:
    return "".join(str(value) for value in _validate_liuyao(liuyao))


@lru_cache(maxsize=1)
def _gua_lookup() -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(GUA_DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法加载六十四卦数据：{GUA_DATA_PATH}") from exc
    if not isinstance(raw, dict) or len(raw) != 64:
        raise RuntimeError("六十四卦数据必须完整包含 64 卦")

    lookup: dict[str, dict[str, Any]] = {}
    for gua in raw.values():
        try:
            code = "".join(
                str(yao["yin_yang"]) for yao in gua["yao_list"]
            )
        except (KeyError, TypeError) as exc:
            raise RuntimeError("六十四卦数据结构无效") from exc
        if len(code) != 6 or set(code) - {"0", "1"} or code in lookup:
            raise RuntimeError("六十四卦阴阳编码无效或重复")
        lookup[code] = gua
    if len(lookup) != 64:
        raise RuntimeError("六十四卦阴阳编码不完整")
    return lookup


def _get_shang_xia_gua(liuyao: Sequence[int]) -> tuple[str, str]:
    values = _validate_liuyao(liuyao)
    xia = GUA_CODE_MAP["".join(str(value) for value in values[:3])]
    shang = GUA_CODE_MAP["".join(str(value) for value in values[3:])]
    return shang, xia


def determine_gua_gong(liuyao: Sequence[int]) -> dict[str, Any]:
    """返回卦名、卦宫、世应位置以及上下卦。"""

    gua = _gua_lookup().get(_gua_code(liuyao))
    if gua is None:
        raise ValueError("未找到匹配的卦象")
    shang, xia = _get_shang_xia_gua(liuyao)
    return {
        "gua_name": gua["name"],
        "gong": gua["gong"],
        "shi_yao": gua["shi"],
        "ying_yao": gua["ying"],
        "shang_gua": shang,
        "xia_gua": xia,
    }


def _trigram_dizhi(
    trigram: str,
    *,
    is_inner: bool,
) -> list[str]:
    config = NAJIA_TABLE[trigram]
    start_key = "inner_start" if is_inner else "outer_start"
    start = DIZHI_ORDER.index(config[start_key])
    step = 2 if config["order"] == "顺" else -2
    return [DIZHI_ORDER[(start + index * step) % 12] for index in range(3)]


def na_dizhi(
    liuyao: Sequence[int],
    gong: str | None = None,
) -> list[str]:
    """按上下经卦纳入初至上爻的六个地支。"""

    base = determine_gua_gong(liuyao)
    if gong is not None and gong != base["gong"]:
        raise ValueError(f"卦宫不匹配：应为{base['gong']}宫")
    shang, xia = base["shang_gua"], base["xia_gua"]
    result = _trigram_dizhi(xia, is_inner=True) + _trigram_dizhi(
        shang,
        is_inner=False,
    )

    expected = [
        yao["dizhi"]
        for yao in _gua_lookup()[_gua_code(liuyao)]["yao_list"]
    ]
    if result != expected:
        raise RuntimeError("纳甲算法与六十四卦数据不一致")
    return result


def install_gua_base(liuyao: Sequence[int]) -> dict[str, Any]:
    """安装卦名、卦宫、世应、上下卦和纳支信息。"""

    base = determine_gua_gong(liuyao)
    base["dizhi_list"] = na_dizhi(liuyao, base["gong"])
    return base
