@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo Leap2Launch V26 - Static verification suite
echo ============================================================
set FAIL=0
python -m py_compile app.py VERIFY_BUILD.py VERIFY_E_LIBRARY.py VERIFY_FORM_SECURITY.py VERIFY_LEARNING_CATALOG.py VERIFY_LEARNING_LINK_AUDIT.py VERIFY_PDF_LINK_AUDIT.py VERIFY_WEB_AUDIT_REPORT.py VERIFY_AI_ENGINE.py VERIFY_CORE_JOURNEYS.py
if errorlevel 1 set FAIL=1
for %%F in (VERIFY_BUILD.py VERIFY_E_LIBRARY.py VERIFY_FORM_SECURITY.py VERIFY_LEARNING_CATALOG.py VERIFY_LEARNING_LINK_AUDIT.py VERIFY_PDF_LINK_AUDIT.py VERIFY_WEB_AUDIT_REPORT.py VERIFY_AI_ENGINE.py VERIFY_CORE_JOURNEYS.py) do (
  echo.
  echo --- Running %%F ---
  python %%F
  if errorlevel 1 set FAIL=1
)
echo.
if "%FAIL%"=="0" (
 echo RESULT: All static checks passed.
) else (
 echo RESULT: One or more checks failed. Read the error above.
)
echo NOTE: Static checks do not replace browser/end-to-end testing.
pause
exit /b %FAIL%
