"""排盘 API 路由。"""

import logging

from fastapi import APIRouter, HTTPException

from ..core.liuyao_engine import LiuyaoEngine
from ..models.gua import GuaDataModel, QiguaResponse

router = APIRouter(prefix="/api/paipan", tags=["排盘"])
logger = logging.getLogger(__name__)
engine = LiuyaoEngine()


@router.post("/", response_model=GuaDataModel)
async def paipan(qigua_response: QiguaResponse):
    """根据已校验的起卦结果进行完整排盘。"""

    try:
        qigua_dict = {
            "yao_list": qigua_response.yao_list,
            "changing_yao": qigua_response.changing_yao,
            "year": qigua_response.timestamp["year"],
            "month": qigua_response.timestamp["month"],
            "day": qigua_response.timestamp["day"],
            "hour": qigua_response.timestamp["hour"],
        }
        return engine.paipan(qigua_dict)
    except Exception as exc:
        logger.exception("排盘引擎执行失败")
        raise HTTPException(
            status_code=500,
            detail="排盘失败，请检查输入或联系维护者。",
        ) from exc
