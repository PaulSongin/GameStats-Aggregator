@echo off
echo Stopping GameStats Aggregator...
cd /d "%~dp0"
docker-compose down
echo.
echo Services stopped!
pause
