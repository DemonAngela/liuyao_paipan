"""
排盘 API 路由
"""

from fastapi import APIRouter, HTTPException
from ..models.gua import GuaDataModel, QiguaResponse
from ..core.liuyao_engine import LiuyaoEngine

router = APIRouter(prefix="/api/paipan", tags=["排盘"])

engine = LiuyaoEngine()


@router.post("/", response_model=GuaDataModel)
async def paipan(qigua_response: QiguaResponse):
    """
    根据起卦结果进行完整排盘
    """
    try:
        qigua_dict = {
            "yao_list": qigua_response.yao_list,
            "changing_yao": qigua_response.changing_yao,
            "year": qigua_response.timestamp["year"],
            "month": qigua_response.timestamp["month"],
            "day": qigua_response.timestamp["day"],
            "hour": qigua_response.timestamp["hour"]
        }
        result = engine.paipan(qigua_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排盘失败: {str(e)}")