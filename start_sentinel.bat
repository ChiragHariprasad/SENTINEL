@echo off
title SENTINEL AI Launcher
echo =====================================================================
echo           SENTINEL AI
echo =====================================================================
echo.

echo [1/2] Launching Backend (uvicorn)...
start cmd /k "title SENTINEL Backend && cd backend && if not exist venv (python -m venv venv) && call .\venv\Scripts\activate.bat && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload"

echo [2/2] Launching Next.js Frontend...
start cmd /k "title SENTINEL Frontend && cd frontend && npm install && set NEXT_PUBLIC_API_URL=http://localhost:8082 && npm run dev -- -p 3000"

echo.
echo =====================================================================
echo  Services launched in background consoles!
echo  - Backend Endpoint:  http://localhost:8082
echo  - Frontend Portal:   http://localhost:3000
echo.
echo  Note: If your Docker Desktop is not running, the backend might crash
echo  trying to connect to PostgreSQL. Please ensure Docker is running and
echo  run `docker compose -f compose.standalone.yml up -d postgres redis` 
echo  to start the database services.
echo =====================================================================
pause
