@echo off
setlocal EnableExtensions

rem Keep Uvicorn attached to this console. Closing the CMD window stops it.
cd /d "%~dp0"

set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo [ERROR] Virtual environment Python was not found:
    echo "%PYTHON%"
    echo Install requirements.lock first.
    pause
    exit /b 1
)

"%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=1).close()" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] Port 8000 already has a running Liuyao service.
    echo Close its CMD window or run stop.bat before trying again.
    pause
    exit /b 1
)

echo Starting Liuyao web service...
start "Liuyao backend" /B "%PYTHON%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

rem Wait until the service is ready before opening the browser.
for /l %%i in (1,1,30) do (
    "%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=1).close()" >nul 2>&1
    if not errorlevel 1 goto ready
    timeout /t 1 /nobreak >nul
)

echo [ERROR] The web service did not become ready within 30 seconds.
echo Check the output above and whether port 8000 is available.
pause
exit /b 1

:ready
echo Web service is ready: http://127.0.0.1:8000/
echo Keep this CMD window open. Closing it stops the service.
if /i not "%~1"=="/no-browser" start "" "http://127.0.0.1:8000/"
exit /b 0
