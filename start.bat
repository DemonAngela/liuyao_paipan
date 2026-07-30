@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\server.ps1" start -OpenBrowser
set "SCRIPT_EXIT=%ERRORLEVEL%"
if not "%SCRIPT_EXIT%"=="0" (
    echo.
    echo Startup failed. See details above.
    pause
)
exit /b %SCRIPT_EXIT%
