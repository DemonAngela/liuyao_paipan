"""起卦 API 路由。"""

import datetime
import random
from typing import List, Tuple

from fastapi import APIRouter, HTTPException

from ..models.gua import ManualYaoResult, QiguaRequest, QiguaResponse

router = APIRouter(prefix="/api/qigua", tags=["起卦"])


def _generate_random_yao() -> Tuple[int, bool]:
    """模拟三枚铜钱生成一爻。

    每枚铜钱取 2/3，和值 6/7/8/9 分别对应老阴、少阳、少阴、老阳；
    因而动爻总概率为 1/4。
    """

    total = sum(random.randint(2, 3) for _ in range(3))
    if total == 6:  # 老阴：1/8
        return 0, True
    if total == 7:  # 少阳：3/8
        return 1, False
    if total == 8:  # 少阴：3/8
        return 0, False
    return 1, True  # 老阳：1/8


def _resolve_datetime(request: QiguaRequest) -> datetime.datetime:
    """把可选请求时间解析为完整且有效的本地公历时间。"""

    now = datetime.datetime.now()
    year = request.year if request.year is not None else now.year
    month = request.month if request.month is not None else now.month
    day = request.day if request.day is not None else now.day
    hour = request.hour if request.hour is not None else now.hour
    return datetime.datetime(year, month, day, hour)


@router.post("/auto", response_model=QiguaResponse)
async def auto_qigua():
    """电脑自动起卦：按三枚铜钱概率生成六爻。"""

    yao_list = []
    changing = []
    for _ in range(6):
        yin_yang, is_change = _generate_random_yao()
        yao_list.append(yin_yang)
        changing.append(is_change)

    now = datetime.datetime.now()
    return QiguaResponse(
        yao_list=yao_list,
        changing_yao=changing,
        timestamp={
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
        },
    )


@router.post("/manual_step", response_model=ManualYaoResult)
async def manual_step():
    """手动摇卦单步：返回一爻的随机结果。"""

    yin_yang, is_change = _generate_random_yao()
    return ManualYaoResult(yin_yang=yin_yang, is_changing=is_change)


@router.post("/manual_complete", response_model=QiguaResponse)
async def manual_complete(yao_results: List[ManualYaoResult]):
    """手动摇卦完成：接收且仅接收六个合法爻结果。"""

    if len(yao_results) != 6:
        raise HTTPException(status_code=400, detail="必须提供6爻数据")

    now = datetime.datetime.now()
    return QiguaResponse(
        yao_list=[item.yin_yang for item in yao_results],
        changing_yao=[item.is_changing for item in yao_results],
        timestamp={
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
        },
    )


@router.post("/specify", response_model=QiguaResponse)
async def specify_qigua(request: QiguaRequest):
    """手工指定起卦。"""

    if request.yao_values is None:
        raise HTTPException(status_code=400, detail="必须提供6个阴阳值")

    changing = request.changing_yao or [False] * 6
    resolved = _resolve_datetime(request)

    return QiguaResponse(
        yao_list=request.yao_values,
        changing_yao=changing,
        timestamp={
            "year": resolved.year,
            "month": resolved.month,
            "day": resolved.day,
            "hour": resolved.hour,
        },
    )


@router.post("/time", response_model=QiguaResponse)
async def time_qigua(request: QiguaRequest):
    """实验性的时间起卦。

    当前实现仍使用公历年月日时的简化数字取余算法，并非完整的传统
    梅花易数年月日时起例。该限制在 README 与 CODE_REVIEW.md 中公开记录。
    """

    resolved = _resolve_datetime(request)
    year, month, day, hour = (
        resolved.year,
        resolved.month,
        resolved.day,
        resolved.hour,
    )

    # 实验性简化算法：公历数字求和取余。
    sum_shang = year + month + day
    sum_xia = year + month + day + hour
    shang_gua_num = sum_shang % 8
    xia_gua_num = sum_xia % 8
    dong_yao_num = sum_xia % 6

    num_to_gua_code = {
        1: "111",  # 乾
        2: "110",  # 兑
        3: "101",  # 离
        4: "100",  # 震
        5: "011",  # 巽
        6: "010",  # 坎
        7: "001",  # 艮
        0: "000",  # 坤
    }
    shang_code = num_to_gua_code[shang_gua_num]
    xia_code = num_to_gua_code[xia_gua_num]
    full_code = xia_code + shang_code
    yao_list = [int(c) for c in full_code]

    changing = [False] * 6
    changing[5 if dong_yao_num == 0 else dong_yao_num - 1] = True

    return QiguaResponse(
        yao_list=yao_list,
        changing_yao=changing,
        timestamp={"year": year, "month": month, "day": day, "hour": hour},
    )
