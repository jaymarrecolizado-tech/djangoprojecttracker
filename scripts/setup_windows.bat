@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =============================================================================
:: Project Tracking Management System - Windows Setup Script
:: For WAMP MySQL Environment
:: =============================================================================

title PTMS - Windows Setup
color 0B
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║           Project Tracking Management System - Windows Setup                 ║
echo ║                         WAMP Environment                                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Configuration
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"
echo 📁 Project root: %CD%
echo.

:: =============================================================================
:: Check Prerequisites
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                         Checking Prerequisites                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python found: !PYTHON_VERSION!

:: Check Node.js
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo    Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('node --version 2^>^&1') do set NODE_VERSION=%%a
echo ✅ Node.js found: !NODE_VERSION!

:: Check npm
echo [3/5] Checking npm installation...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed or not in PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('npm --version 2^>^&1') do set NPM_VERSION=%%a
echo ✅ npm found: !NPM_VERSION!

:: Check MySQL/MariaDB
echo [4/5] Checking MySQL availability...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL CLI not in PATH
    echo    Make sure WAMP MySQL is running and mysql.exe is accessible
    echo    You may need to add C:\wamp64\bin\mysql\mysql8.x.x\bin to PATH
) else (
    for /f "tokens=*" %%a in ('mysql --version 2^>^&1') do set MYSQL_VERSION=%%a
    echo ✅ MySQL found: !MYSQL_VERSION!
)

:: Check WAMP
echo [5/5] Checking WAMP Server...
if exist "C:\wamp64\wampmanager.exe" (
    echo ✅ WAMP64 found at C:\wamp64
) else if exist "C:\wamp\wampmanager.exe" (
    echo ✅ WAMP found at C:\wamp
) else (
    echo ⚠️  WAMP installation not detected in standard locations
    echo    Please ensure WAMP is installed at C:\wamp64 or C:\wamp
)

echo.
echo ✅ All required prerequisites found!
echo.

:: =============================================================================
:: Setup Database
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                         Database Setup                                       ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Make sure WAMP MySQL is running before proceeding!
echo.
echo Do you want to create the database now? (Y/N)
set /p CREATE_DB=
if /i "!CREATE_DB!"=="Y" (
    echo.
    echo Creating database and user...
    mysql -u root -p < scripts\setup_database.sql
    if errorlevel 1 (
        echo ⚠️  Database setup failed. You may need to run it manually:
        echo    mysql -u root -p ^< scripts\setup_database.sql
    ) else (
        echo ✅ Database created successfully
    )
)
echo.

:: =============================================================================
:: Backend Setup
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                         Backend Setup                                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check if virtual environment exists
echo [1/4] Setting up Python virtual environment...
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment and install dependencies
echo [2/4] Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing Python packages (this may take a few minutes)...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python packages
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed

:: Copy environment file
echo [3/4] Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Created .env from .env.example
        echo ⚠️  IMPORTANT: Please edit .env and update database credentials!
    ) else (
        echo ❌ .env.example not found
    )
) else (
    echo ✅ .env file already exists
)

:: Run migrations
echo [4/4] Running database migrations...
echo [INFO] Make sure you have configured the database credentials in .env
echo Do you want to run migrations now? (Y/N)
set /p RUN_MIGRATIONS=
if /i "!RUN_MIGRATIONS!"=="Y" (
    python manage.py migrate
    if errorlevel 1 (
        echo ⚠️  Migrations failed. Check your database settings in .env
        echo    Ensure MySQL is running and credentials are correct
    ) else (
        echo ✅ Database migrations completed
        
        :: Create superuser
        echo.
        echo Do you want to create a superuser? (Y/N)
        set /p CREATE_SUPERUSER=
        if /i "!CREATE_SUPERUSER!"=="Y" (
            python manage.py createsuperuser
        )
        
        :: Seed data
        echo.
        echo Do you want to seed reference data? (Y/N)
        set /p SEED_DATA=
        if /i "!SEED_DATA!"=="Y" (
            python manage.py seed_data
            echo ✅ Reference data seeded
        )
    )
)

call venv\Scripts\deactivate.bat
cd ..
echo.

:: =============================================================================
:: Frontend Setup
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                         Frontend Setup                                       ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

cd frontend

:: Install dependencies
echo [1/2] Installing frontend dependencies...
if not exist "node_modules" (
    echo Installing npm packages (this may take a few minutes)...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install npm packages
        pause
        exit /b 1
    )
    echo ✅ Frontend dependencies installed
) else (
    echo ✅ node_modules already exists
)

:: Copy environment file
echo [2/2] Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Created .env from .env.example
    ) else (
        echo ❌ .env.example not found
    )
) else (
    echo ✅ .env file already exists
)

cd ..
echo.

:: =============================================================================
:: Setup Complete
:: =============================================================================
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                       Setup Complete!                                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Project Tracking Management System has been configured!
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  NEXT STEPS:
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  1. ⚙️  Configure Environment Variables:
echo     • Edit backend\.env with your database credentials
echo     • Edit frontend\.env if needed (default settings should work)
echo.
echo  2. 🚀 Start the Application:
echo     • Run: scripts\start_windows.bat
echo     • Or start backend and frontend manually in separate terminals
echo.
echo  3. 🌐 Access the Application:
echo     • Frontend: http://localhost:3000
echo     • Backend API: http://localhost:8000/api/v1/
echo     • Admin Panel: http://localhost:8000/admin/
echo.
echo  4. 📚 Documentation:
echo     • See SETUP_WAMP.md for detailed WAMP setup instructions
echo     • See docs\ folder for complete documentation
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
pause
