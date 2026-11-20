@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build.ps1"
if errorlevel 1 (echo. & echo Build fehlgeschlagen. & pause & exit /b 1)
echo. & echo Build abgeschlossen. Ergebnisse im Ordner dist. & pause
