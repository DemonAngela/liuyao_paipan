"""排盘 API。"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..core.liuyao_engine import LiuyaoEngine
from ..models.gua import GuaDataModel, QiguaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/paipan", tags=["排盘"])
engine = LiuyaoEngine()


@router.post("/", response_model=GuaDataModel)
async def paipan(qigua_response: QiguaResponse):
    """根据已校验的起卦结果进行完整排盘。"""

    timestamp = qigua_response.timestamp
    try:
        return engine.paipan(
            {
                "yao_list": qigua_response.yao_list,
                "changing_yao": qigua_response.changing_yao,
                "year": timestamp.year,
                "month": timestamp.month,
                "day": timestamp.day,
                "hour": timestamp.hour,
                "minute": timestamp.minute,
                "second": timestamp.second,
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="排盘数据无效") from exc
    except Exception as exc:
        logger.exception("排盘失败")
        raise HTTPException(status_code=500, detail="排盘失败") from exc
