"""卦象数据模型定义。"""

import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator


class BianguaYaoDataModel(BaseModel):
    """变爻数据模型。"""

    yin_yang: int
    dizhi: str
    wuxing: str
    liuqin: str
    is_kong: bool = False


class YaoDataModel(BaseModel):
    """爻数据模型。"""

    position: int
    yin_yang: int
    is_changing: bool
    dizhi: str
    wuxing: str
    liuqin: str
    liushen: str
    is_kong: bool
    biangua_yao: Optional[BianguaYaoDataModel] = None
    biangua_info: Optional[BianguaYaoDataModel] = None
    shengke: str = ""
    fushen: Optional[str] = None

    # 日建关系
    ri_zhi: bool = False
    ri_sheng: bool = False
    ri_ke: bool = False
    ri_chong: bool = False
    ri_he: bool = False
    ri_lin: bool = False

    # 月建关系
    yue_zhi: bool = False
    yue_sheng: bool = False
    yue_ke: bool = False
    yue_chong: bool = False
    yue_he: bool = False
    yue_lin: bool = False

    # 动静及破空状态
    is_andong: bool = False
    is_ripo: bool = False
    is_yuepo: bool = False


class GuaDataModel(BaseModel):
    """完整排盘结果模型。"""

    ben_gua_name: str
    bian_gua_name: str
    yao_list: List[YaoDataModel]
    shi_yao: int
    ying_yao: int
    gan_zhi: Dict[str, str]
    xunkong: Tuple[str, str]
    relations: Dict[str, Any]
    special_attr: Optional[str] = None
    bian_special_attr: Optional[str] = None


class ManualYaoResult(BaseModel):
    """单次手动摇卦结果。"""

    yin_yang: Literal[0, 1]
    is_changing: bool


class QiguaRequest(BaseModel):
    """起卦请求模型。

    ``yao_values`` 与 ``changing_yao`` 一旦提供就必须恰好包含六项。
    年月日可全部省略（使用当前日期），但不可只提供其中一部分。
    """

    method: str
    yao_values: Optional[List[Literal[0, 1]]] = Field(
        default=None, min_length=6, max_length=6
    )
    changing_yao: Optional[List[bool]] = Field(
        default=None, min_length=6, max_length=6
    )
    year: Optional[int] = Field(default=None, ge=1, le=9999)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    day: Optional[int] = Field(default=None, ge=1, le=31)
    hour: Optional[int] = Field(default=None, ge=0, le=23)

    @model_validator(mode="after")
    def validate_calendar_date(self):
        date_parts = (self.year, self.month, self.day)
        if any(part is not None for part in date_parts) and not all(
            part is not None for part in date_parts
        ):
            raise ValueError("year、month、day 必须同时提供或同时省略")

        if all(part is not None for part in date_parts):
            dt.datetime(self.year, self.month, self.day, self.hour or 0)
        return self


class QiguaResponse(BaseModel):
    """起卦响应模型。"""

    yao_list: List[Literal[0, 1]] = Field(min_length=6, max_length=6)
    changing_yao: List[bool] = Field(min_length=6, max_length=6)
    timestamp: Dict[str, int]

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: Dict[str, int]) -> Dict[str, int]:
        required = {"year", "month", "day", "hour"}
        if set(value) != required:
            raise ValueError("timestamp 必须且只能包含 year、month、day、hour")

        try:
            dt.datetime(
                value["year"], value["month"], value["day"], value["hour"]
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("timestamp 不是有效的公历时间") from exc
        return value
