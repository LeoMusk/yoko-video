@echo off
REM yoko-video: generate daily AI news brief
powershell -ExecutionPolicy Bypass -File "%~dp0run_news.ps1"
pause
