"""六爻排盘核心引擎。

静态卦宫、世应、纳甲与六亲来自已校验的六十四卦数据；运行时只计算
干支、六神、旬空、伏神、动变和生克冲合关系。
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ..models.gua import BianguaYaoData, GuaData, YaoData
from ..utils.constants import (
    DIZHI_WUXING,
    LIU_CHONG,
    LIU_HE,
    SPECIAL_GUA,
)
from .ganzhi import get_ganzhi_by_date
from .liushen import assign_liushen
from .shengke import ShengKeCalculator

ALL_LIUQIN = {"父母", "兄弟", "官鬼", "妻财", "子孙"}
PURE_GUA_NAMES = {
    "乾": "乾为天",
    "兑": "兑为泽",
    "离": "离为火",
    "震": "震为雷",
    "巽": "巽为风",
    "坎": "坎为水",
    "艮": "艮为山",
    "坤": "坤为地",
}
SHENG_SOURCE = {
    "木": "水",
    "火": "木",
    "土": "火",
    "金": "土",
    "水": "金",
}
KE_SOURCE = {
    "木": "金",
    "火": "水",
    "土": "木",
    "金": "火",
    "水": "土",
}


class LiuyaoEngine:
    """使用六十四卦查表数据完成排盘。"""

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or (
            Path(__file__).resolve().parent.parent
            / "data"
            / "64gua_full.json"
        )
        self.gua_dict = self._load_gua_data(self.data_path)
        self._gua_by_code = self._build_code_lookup(self.gua_dict)
        self._gua_by_name = {
            gua["name"]: gua for gua in self.gua_dict.values()
        }
        self.shengke_calc = ShengKeCalculator()

    @staticmethod
    def _load_gua_data(path: Path) -> dict[str, dict[str, Any]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"无法加载六十四卦数据：{path}") from exc
        if not isinstance(data, dict) or len(data) != 64:
            raise RuntimeError("六十四卦数据必须完整包含 64 卦")
        return data

    @classmethod
    def _build_code_lookup(
        cls,
        gua_dict: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, Mapping[str, Any]]:
        lookup: dict[str, Mapping[str, Any]] = {}
        for gua in gua_dict.values():
            try:
                yao_list = gua["yao_list"]
                code = "".join(
                    str(yao["yin_yang"]) for yao in yao_list
                )
            except (KeyError, TypeError) as exc:
                raise RuntimeError("六十四卦数据结构无效") from exc
            if len(code) != 6 or set(code) - {"0", "1"} or code in lookup:
                raise RuntimeError("六十四卦阴阳编码无效或重复")
            lookup[code] = gua
        if len(lookup) != 64:
            raise RuntimeError("六十四卦阴阳编码不完整")
        return lookup

    @staticmethod
    def _validate_yao_list(values: object) -> list[int]:
        if (
            not isinstance(values, Sequence)
            or isinstance(values, (str, bytes))
            or len(values) != 6
        ):
            raise ValueError("yao_list 必须恰好包含六个阴阳值")
        result = list(values)
        if any(type(value) is not int or value not in (0, 1) for value in result):
            raise ValueError("yao_list 只能包含整数 0 或 1")
        return result

    @staticmethod
    def _validate_changing_flags(values: object) -> list[bool]:
        if (
            not isinstance(values, Sequence)
            or isinstance(values, (str, bytes))
            or len(values) != 6
        ):
            raise ValueError("changing_yao 必须恰好包含六个标志")
        result = list(values)
        if any(type(value) is not bool for value in result):
            raise ValueError("changing_yao 只能包含布尔值")
        return result

    @staticmethod
    def _required_int(
        source: Mapping[str, object],
        key: str,
        default: int | None = None,
    ) -> int:
        value = source.get(key, default)
        if type(value) is not int:
            raise ValueError(f"{key} 必须是整数")
        return value

    def _find_gua_by_yao_list(
        self,
        yao_list: Sequence[int],
    ) -> Mapping[str, Any]:
        code = "".join(str(value) for value in yao_list)
        try:
            return self._gua_by_code[code]
        except KeyError as exc:
            raise ValueError(f"未找到匹配的卦象：{code}") from exc

    def _find_gong_gua(self, gong_name: str) -> Mapping[str, Any]:
        try:
            return self._gua_by_name[PURE_GUA_NAMES[gong_name]]
        except KeyError as exc:
            raise ValueError(f"未找到{gong_name}宫本宫卦") from exc

    @staticmethod
    def _get_fushen_for_yao(
        ben_yao: Mapping[str, Any],
        ben_gua: Mapping[str, Any],
        ben_gong_gua: Mapping[str, Any],
    ) -> str | None:
        present = {
            yao["liuqin"].strip() for yao in ben_gua["yao_list"]
        }
        missing = ALL_LIUQIN - present
        if not missing:
            return None
        gong_yao = ben_gong_gua["yao_list"][ben_yao["pos"] - 1]
        gong_liuqin = gong_yao["liuqin"].strip()
        if gong_liuqin not in missing:
            return None
        gong_dizhi = gong_yao["dizhi"]
        return f"{gong_liuqin}{gong_dizhi}{DIZHI_WUXING[gong_dizhi]}"

    def paipan(self, qigua_result: Mapping[str, object]) -> GuaData:
        """校验起卦输入并返回完整排盘对象。"""

        yao_values = self._validate_yao_list(
            qigua_result.get("yao_list")
        )
        changing_flags = self._validate_changing_flags(
            qigua_result.get("changing_yao", [False] * 6)
        )
        year = self._required_int(qigua_result, "year")
        month = self._required_int(qigua_result, "month")
        day = self._required_int(qigua_result, "day")
        hour = self._required_int(qigua_result, "hour", 0)
        minute = self._required_int(qigua_result, "minute", 0)
        second = self._required_int(qigua_result, "second", 0)

        full_ganzhi = get_ganzhi_by_date(
            year,
            month,
            day,
            hour,
            minute,
            second,
        )
        xunkong = full_ganzhi["xunkong"]
        ganzhi = {
            key: full_ganzhi[key]
            for key in ("year", "month", "day", "hour")
        }
        day_gan = ganzhi["day"][0]

        bian_values = [
            1 - value if changing_flags[index] else value
            for index, value in enumerate(yao_values)
        ]
        ben_gua = self._find_gua_by_yao_list(yao_values)
        bian_gua = self._find_gua_by_yao_list(bian_values)
        has_biangua = any(changing_flags)
        ben_gong_gua = self._find_gong_gua(ben_gua["gong"])
        liushen_list = assign_liushen(day_gan)

        yao_data_list = [
            self._build_yao_data(
                index=index,
                ben_gua=ben_gua,
                bian_gua=bian_gua,
                ben_gong_gua=ben_gong_gua,
                changing_flags=changing_flags,
                has_biangua=has_biangua,
                liushen=liushen_list[index],
                xunkong=xunkong,
                ganzhi=ganzhi,
            )
            for index in range(6)
        ]
        relations = self.shengke_calc.calc_all_relations_from_yao_list(
            yao_data_list,
            ganzhi["day"],
            ganzhi["month"],
        )
        ben_name = ben_gua["name"]
        bian_name = bian_gua["name"] if has_biangua else ""
        return GuaData(
            ben_gua_name=ben_name,
            bian_gua_name=bian_name,
            yao_list=yao_data_list,
            shi_yao=ben_gua["shi"],
            ying_yao=ben_gua["ying"],
            gan_zhi=ganzhi,
            xunkong=xunkong,
            relations=relations,
            special_attr=SPECIAL_GUA.get(ben_name),
            bian_special_attr=(
                SPECIAL_GUA.get(bian_name) if has_biangua else None
            ),
        )

    def _build_yao_data(
        self,
        *,
        index: int,
        ben_gua: Mapping[str, Any],
        bian_gua: Mapping[str, Any],
        ben_gong_gua: Mapping[str, Any],
        changing_flags: Sequence[bool],
        has_biangua: bool,
        liushen: str,
        xunkong: tuple[str, str],
        ganzhi: Mapping[str, str],
    ) -> YaoData:
        ben_yao = ben_gua["yao_list"][index]
        bian_yao = bian_gua["yao_list"][index]
        ben_dizhi = ben_yao["dizhi"]
        bian_dizhi = bian_yao["dizhi"]
        is_changing = changing_flags[index]
        biangua_info = (
            BianguaYaoData(
                yin_yang=bian_yao["yin_yang"],
                dizhi=bian_dizhi,
                wuxing=DIZHI_WUXING[bian_dizhi],
                liuqin=bian_yao["liuqin"],
                is_kong=bian_dizhi in xunkong,
            )
            if has_biangua
            else None
        )
        yao = YaoData(
            position=index + 1,
            yin_yang=ben_yao["yin_yang"],
            is_changing=is_changing,
            dizhi=ben_dizhi,
            wuxing=DIZHI_WUXING[ben_dizhi],
            liuqin=ben_yao["liuqin"],
            liushen=liushen,
            is_kong=ben_dizhi in xunkong,
            biangua_info=biangua_info,
            shengke=(
                self._calc_dongbian_relation(
                    ben_dizhi,
                    DIZHI_WUXING[ben_dizhi],
                    bian_dizhi,
                    DIZHI_WUXING[bian_dizhi],
                )
                if is_changing
                else ""
            ),
            fushen=self._get_fushen_for_yao(
                ben_yao,
                ben_gua,
                ben_gong_gua,
            ),
        )
        self.shengke_calc.calc_riyue_status(
            yao,
            ganzhi["day"],
            ganzhi["month"],
        )
        return yao

    @staticmethod
    def _calc_dongbian_relation(
        ben_dizhi: str,
        ben_wuxing: str,
        bian_dizhi: str,
        bian_wuxing: str,
    ) -> str:
        if (ben_dizhi, bian_dizhi) in LIU_HE:
            return "化合"
        if (ben_dizhi, bian_dizhi) in LIU_CHONG:
            return "化冲"
        if bian_wuxing == SHENG_SOURCE[ben_wuxing]:
            return "回头生"
        if bian_wuxing == KE_SOURCE[ben_wuxing]:
            return "回头克"
        return ""
