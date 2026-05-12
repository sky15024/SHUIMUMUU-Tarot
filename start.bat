@echo off
cd /d "%~dp0"
echo ==============================================
echo Starting SHUIMUMUU Tarot Server...
echo ==============================================

start "" "http://localhost:8000"

python main.py

pause
