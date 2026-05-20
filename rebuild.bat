@echo off
echo Rebuilding and starting GameStats Aggregator...
cd /d "%~dp0"
docker-compose down
docker-compose up -d --build
echo.
echo Services rebuilt and started!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:5000
echo Python Provider: http://localhost:8000
echo.
pause
