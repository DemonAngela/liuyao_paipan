@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" start -OpenBrowser
set "SCRIPT_EXIT=%ERRORLEVEL%"
if not "%SCRIPT_EXIT%"=="0" (
    echo.
    echo 启动失败，请检查上方信息。
    pause
)
exit /b %SCRIPT_EXIT%
