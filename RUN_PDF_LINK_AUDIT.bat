@echo off
cd /d "%~dp0"
python AUDIT_DIRECT_PDF_LINKS.py
if errorlevel 1 pause
pause
