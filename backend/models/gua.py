"""排盘领域对象与 API 数据模型。"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

YaoValue: TypeAlias = Literal[0, 1]
YaoValues: TypeAlias = Annotated[list[YaoValue], Field(min_length=6, max_length=6)]
ChangingFlags: TypeAlias = Annotated[list[bool], Field(min_length=6, max_length=6)]
YearValue: TypeAlias = Annotated[int, Field(ge=1900, le=2099)]
MonthValue: TypeAlias = Annotated[int, Field(ge=1, le=12)]
DayValue: TypeAlias = Annotated[int, Field(ge=1, le=31)]
HourValue: TypeAlias = Annotated[int, Field(ge=0, le=23)]
MinuteSecondValue: TypeAlias = Annotated[int, Field(ge=0, le=59)]


class StrictModel(BaseModel):
    """禁止额外字段和隐式类型转换的公共基类。"""

    model_config = ConfigDict(extra="forbid", strict=True)


class TimestampModel(StrictModel):
    """项目统一使用的本地民用时间，不隐式附加时区。"""

    year: YearValue
    month: MonthValue
    day: DayValue
    hour: HourValue
    minute: MinuteSecondValue = 0
    second: MinuteSecondValue = 0

    @model_validator(mode="after")
    def validate_calendar_date(self) -> TimestampModel:
        dt.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
        )
        return self

    @classmethod
    def from_datetime(cls, value: dt.datetime) -> TimestampModel:
        return cls(
            year=value.year,
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
        )

    def to_datetime(self) -> dt.datetime:
        return dt.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
        )


class DateTimeRequest(StrictModel):
    """允许完全省略时间；一旦指定日期，就必须同时给出年月日。"""

    year: YearValue | None = None
    month: MonthValue | None = None
    day: DayValue | None = None
    hour: HourValue | None = None
    minute: MinuteSecondValue | None = None
    second: MinuteSecondValue | None = None

    @model_validator(mode="after")
    def validate_datetime_group(self) -> DateTimeRequest:
        date_values = (self.year, self.month, self.day)
        has_date = any(value is not None for value in date_values)
        if has_date and not all(value is not None for value in date_values):
            raise ValueError("指定时间时必须同时提供 year、month、day")
        if not has_date and any(
            value is not None for value in (self.hour, self.minute, self.second)
        ):
            raise ValueError("不能只提供时分秒而省略年月日")
        if has_date:
            dt.datetime(
                self.year,
                self.month,
                self.day,
                self.hour or 0,
                self.minute or 0,
                self.second or 0,
            )
        return self

    def resolve_datetime(self, now: dt.datetime | None = None) -> dt.datetime:
        if self.year is None:
            return (now or dt.datetime.now()).replace(microsecond=0)
        return dt.datetime(
            self.year,
            self.month,
            self.day,
            self.hour or 0,
            self.minute or 0,
            self.second or 0,
        )


class TimeQiguaRequest(DateTimeRequest):
    method: Literal["time"] = "time"


class SpecifyQiguaRequest(DateTimeRequest):
    method: Literal["specify"] = "specify"
    yao_values: YaoValues
    changing_yao: ChangingFlags = Field(default_factory=lambda: [False] * 6)


QiguaRequest: TypeAlias = TimeQiguaRequest | SpecifyQiguaRequest


class ManualYaoResult(StrictModel):
    yin_yang: YaoValue
    is_changing: bool


ManualYaoResults: TypeAlias = Annotated[
    list[ManualYaoResult], Field(min_length=6, max_length=6)
]


class QiguaResponse(StrictModel):
    """所有起卦方式统一返回的排盘输入。"""

    yao_list: YaoValues
    changing_yao: ChangingFlags
    timestamp: TimestampModel


@dataclass(slots=True)
class BianguaYaoData:
    yin_yang: int
    dizhi: str
    wuxing: str
    liuqin: str
    is_kong: bool = False
    day_relations: list[str] = field(default_factory=list)
    month_relations: list[str] = field(default_factory=list)


@dataclass(slots=True)
class YaoData:
    position: int
    yin_yang: int
    is_changing: bool = False
    dizhi: str = ""
    wuxing: str = ""
    liuqin: str = ""
    liushen: str = ""
    is_kong: bool = False
    biangua_info: BianguaYaoData | None = None
    shengke: str = ""
    fushen: str | None = None
    ri_zhi: bool = False
    ri_sheng: bool = False
    ri_ke: bool = False
    ri_chong: bool = False
    ri_he: bool = False
    yue_zhi: bool = False
    yue_sheng: bool = False
    yue_ke: bool = False
    yue_chong: bool = False
    yue_he: bool = False
    is_andong: bool = False
    is_ripo: bool = False
    is_yuepo: bool = False
    ri_lin: bool = False
    yue_lin: bool = False
    day_relations: list[str] = field(default_factory=list)
    month_relations: list[str] = field(default_factory=list)
    transformation_relations: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GuaData:
    ben_gua_name: str
    bian_gua_name: str
    yao_list: list[YaoData]
    shi_yao: int
    ying_yao: int
    gan_zhi: dict[str, str]
    xunkong: tuple[str, str]
    relations: dict[str, Any]
    analysis: dict[str, Any] | None = None
    special_attr: str | None = None
    bian_special_attr: str | None = None


class AttributeModel(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        from_attributes=True,
    )


class BianguaYaoDataModel(AttributeModel):
    yin_yang: YaoValue
    dizhi: str
    wuxing: str
    liuqin: str
    is_kong: bool = False
    day_relations: list[str] = Field(default_factory=list)
    month_relations: list[str] = Field(default_factory=list)


class YaoDataModel(AttributeModel):
    position: Annotated[int, Field(ge=1, le=6)]
    yin_yang: YaoValue
    is_changing: bool
    dizhi: str
    wuxing: str
    liuqin: str
    liushen: str
    is_kong: bool
    biangua_info: BianguaYaoDataModel | None = None
    shengke: str = ""
    fushen: str | None = None
    ri_zhi: bool = False
    ri_sheng: bool = False
    ri_ke: bool = False
    ri_chong: bool = False
    ri_he: bool = False
    yue_zhi: bool = False
    yue_sheng: bool = False
    yue_ke: bool = False
    yue_chong: bool = False
    yue_he: bool = False
    is_andong: bool = False
    is_ripo: bool = False
    is_yuepo: bool = False
    ri_lin: bool = False
    yue_lin: bool = False
    day_relations: list[str] = Field(default_factory=list)
    month_relations: list[str] = Field(default_factory=list)
    transformation_relations: list[str] = Field(default_factory=list)


class GanZhiModel(StrictModel):
    year: str
    month: str
    day: str
    hour: str


class SanheItemModel(StrictModel):
    pos: Annotated[int, Field(ge=1, le=6)]
    dizhi: str
    is_bian: bool
    src_pos: Annotated[int, Field(ge=1, le=6)] | None = None


class SanheRelationModel(StrictModel):
    wuxing: str
    items: list[SanheItemModel]


class RelationsModel(StrictModel):
    liuhe: list[tuple[str, str, int, int]]
    liuchong: list[tuple[str, str, int, int]]
    sanhe: list[SanheRelationModel]
    shengwangmujue: list[dict[str, str | None]]
    shengwangmujue_details: list[str]


class AnalysisFindingModel(StrictModel):
    category: str
    title: str
    detail: str
    positions: list[Annotated[int, Field(ge=1, le=6)]] = Field(
        default_factory=list
    )
    rule_ids: list[str] = Field(default_factory=list)


class RuleTraceModel(StrictModel):
    rule_id: str
    category: str
    title: str
    source: str
    source_text: str
    source_url: str
    confidence: Literal["明确规则", "条件提示"]


class YongshenCandidateModel(StrictModel):
    position: Annotated[int, Field(ge=1, le=6)]
    dizhi: str
    wuxing: str
    is_hidden: bool
    activity: str
    statuses: list[str] = Field(default_factory=list)


class YongshenRoleModel(StrictModel):
    role: Literal["用神", "元神", "忌神", "仇神"]
    liuqin: str
    relationship: str
    candidates: list[YongshenCandidateModel] = Field(default_factory=list)


class TimingHintModel(StrictModel):
    trigger: str
    detail: str
    branches: list[str]
    positions: list[Annotated[int, Field(ge=1, le=6)]] = Field(
        default_factory=list
    )
    rule_ids: list[str] = Field(default_factory=list)


class YongshenProfileModel(StrictModel):
    yongshen: str
    summary: str
    roles: list[YongshenRoleModel]
    timing_hints: list[TimingHintModel] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)


class InterpretationModel(StrictModel):
    version: str
    notice: str
    transformation_findings: list[AnalysisFindingModel] = Field(
        default_factory=list
    )
    structure_findings: list[AnalysisFindingModel] = Field(
        default_factory=list
    )
    yongshen_profiles: dict[str, YongshenProfileModel]
    rule_traces: list[RuleTraceModel]


class GuaDataModel(AttributeModel):
    """完整排盘响应。"""

    ben_gua_name: str
    bian_gua_name: str
    yao_list: list[YaoDataModel]
    shi_yao: Annotated[int, Field(ge=1, le=6)]
    ying_yao: Annotated[int, Field(ge=1, le=6)]
    gan_zhi: GanZhiModel
    xunkong: tuple[str, str]
    relations: RelationsModel
    analysis: InterpretationModel | None = None
    special_attr: str | None = None
    bian_special_attr: str | None = None
