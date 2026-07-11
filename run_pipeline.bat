@echo off
REM Backward-compatible alias. Prefer run_news.bat / run_all.bat.
powershell -ExecutionPolicy Bypass -File "%~dp0run_pipeline.ps1"
pause
