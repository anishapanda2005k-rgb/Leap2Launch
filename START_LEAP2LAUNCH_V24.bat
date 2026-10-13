@echo off
title Leap2Launch V24
echo.
echo ==============================================
echo      Leap2Launch V24 - SIH Working Build
echo ==============================================
echo.
cd /d "%~dp0"
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PY=py -3.12"
)
echo Using Python: %PY%
echo Project: %CD%
echo.
%PY% app.py
pause
