"""
起卦 API 路由
提供多种起卦方式
"""

import random
import datetime
from typing import List, Tuple
from fastapi import APIRouter, HTTPException
from ..models.gua import QiguaRequest, QiguaResponse

router = APIRouter(prefix="/api/qigua", tags=["起卦"])


def _generate_random_yao() -> Tuple[int, bool]:
    """
    生成随机一爻
    返回 (阴阳, 是否动爻)
    老阳(3)为阳动，老阴(2)为阴动，少阳(1)为阳静，少阴(0)为阴静
    概率：动爻约1/4
    """
    r = random.randint(0, 5)
    if r == 0:        # 老阴 (1/6)
        return 0, True
    elif r == 1:      # 少阳 (1/6)
        return 1, False
    elif r == 2:      # 少阴 (1/6)
        return 0, False
    elif r == 3:      # 老阳 (1/6)
        return 1, True
    elif r == 4:      # 少阳 (额外)
        return 1, False
    else:             # 少阴 (额外)
        return 0, False


@router.post("/auto", response_model=QiguaResponse)
async def auto_qigua():
    """电脑自动起卦：随机生成6爻，含动爻"""
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
        timestamp={"year": now.year, "month": now.month, "day": now.day, "hour": now.hour}
    )


@router.post("/manual_step", response_model=dict)
async def manual_step():
    """手动摇卦单步：返回一爻的随机结果"""
    yin_yang, is_change = _generate_random_yao()
    return {"yin_yang": yin_yang, "is_changing": is_change}


@router.post("/manual_complete", response_model=QiguaResponse)
async def manual_complete(yao_results: List[dict]):
    """
    手动摇卦完成：接收6次结果组成的数组
    每个元素格式：{"yin_yang": 0/1, "is_changing": bool}
    """
    if len(yao_results) != 6:
        raise HTTPException(status_code=400, detail="必须提供6爻数据")
    yao_list = [item["yin_yang"] for item in yao_results]
    changing = [item["is_changing"] for item in yao_results]
    now = datetime.datetime.now()
    return QiguaResponse(
        yao_list=yao_list,
        changing_yao=changing,
        timestamp={"year": now.year, "month": now.month, "day": now.day, "hour": now.hour}
    )


@router.post("/specify", response_model=QiguaResponse)
async def specify_qigua(request: QiguaRequest):
    """
    手工指定起卦：直接提供阴阳列表和动爻列表
    """
    if not request.yao_values or len(request.yao_values) != 6:
        raise HTTPException(status_code=400, detail="必须提供6个阴阳值")
    if not request.changing_yao or len(request.changing_yao) != 6:
        # 若未提供动爻，默认全部静爻
        changing = [False] * 6
    else:
        changing = request.changing_yao

    now = datetime.datetime.now()
    year = request.year or now.year
    month = request.month or now.month
    day = request.day or now.day
    hour = request.hour if request.hour is not None else now.hour

    return QiguaResponse(
        yao_list=request.yao_values,
        changing_yao=changing,
        timestamp={"year": year, "month": month, "day": day, "hour": hour}
    )


@router.post("/time", response_model=QiguaResponse)
async def time_qigua(request: QiguaRequest):
    """
    时间起卦：以指定时间（或当前时间）用梅花易数规则生成卦
    简化实现：取年月日时数字之和求余得卦
    """
    now = datetime.datetime.now()
    year = request.year or now.year
    month = request.month or now.month
    day = request.day or now.day
    hour = request.hour if request.hour is not None else now.hour

    # 梅花易数时间起卦：年+月+日 取上卦，年+月+日+时 取下卦，总和取动爻
    sum_shang = year + month + day
    sum_xia = year + month + day + hour
    shang_gua_num = sum_shang % 8  # 0坤 1乾 2兑 3离 4震 5巽 6坎 7艮
    xia_gua_num = sum_xia % 8
    dong_yao_num = sum_xia % 6  # 0代表6爻动

    # 八卦数字对应表（先天数）
    num_to_gua_code = {
        1: '111',  # 乾
        2: '110',  # 兑
        3: '101',  # 离
        4: '100',  # 震
        5: '011',  # 巽
        6: '010',  # 坎
        7: '001',  # 艮
        0: '000'   # 坤
    }
    shang_code = num_to_gua_code[shang_gua_num]
    xia_code = num_to_gua_code[xia_gua_num]
    full_code = xia_code + shang_code  # 初爻在左
    yao_list = [int(c) for c in full_code]
    changing = [False] * 6
    if dong_yao_num != 0:
        changing[dong_yao_num - 1] = True
    else:
        changing[5] = True  # 6爻动

    return QiguaResponse(
        yao_list=yao_list,
        changing_yao=changing,
        timestamp={"year": year, "month": month, "day": day, "hour": hour}
    )