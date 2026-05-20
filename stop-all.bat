@echo off
echo Stopping all GameStats Aggregator services...
cd /d "%~dp0"

echo Stopping Docker containers...
docker-compose down

echo.
echo All services stopped!
echo Note: Frontend terminal windows need to be closed manually (Ctrl+C)
echo.
pause
