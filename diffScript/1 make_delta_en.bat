@echo off
setlocal

REM Folder where this .bat lives (diffScript)
set "SCRIPT_DIR=%~dp0"
REM Project root = parent of diffScript
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

REM English inputs (old + new)
set "EN_OLD=%ROOT%\translations.json"
set "EN_NEW=%ROOT%\new_translations.json"

REM Store deltas next to scripts
set "DELTAS_DIR=%SCRIPT_DIR%deltas"
set "OUT_DELTA=%DELTAS_DIR%\delta_en.json"

if not exist "%EN_OLD%" (
  echo [ERROR] Old EN file not found: "%EN_OLD%"
  pause
  exit /b 1
)

if not exist "%EN_NEW%" (
  echo [ERROR] New EN file not found: "%EN_NEW%"
  pause
  exit /b 1
)

if not exist "%DELTAS_DIR%" (
  mkdir "%DELTAS_DIR%"
)

py "%SCRIPT_DIR%diff_i18n.py" "%EN_OLD%" "%EN_NEW%" "%OUT_DELTA%"
if errorlevel 1 (
  echo [ERROR] diff_i18n.py failed.
  pause
  exit /b 1
)

echo.
echo Done: "%OUT_DELTA%"
pause
