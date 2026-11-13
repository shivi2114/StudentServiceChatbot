@echo off
title CampusAI Backend Server
cd /d "%~dp0"
echo ====================================================
echo  Starting CampusAI Multi-Agent Backend Server
echo  Unified Web Portal: http://localhost:8000
echo  Swagger API Docs:   http://localhost:8000/docs
echo ====================================================
echo.
if exist ".\venv\Scripts\python.exe" (
    ".\venv\Scripts\python.exe" backend\app\main.py
) else (
    python backend\app\main.py
)
pause
