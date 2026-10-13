@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo Leap2Launch V26 - Local setup
 echo This installs dependencies into a project-local .venv.
echo Internet is required for the first installation.
echo ============================================================
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python was not found. Install Python 3.11+ and enable Add Python to PATH.
    pause
    exit /b 2
  )
  set PY=python
) else (
  set PY=py
)
if not exist .venv\Scripts\python.exe (
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
call VERIFY_ALL_STATIC.bat
if errorlevel 1 goto failed
echo.
echo Setup complete. Starting the local server...
echo Open http://127.0.0.1:5000 in your browser.
echo Keep this terminal open while using the app.
python app.py
goto end
:failed
echo.
echo SETUP/VERIFICATION FAILED. Read the error above.
echo If installation fails due to DNS/network restrictions, connect to the internet and rerun this file.
pause
exit /b 1
:end
endlocal
