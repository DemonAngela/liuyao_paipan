@echo off
chcp 65001 >nul
echo 正在启动周易六爻排盘系统...
cd /d %~dp0
call .\venv\Scripts\activate.bat 2>nul || echo 虚拟环境未找到，请先创建虚拟环境并安装依赖
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
