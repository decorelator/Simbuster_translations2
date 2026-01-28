@echo off
setlocal

REM Folder where this .bat lives (diffScript)
set "SCRIPT_DIR=%~dp0"
REM Project root = parent of diffScript
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

REM Inputs/outputs
set "ES_IN=%ROOT%\es\es.json"
set "DELTA=%SCRIPT_DIR%deltas\delta_es.json"
set "ES_OUT=%ROOT%\es\es_updated.json"

if not exist "%ES_IN%" (
  echo [ERROR] Spanish file not found: "%ES_IN%"
  echo Fix ES_IN inside this .bat if your path is different.
  pause
  exit /b 1
)

if not exist "%DELTA%" (
  echo [ERROR] Delta file not found: "%DELTA%"
  echo Put delta_es.json into: "%SCRIPT_DIR%deltas\"
  pause
  exit /b 1
)

py "%SCRIPT_DIR%apply_delta.py" "%ES_IN%" "%DELTA%" "%ES_OUT%"
if errorlevel 1 (
  echo [ERROR] apply_delta.py failed.
  pause
  exit /b 1
)

echo.
echo Done: "%ES_OUT%"
pause
