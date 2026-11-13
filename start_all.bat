@echo off
title CampusAI Launcher
cd /d "%~dp0"
echo ====================================================
echo  Launching CampusAI Full Stack System
echo ====================================================
echo.
echo [1/2] Starting Backend FastAPI Server...
start "CampusAI Backend" cmd /k "cd /d "%~dp0" && .\venv\Scripts\python.exe backend\app\main.py"

echo [2/2] Starting Frontend Vite Server...
start "CampusAI Frontend" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

echo.
echo All services launched!
echo - FastAPI Unified Portal & Docs: http://localhost:8000
echo - React Dev Portal (HMR):       http://localhost:5173
echo.
