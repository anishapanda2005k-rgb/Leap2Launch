@echo off
setlocal
 title Leap2Launch V26 - A-Z Learning Directory
cd /d "%~dp0"
echo.
echo ==================================================
echo   Leap2Launch V26 - Career Pathways + Learning Studio
echo ==================================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Creating a local Python virtual environment...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.12 -m venv .venv 2>nul
    if errorlevel 1 py -3 -m venv .venv 2>nul
  ) else (
    python -m venv .venv 2>nul
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Python could not create .venv.
  echo Install Python 3.11 or 3.12, enable the Python launcher, then run this file again.
  pause
  exit /b 1
)

.venv\Scripts\python.exe -c "import flask, reportlab, pygame" >nul 2>nul
if errorlevel 1 (
  echo Installing required Python packages from requirements.txt...
  .venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 goto :install_failed
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :install_failed
)

echo Starting Leap2Launch...
echo Open http://127.0.0.1:5000/ in your browser.
echo Press Ctrl+C in this window to stop the server.
echo.
.venv\Scripts\python.exe app.py
pause
exit /b 0

:install_failed
echo.
echo ERROR: Dependency installation failed. Check your internet connection and Python setup.
echo You can also run: .venv\Scripts\python.exe -m pip install -r requirements.txt
pause
exit /b 1
