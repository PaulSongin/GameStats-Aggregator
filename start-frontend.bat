@echo off
echo Starting Frontend...
cd /d "%~dp0\frontend"
start cmd /k "npm run dev"
echo.
echo Frontend starting at http://localhost:3000
