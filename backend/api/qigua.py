"""四种起卦方式的 API。"""

from __future__ import annotations

import datetime as dt
import secrets
from collections.abc import Callable

from fastapi import APIRouter

from ..core.meihua import qigua_by_datetime
from ..models.gua import (
    ManualYaoResult,
    ManualYaoResults,
    QiguaResponse,
    SpecifyQiguaRequest,
    TimeQiguaRequest,
    TimestampModel,
)

router = APIRouter(prefix="/api/qigua", tags=["起卦"])


def _current_time() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def _generate_random_yao(
    randbelow: Callable[[int], int] = secrets.randbelow,
) -> tuple[int, bool]:
    """模拟三枚铜钱：老阴/少阳/少阴/老阳概率为 1/8、3/8、3/8、1/8。"""

    yang_coins = sum(randbelow(2) for _ in range(3))
    if yang_coins == 0:
        return 0, True
    if yang_coins == 1:
        return 1, False
    if yang_coins == 2:
        return 0, False
    return 1, True


def _response(
    yao_list: list[int],
    changing_yao: list[bool],
    value: dt.datetime,
) -> QiguaResponse:
    return QiguaResponse(
        yao_list=yao_list,
        changing_yao=changing_yao,
        timestamp=TimestampModel.from_datetime(value),
    )


@router.post("/auto", response_model=QiguaResponse)
async def auto_qigua() -> QiguaResponse:
    """电脑自动起卦。"""

    results = [_generate_random_yao() for _ in range(6)]
    return _response(
        [item[0] for item in results],
        [item[1] for item in results],
        _current_time(),
    )


@router.post("/manual_step", response_model=ManualYaoResult)
async def manual_step() -> ManualYaoResult:
    """手动摇卦单步。"""

    yin_yang, is_changing = _generate_random_yao()
    return ManualYaoResult(
        yin_yang=yin_yang,
        is_changing=is_changing,
    )


@router.post("/manual_complete", response_model=QiguaResponse)
async def manual_complete(yao_results: ManualYaoResults) -> QiguaResponse:
    """校验并汇总六次手摇结果。"""

    return _response(
        [item.yin_yang for item in yao_results],
        [item.is_changing for item in yao_results],
        _current_time(),
    )


@router.post("/specify", response_model=QiguaResponse)
async def specify_qigua(request: SpecifyQiguaRequest) -> QiguaResponse:
    """手工指定阴阳、动爻和可选时间。"""

    return _response(
        request.yao_values,
        request.changing_yao,
        request.resolve_datetime(_current_time()),
    )


@router.post("/time", response_model=QiguaResponse)
async def time_qigua(request: TimeQiguaRequest) -> QiguaResponse:
    """按梅花易数年月日时规则起卦。"""

    value = request.resolve_datetime(_current_time())
    yao_list, changing = qigua_by_datetime(value)
    return _response(yao_list, changing, value)
