@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

REM Try a few common PT paths. Adjust if yours is different.
set "PT_IN=%ROOT%\pt\pt.json"
if not exist "%PT_IN%" set "PT_IN=%ROOT%\pt\pt-PT.json"
if not exist "%PT_IN%" set "PT_IN=%ROOT%\pt\pt_pt.json"
if not exist "%PT_IN%" set "PT_IN=%ROOT%\pt\pt_PT.json"
if not exist "%PT_IN%" set "PT_IN=%ROOT%\pt\ptBR.json"
if not exist "%PT_IN%" set "PT_IN=%ROOT%\pt\pt-BR.json"

set "DELTA=%SCRIPT_DIR%deltas\delta_pt.json"
set "PT_OUT=%ROOT%\pt\pt_updated.json"

if not exist "%PT_IN%" (
  echo [ERROR] Portuguese file not found in common locations.
  echo Please edit PT_IN in this .bat to your real path.
  pause
  exit /b 1
)

if not exist "%DELTA%" (
  echo [ERROR] Delta file not found: "%DELTA%"
  echo Put delta_pt.json into: "%SCRIPT_DIR%deltas\"
  pause
  exit /b 1
)

py "%SCRIPT_DIR%apply_delta.py" "%PT_IN%" "%DELTA%" "%PT_OUT%"
if errorlevel 1 (
  echo [ERROR] apply_delta.py failed.
  pause
  exit /b 1
)

echo.
echo Done: "%PT_OUT%"
pause
