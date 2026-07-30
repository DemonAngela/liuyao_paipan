@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" -Action status >nul 2>&1
set "SERVICE_STATUS=%ERRORLEVEL%"

if "%SERVICE_STATUS%"=="0" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" -Action stop
) else (
    if /i "%~1"=="/no-browser" (
        powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" -Action start
    ) else (
        powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" -Action start -OpenBrowser
    )
)

set "SCRIPT_EXIT=%ERRORLEVEL%"
if not "%SCRIPT_EXIT%"=="0" (
    echo.
    echo Operation failed. See details above.
    pause
)
exit /b %SCRIPT_EXIT%
