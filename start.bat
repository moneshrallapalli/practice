@echo off
REM ################################################################################
REM SentinTinel Surveillance System - Windows Startup Script
REM Starts all required services
REM ################################################################################

setlocal EnableDelayedExpansion

echo.
echo ==================================
echo Starting SentinTinel Surveillance
echo ==================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Create PID directory
if not exist ".pids" mkdir ".pids"

REM ################################################################################
REM Check Prerequisites
REM ################################################################################

echo Checking Prerequisites...
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js found: %NODE_VERSION%

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed or not in PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm found: v%NPM_VERSION%

echo.

REM ################################################################################
REM Setup Backend
REM ################################################################################

echo ==================================
echo Setting up Backend
echo ==================================
echo.

cd "%SCRIPT_DIR%backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo [WARNING] Virtual environment not found. Creating...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\.installed" (
    echo [WARNING] Installing backend dependencies...
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo. > venv\.installed
    echo [OK] Backend dependencies installed
) else (
    echo [OK] Backend dependencies already installed
)

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from template...
    copy .env.example .env
    echo.
    echo ********************************************************
    echo IMPORTANT: Please edit backend\.env and add your Gemini API key!
    echo ********************************************************
    echo.
    pause
)

REM Initialize database if needed
if not exist ".db_initialized" (
    echo [WARNING] Initializing database...
    python init_db.py
    echo. > .db_initialized
    echo [OK] Database initialized
)

REM Start backend in new window
echo Starting backend server...
start "SentinTinel Backend" cmd /k "cd /d %SCRIPT_DIR%backend && venv\Scripts\activate && python main.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [OK] Backend started
echo Backend running at: http://localhost:8000

REM ################################################################################
REM Setup Frontend
REM ################################################################################

echo.
echo ==================================
echo Setting up Frontend
echo ==================================
echo.

cd "%SCRIPT_DIR%frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] Installing frontend dependencies...
    call npm install
    echo [OK] Frontend dependencies installed
) else (
    echo [OK] Frontend dependencies already installed
)

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from template...
    copy .env.example .env
    echo [OK] .env file created
)

REM Start frontend in new window
echo Starting frontend server...
start "SentinTinel Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend && npm start"

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo [OK] Frontend started
echo Frontend running at: http://localhost:3000

REM ################################################################################
REM Summary
REM ################################################################################

echo.
echo ==================================
echo SentinTinel Started Successfully!
echo ==================================
echo.
echo Services:
echo   - Backend:  http://localhost:8000
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Two command windows have been opened:
echo   1. Backend Server
echo   2. Frontend Server
echo.
echo To stop the system:
echo   - Close both command windows, OR
echo   - Run stop.bat
echo.
echo Opening dashboard in browser...
timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:3000

echo.
echo Happy Monitoring!
echo.
pause
