"""卦辞、爻辞 API。"""

from __future__ import annotations

from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Path as PathParam
from pydantic import BaseModel, ConfigDict

from ..core.guaci import GuaciManager


class GuaciResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    gua_ci: str
    tuan_ci: str
    xiang_ci: str


class YaociResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    yao_ci: str


router = APIRouter(prefix="/api", tags=["卦辞爻辞"])
manager = GuaciManager(FilePath(__file__).resolve().parent.parent / "data")


@router.get("/guaci/{gua_id}", response_model=GuaciResponse)
async def get_guaci(
    gua_id: Annotated[int, PathParam(ge=1, le=64)],
) -> dict[str, str]:
    """获取指定卦的卦辞。"""

    try:
        return manager.load_guaci(gua_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="卦不存在") from exc


@router.get("/yaoci/{gua_id}/{yao_pos}", response_model=YaociResponse)
async def get_yaoci(
    gua_id: Annotated[int, PathParam(ge=1, le=64)],
    yao_pos: Annotated[int, PathParam(ge=1, le=6)],
) -> dict[str, str]:
    """获取指定卦指定爻的爻辞。"""

    try:
        return {"yao_ci": manager.load_yaoci(gua_id, yao_pos)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="卦或爻位不存在") from exc
