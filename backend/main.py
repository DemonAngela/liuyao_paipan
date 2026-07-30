"""FastAPI 应用入口与运行配置。"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import cidian, ganzhi, paipan, qigua

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def _configured_cors_origins() -> tuple[str, ...]:
    raw = os.getenv("LIUYAO_CORS_ORIGINS", "")
    origins = tuple(
        value.strip().rstrip("/")
        for value in raw.split(",")
        if value.strip()
    )
    if "*" in origins:
        raise ValueError("LIUYAO_CORS_ORIGINS 不允许使用通配符 *")
    return origins


def create_app(
    cors_origins: Sequence[str] | None = None,
) -> FastAPI:
    """创建应用；默认同源运行，仅为显式白名单启用 CORS。"""

    origins = (
        tuple(cors_origins)
        if cors_origins is not None
        else _configured_cors_origins()
    )
    if "*" in origins:
        raise ValueError("CORS 白名单不允许使用通配符 *")

    application = FastAPI(
        title="周易六爻排盘系统",
        version="1.2.0",
    )
    if origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(origins),
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type"],
        )

    application.include_router(qigua.router)
    application.include_router(paipan.router)
    application.include_router(cidian.router)
    application.include_router(ganzhi.router)

    @application.get("/healthz", include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/", include_in_schema=False)
    async def root():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        return {"message": "周易六爻排盘系统 API 已运行"}

    if FRONTEND_DIR.is_dir():
        application.mount(
            "/",
            StaticFiles(directory=FRONTEND_DIR, html=True),
            name="frontend",
        )
    return application


app = create_app()


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} 必须是布尔值")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=os.getenv("LIUYAO_HOST", "127.0.0.1"),
        port=int(os.getenv("LIUYAO_PORT", "8000")),
        reload=_env_flag("LIUYAO_RELOAD"),
    )
