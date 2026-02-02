@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =============================================================================
:: Project Tracking Management System - Windows Start Script
:: Starts both backend and frontend development servers
:: =============================================================================

title PTMS - Development Servers
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║       Project Tracking Management System - Development Server Startup        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

:: Check if servers are already running
echo Checking for existing servers...
netstat -ano | findstr :8000 >nul && (
    echo ⚠️  Port 8000 is already in use. Backend may already be running.
)
netstat -ano | findstr :3000 >nul && (
    echo ⚠️  Port 3000 is already in use. Frontend may already be running.
)
echo.

:: =============================================================================
:: Start Backend Server
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    Starting Backend Server (Django)                          ║
echo ║                    URL: http://localhost:8000                                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

start "PTMS Backend" cmd /k "cd /d %CD%\backend && call venv\Scripts\activate.bat && echo Starting Django development server... && python manage.py runserver 0.0.0.0:8000"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Check if backend started successfully
netstat -ano | findstr :8000 >nul && (
    echo ✅ Backend server started on http://localhost:8000
) || (
    echo ⚠️  Waiting for backend to initialize...
)

echo.

:: =============================================================================
:: Start Frontend Server
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    Starting Frontend Server (Vite)                           ║
echo ║                    URL: http://localhost:3000                                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

start "PTMS Frontend" cmd /k "cd /d %CD%\frontend && echo Starting Vite development server... && npm run dev"

:: Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

:: Check if frontend started successfully
netstat -ano | findstr :3000 >nul && (
    echo ✅ Frontend server started on http://localhost:3000
) || (
    echo ⚠️  Waiting for frontend to initialize...
)

echo.

:: =============================================================================
:: Display Status
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                          Servers Started!                                    ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Development servers are starting up...
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  ACCESS URLs:
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  🌐 Frontend Application:  http://localhost:3000
echo  📡 Backend API:           http://localhost:8000/api/v1/
echo  🔧 Admin Panel:           http://localhost:8000/admin/
echo  📚 API Documentation:     http://localhost:8000/api/v1/docs/
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  DEFAULT LOGIN CREDENTIALS:
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  Username: admin
echo  Password: admin123
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  IMPORTANT NOTES:
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  • This window will remain open while servers are running
echo  • Close the individual command windows to stop each server
echo  • Backend terminal: PTMS Backend
echo  • Frontend terminal: PTMS Frontend
echo.
echo  Press any key to close this status window (servers will keep running)...
echo.
pause >nul
