"""六爻生克、冲合与生旺墓绝计算。

冲合展示采用项目统一口径：六合、六冲至少有一爻明动或暗动；三合按
“三本支至少两动”及内外卦首尾爻动化参与两类组合识别。流派存在差异，
因此这里明确描述程序口径，不把该筛选规则宣称为唯一古法。
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations
from typing import Any

from ..models.gua import GuaData, YaoData
from ..utils.constants import (
    DIZHI_WUXING,
    LIU_CHONG,
    LIU_HE,
    SAN_HE,
    SHENG_WANG_MU_JUE,
)

WUXING_SHENG = {
    ("木", "火"),
    ("火", "土"),
    ("土", "金"),
    ("金", "水"),
    ("水", "木"),
}
WUXING_KE = {
    ("木", "土"),
    ("火", "金"),
    ("土", "水"),
    ("金", "木"),
    ("水", "火"),
}
SANHE_ORDER = {
    "水": ("申", "子", "辰"),
    "金": ("巳", "酉", "丑"),
    "火": ("寅", "午", "戌"),
    "木": ("亥", "卯", "未"),
}
STATE_LABELS = {
    "生": "长生",
    "旺": "帝旺",
    "墓": "墓",
    "绝": "绝",
}
POSITION_NAMES = {
    1: "初",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "上",
}


class ShengKeCalculator:
    """计算排盘结果中的动态关系。"""

    @staticmethod
    def _is_liuhe(zhi1: str, zhi2: str) -> bool:
        return (zhi1, zhi2) in LIU_HE

    @staticmethod
    def _is_liuchong(zhi1: str, zhi2: str) -> bool:
        return (zhi1, zhi2) in LIU_CHONG

    @staticmethod
    def _is_moving(yao: YaoData) -> bool:
        return yao.is_changing or yao.is_andong

    def find_liuhe(
        self,
        yao_list: Sequence[YaoData],
    ) -> list[tuple[str, str, int, int]]:
        """返回至少一爻发动的六合关系。"""

        result = []
        for yao1, yao2 in combinations(yao_list, 2):
            if not (self._is_moving(yao1) or self._is_moving(yao2)):
                continue
            if self._is_liuhe(yao1.dizhi, yao2.dizhi):
                result.append(
                    (
                        yao1.dizhi,
                        yao2.dizhi,
                        yao1.position,
                        yao2.position,
                    )
                )
        return result

    def find_liuchong(
        self,
        yao_list: Sequence[YaoData],
    ) -> list[tuple[str, str, int, int]]:
        """返回至少一爻发动的六冲关系。"""

        result = []
        for yao1, yao2 in combinations(yao_list, 2):
            if not (self._is_moving(yao1) or self._is_moving(yao2)):
                continue
            if self._is_liuchong(yao1.dizhi, yao2.dizhi):
                result.append(
                    (
                        yao1.dizhi,
                        yao2.dizhi,
                        yao1.position,
                        yao2.position,
                    )
                )
        return result

    @staticmethod
    def _match_sanhe(zhis: Sequence[str]) -> str | None:
        if len(zhis) != 3:
            return None
        zhi_set = set(zhis)
        return next(
            (
                wuxing
                for wuxing, expected in SAN_HE.items()
                if zhi_set == expected
            ),
            None,
        )

    @staticmethod
    def _ordered_sanhe_items(
        wuxing: str,
        candidates: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        by_zhi = {item["dizhi"]: item for item in candidates}
        return [by_zhi[zhi] for zhi in SANHE_ORDER[wuxing]]

    def find_sanhe(self, yao_list: Sequence[YaoData]) -> list[dict[str, Any]]:
        """按项目口径返回三合局及参与的本爻、变爻信息。"""

        if len(yao_list) != 6:
            raise ValueError("三合计算需要六个爻")

        results: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()

        for selected in combinations(yao_list, 3):
            wuxing = self._match_sanhe([yao.dizhi for yao in selected])
            if wuxing is None:
                continue
            if sum(self._is_moving(yao) for yao in selected) < 2:
                continue
            key = ("本支", wuxing, *(yao.position for yao in selected))
            if key in seen:
                continue
            seen.add(key)
            candidates = [
                {
                    "pos": yao.position,
                    "dizhi": yao.dizhi,
                    "is_bian": False,
                }
                for yao in selected
            ]
            results.append(
                {
                    "wuxing": wuxing,
                    "items": self._ordered_sanhe_items(
                        wuxing,
                        candidates,
                    ),
                }
            )

        for first_pos, second_pos in ((1, 3), (4, 6)):
            for moving_pos, static_pos in (
                (first_pos, second_pos),
                (second_pos, first_pos),
            ):
                moving = yao_list[moving_pos - 1]
                static = yao_list[static_pos - 1]
                if not moving.is_changing or moving.biangua_info is None:
                    continue
                candidates = [
                    {
                        "pos": moving.position,
                        "dizhi": moving.dizhi,
                        "is_bian": False,
                    },
                    {
                        "pos": moving.position,
                        "dizhi": moving.biangua_info.dizhi,
                        "is_bian": True,
                        "src_pos": moving.position,
                    },
                    {
                        "pos": static.position,
                        "dizhi": static.dizhi,
                        "is_bian": False,
                    },
                ]
                wuxing = self._match_sanhe(
                    [item["dizhi"] for item in candidates]
                )
                if wuxing is None:
                    continue
                key = (
                    "动化",
                    wuxing,
                    moving.position,
                    static.position,
                )
                if key in seen:
                    continue
                seen.add(key)
                results.append(
                    {
                        "wuxing": wuxing,
                        "items": self._ordered_sanhe_items(
                            wuxing,
                            candidates,
                        ),
                    }
                )

        return results

    @staticmethod
    def _extract_zhi(ganzhi: str, label: str) -> str:
        if (
            not isinstance(ganzhi, str)
            or len(ganzhi) != 2
            or ganzhi[1] not in DIZHI_WUXING
        ):
            raise ValueError(f"{label}必须是有效干支")
        return ganzhi[1]

    def calc_shengwangmujue_for_yao(
        self,
        yao_wuxing: str,
        yao_dizhi: str,
        ri_ganzhi: str,
        yue_ganzhi: str,
    ) -> dict[str, str | None]:
        """计算一个爻在日建、月建下触发的长生、帝旺、墓、绝。"""

        if yao_dizhi not in DIZHI_WUXING:
            raise ValueError("爻地支无效")
        ri_zhi = self._extract_zhi(ri_ganzhi, "日干支")
        yue_zhi = self._extract_zhi(yue_ganzhi, "月干支")
        table = SHENG_WANG_MU_JUE.get(yao_wuxing)
        if table is None:
            return {"日建": None, "月建": None}

        def state_at(zhi: str) -> str | None:
            return next(
                (
                    STATE_LABELS[state]
                    for state, target in table.items()
                    if target == zhi
                ),
                None,
            )

        return {
            "日建": state_at(ri_zhi),
            "月建": state_at(yue_zhi),
        }

    def calc_all_relations(self, gua_data: GuaData) -> dict[str, Any]:
        """从完整排盘对象计算所有关系，保留原公共入口。"""

        try:
            day_ganzhi = gua_data.gan_zhi["day"]
            month_ganzhi = gua_data.gan_zhi["month"]
        except (AttributeError, KeyError, TypeError) as exc:
            raise ValueError("排盘对象缺少日月干支") from exc
        return self.calc_all_relations_from_yao_list(
            gua_data.yao_list,
            day_ganzhi,
            month_ganzhi,
        )

    def calc_all_relations_from_yao_list(
        self,
        yao_list: Sequence[YaoData],
        day_ganzhi: str,
        month_ganzhi: str,
    ) -> dict[str, Any]:
        """从六爻列表和日月干支计算前端所需的完整关系结构。"""

        if len(yao_list) != 6:
            raise ValueError("关系计算需要六个爻")
        return {
            "liuhe": self.find_liuhe(yao_list),
            "liuchong": self.find_liuchong(yao_list),
            "sanhe": self.find_sanhe(yao_list),
            "shengwangmujue": [
                self.calc_shengwangmujue_for_yao(
                    yao.wuxing,
                    yao.dizhi,
                    day_ganzhi,
                    month_ganzhi,
                )
                for yao in yao_list
            ],
            "shengwangmujue_details": (
                self.calc_shengwangmujue_details(
                    yao_list,
                    day_ganzhi,
                    month_ganzhi,
                )
            ),
        }

    def calc_shengwangmujue_details(
        self,
        yao_list: Sequence[YaoData],
        day_ganzhi: str,
        month_ganzhi: str | None = None,
    ) -> list[str]:
        """返回日建、月建、动爻和动化触发的生旺墓绝说明。"""

        day_zhi = self._extract_zhi(day_ganzhi, "日干支")
        month_zhi = (
            self._extract_zhi(month_ganzhi, "月干支")
            if month_ganzhi is not None
            else None
        )
        results: list[str] = []
        seen: set[str] = set()

        def add(message: str) -> None:
            if message not in seen:
                seen.add(message)
                results.append(message)

        for yao in yao_list:
            table = SHENG_WANG_MU_JUE.get(yao.wuxing)
            if table is None:
                continue
            prefix = (
                f"[{POSITION_NAMES[yao.position]}爻"
                f"{yao.dizhi}{yao.wuxing}]"
            )
            for state, target_zhi in table.items():
                label = STATE_LABELS[state]
                if day_zhi == target_zhi:
                    add(
                        f"{prefix}{label}在{target_zhi}"
                        f"[日建{day_zhi}{DIZHI_WUXING[day_zhi]}]"
                    )
                if month_zhi == target_zhi:
                    add(
                        f"{prefix}{label}在{target_zhi}"
                        f"[月建{month_zhi}{DIZHI_WUXING[month_zhi]}]"
                    )
                for other in yao_list:
                    if other is yao or not self._is_moving(other):
                        continue
                    if other.dizhi == target_zhi:
                        add(
                            f"{prefix}{label}在{target_zhi}"
                            f"[{POSITION_NAMES[other.position]}爻"
                            f"{other.dizhi}{other.wuxing}]"
                        )
                if (
                    yao.is_changing
                    and yao.biangua_info is not None
                    and yao.biangua_info.dizhi == target_zhi
                ):
                    bian_zhi = yao.biangua_info.dizhi
                    add(
                        f"{prefix}{label}在{target_zhi}"
                        f"[变爻{bian_zhi}{DIZHI_WUXING[bian_zhi]}]"
                    )

        return results

    @staticmethod
    def _is_wang_single(yao_wuxing: str, yue_zhi: str) -> bool:
        """兼容旧入口：判断爻是否受月建同类或生扶。"""

        if yue_zhi not in DIZHI_WUXING:
            raise ValueError("月支无效")
        yue_wuxing = DIZHI_WUXING[yue_zhi]
        return (
            yao_wuxing == yue_wuxing
            or (yue_wuxing, yao_wuxing) in WUXING_SHENG
        )

    def calc_riyue_status(
        self,
        yao: YaoData,
        ri_ganzhi: str,
        yue_ganzhi: str,
    ) -> None:
        """就项目口径为一个爻写入日月关系、暗动和日月破标志。"""

        ri_zhi = self._extract_zhi(ri_ganzhi, "日干支")
        yue_zhi = self._extract_zhi(yue_ganzhi, "月干支")
        if yao.dizhi not in DIZHI_WUXING:
            raise ValueError("爻地支无效")

        ri_wuxing = DIZHI_WUXING[ri_zhi]
        yue_wuxing = DIZHI_WUXING[yue_zhi]

        yao.ri_zhi = yao.dizhi == ri_zhi
        yao.ri_lin = ri_wuxing == yao.wuxing and not yao.ri_zhi
        yao.ri_he = self._is_liuhe(yao.dizhi, ri_zhi)
        yao.ri_chong = self._is_liuchong(yao.dizhi, ri_zhi)
        yao.ri_sheng = (ri_wuxing, yao.wuxing) in WUXING_SHENG
        yao.ri_ke = (ri_wuxing, yao.wuxing) in WUXING_KE

        yao.yue_zhi = yao.dizhi == yue_zhi
        yao.yue_lin = yue_wuxing == yao.wuxing and not yao.yue_zhi
        yao.yue_he = self._is_liuhe(yao.dizhi, yue_zhi)
        yao.yue_chong = self._is_liuchong(yao.dizhi, yue_zhi)
        yao.yue_sheng = (yue_wuxing, yao.wuxing) in WUXING_SHENG
        yao.yue_ke = (yue_wuxing, yao.wuxing) in WUXING_KE
        yao.is_yuepo = yao.yue_chong

        yao.is_andong = False
        yao.is_ripo = False
        if not yao.is_changing and yao.ri_chong:
            month_supported = self._is_wang_single(
                yao.wuxing,
                yue_zhi,
            )
            if not yao.is_yuepo and month_supported:
                yao.is_andong = True
            else:
                yao.is_ripo = True
