@echo off
title Leap2Launch V23
cd /d "%~dp0"
echo.
echo ==============================================
echo        Leap2Launch V23 - SIH Build
echo ==============================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py
) else (
  set PY=python
)
if exist ".venv\Scripts\python.exe" (
  set PY=.venv\Scripts\python.exe
)
echo Using: %PY%
echo.
%PY% app.py
pause
