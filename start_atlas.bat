@echo off
title A.T.L.A.S Launcher
echo ===================================================
echo   A.T.L.A.S // Autonomous Thinking Learning OS
echo ===================================================
echo.

echo Starting Python Backend Server...
start "ATLAS Backend" cmd /c "python server.py"

echo Starting Next.js Desktop Dashboard...
cd apps\desktop-client
start "ATLAS Frontend" cmd /c "npm run dev"

echo.
echo ===================================================
echo   A.T.L.A.S is booting!
echo   - Backend runs on http://localhost:8000
echo   - Dashboard runs on http://localhost:3000
echo ===================================================
echo.
pause
