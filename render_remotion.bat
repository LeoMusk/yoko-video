@echo off
REM yoko-video: render latest M3 script with Remotion
powershell -ExecutionPolicy Bypass -File "%~dp0render_remotion.ps1"
pause
