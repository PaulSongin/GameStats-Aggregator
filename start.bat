@echo off
echo Starting GameStats Aggregator...
cd /d "%~dp0"
docker-compose up -d
echo.
echo Services started!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:5000
echo Python Provider: http://localhost:8000
echo.
pause
