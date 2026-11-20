@echo off
rem MPW im Browser (Portable): nutzt den Ordner Data dieser Portable-Version.
cd /d "%~dp0"
if not exist "%~dp0.mpw-portable-v2" (
  echo Portable-Marker fehlt. Start abgebrochen.
  pause
  exit /b 1
)
"%~dp0App\MPW-Web.exe"
if errorlevel 1 pause
