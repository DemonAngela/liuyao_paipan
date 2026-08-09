"""FastAPI 主入口。"""

import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.api import cidian, paipan, qigua

app = FastAPI(title="周易六爻排盘系统", version="1.0.0")

# 默认同源部署不需要 CORS。若确需跨域访问，使用逗号分隔的环境变量显式授权：
# LIUYAO_CORS_ORIGINS=https://example.com,http://localhost:5173
cors_origins = [
    origin.strip()
    for origin in os.getenv("LIUYAO_CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

app.include_router(qigua.router)
app.include_router(paipan.router)
app.include_router(cidian.router)

frontend_path = os.path.join(project_root, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/")
async def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "周易六爻排盘系统 API 已运行，请访问前端页面。"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="::",
        port=8000,
        reload=True,
    )
