"""历法查询请求与响应模型。"""

from .gua import StrictModel, TimestampModel


class GanzhiQueryRequest(TimestampModel):
    """自定义本地日期时间查询。"""


class GanzhiSummaryResponse(StrictModel):
    """干支、公历和农历摘要。"""

    ganzhi: str
    solar: str
    lunar: str
