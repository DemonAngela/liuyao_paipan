"""
FastAPI 主入口
兼容直接运行和模块运行
"""

import sys
import os

# 将项目根目录加入 sys.path，确保能导入 backend 包
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from backend.api import qigua, paipan, cidian

app = FastAPI(title="周易六爻排盘系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qigua.router)
app.include_router(paipan.router)
app.include_router(cidian.router)

frontend_path = os.path.join(project_root, "frontend")
if os.path.exists(frontend_path):
    # 将 frontend 目录挂载到根路径，但不覆盖 API 路由
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
        host="::",          # 双栈监听，兼容 IPv4 和 IPv6
        #host="127.0.0.1",  # IPv4
        #host="0.0.0.0",  # 双栈监听，兼容 IPv4 和 IPv6
        port=8000,
        reload=True         # 开发模式热重载，生产环境可设为 False
    )