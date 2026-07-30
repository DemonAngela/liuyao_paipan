"""卦辞、爻辞数据访问。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GuaciManager:
    """启动时校验并缓存卦辞、爻辞 JSON 数据。"""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self._guaci = self._load_json("64gua.json")
        self._yaoci = self._load_json("yaoci.json")
        if len(self._guaci) != 64 or len(self._yaoci) != 64:
            raise RuntimeError("卦辞和爻辞数据必须各自完整包含 64 卦")

    def _load_json(self, filename: str) -> dict[str, Any]:
        path = self.data_dir / filename
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"无法加载辞典数据：{path}") from exc
        if not isinstance(data, dict):
            raise RuntimeError(f"辞典数据根节点必须是对象：{path}")
        return data

    @staticmethod
    def _validate_gua_id(gua_id: int) -> str:
        if type(gua_id) is not int or not 1 <= gua_id <= 64:
            raise ValueError("卦序必须是 1 至 64 的整数")
        return str(gua_id)

    def load_guaci(self, gua_id: int) -> dict[str, str]:
        """返回指定卦的卦名、卦辞、彖辞和象辞。"""

        key = self._validate_gua_id(gua_id)
        try:
            item = self._guaci[key]
        except KeyError as exc:
            raise KeyError("卦不存在") from exc
        if not isinstance(item, dict):
            raise RuntimeError(f"第 {gua_id} 卦辞数据结构无效")
        fields = ("name", "gua_ci", "tuan_ci", "xiang_ci")
        result = {field: item.get(field, "") for field in fields}
        if any(not isinstance(value, str) for value in result.values()):
            raise RuntimeError(f"第 {gua_id} 卦辞字段类型无效")
        return result

    def load_yaoci(self, gua_id: int, yao_pos: int) -> str:
        """返回指定卦初至上爻中的一条爻辞。"""

        key = self._validate_gua_id(gua_id)
        if type(yao_pos) is not int or not 1 <= yao_pos <= 6:
            raise ValueError("爻位必须是 1 至 6 的整数")
        try:
            gua = self._yaoci[key]
        except KeyError as exc:
            raise KeyError("卦不存在") from exc
        if not isinstance(gua, dict):
            raise RuntimeError(f"第 {gua_id} 卦爻辞数据结构无效")
        try:
            value = gua[str(yao_pos)]
        except KeyError as exc:
            raise KeyError("爻位不存在") from exc
        if not isinstance(value, str):
            raise RuntimeError(f"第 {gua_id} 卦第 {yao_pos} 爻辞类型无效")
        return value
