@echo off
echo ========================================
echo   GameStats Aggregator - Full Start
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Docker services (Backend, DB, Redis)...
docker-compose up -d
echo.

echo [2/2] Starting Frontend (Next.js)...
cd frontend
start cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   All services started!
echo ========================================
echo Frontend:        http://localhost:3000
echo Backend API:     http://localhost:5000
echo Python Provider: http://localhost:8000
echo PostgreSQL:      localhost:5433
echo Redis:           localhost:6379
echo ========================================
echo.
pause
