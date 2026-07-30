"""干支历查询 API。"""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter

from ..core.ganzhi import get_calendar_summary
from ..models.calendar import GanzhiQueryRequest, GanzhiSummaryResponse

router = APIRouter(prefix="/api/ganzhi", tags=["干支查询"])


def _current_time() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


@router.get("/today", response_model=GanzhiSummaryResponse)
async def get_today_ganzhi() -> GanzhiSummaryResponse:
    """返回服务器本地日期的今日干支、公历和农历。"""

    return GanzhiSummaryResponse(**get_calendar_summary(_current_time()))


@router.post("/query", response_model=GanzhiSummaryResponse)
async def query_ganzhi(request: GanzhiQueryRequest) -> GanzhiSummaryResponse:
    """返回指定本地日期时间的四柱干支、公历和农历。"""

    return GanzhiSummaryResponse(
        **get_calendar_summary(request.to_datetime(), include_time=True)
    )
