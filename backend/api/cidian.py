"""
卦辞爻辞 API 路由
"""

import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["卦辞爻辞"])

# 加载数据文件
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

GUACI_DATA = load_json("64gua.json")
YAOCI_DATA = load_json("yaoci.json")


@router.get("/guaci/{gua_id}")
async def get_guaci(gua_id: int):
    """获取指定卦的卦辞"""
    gua = GUACI_DATA.get(str(gua_id))
    if not gua:
        raise HTTPException(status_code=404, detail="卦不存在")
    return {
        "name": gua.get("name", ""),
        "gua_ci": gua.get("gua_ci", ""),
        "tuan_ci": gua.get("tuan_ci", ""),
        "xiang_ci": gua.get("xiang_ci", "")
    }


@router.get("/yaoci/{gua_id}/{yao_pos}")
async def get_yaoci(gua_id: int, yao_pos: int):
    """获取指定卦指定爻的爻辞"""
    gua = YAOCI_DATA.get(str(gua_id))
    if not gua:
        raise HTTPException(status_code=404, detail="卦不存在")
    yao = gua.get(str(yao_pos))
    if not yao:
        raise HTTPException(status_code=404, detail="爻位不存在")
    return {"yao_ci": yao}