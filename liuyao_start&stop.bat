@echo off
setlocal EnableExtensions

rem Always run from the project directory, regardless of the launch location.
cd /d "%~dp0"

set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo [ERROR] Virtual environment Python was not found:
    echo "%PYTHON%"
    echo Create the virtual environment and install requirements.txt first.
    pause
    exit /b 1
)

echo Starting Liuyao web service...
start "Liuyao backend" /B "%PYTHON%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

rem Wait until the service is reachable instead of opening the browser after a fixed delay.
for /l %%i in (1,1,30) do (
    "%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=1).close()" >nul 2>&1
    if not errorlevel 1 goto ready
    timeout /t 1 /nobreak >nul
)

echo [ERROR] The web service did not become ready within 30 seconds.
echo Check the backend error output above and whether port 8000 is already in use.
pause
exit /b 1

:ready
echo Web service is ready: http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"
exit /b 0
