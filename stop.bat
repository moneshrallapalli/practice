@echo off
REM ################################################################################
REM SentinTinel Surveillance System - Windows Stop Script
REM Stops all running services
REM ################################################################################

setlocal EnableDelayedExpansion

echo.
echo ==================================
echo Stopping SentinTinel Surveillance
echo ==================================
echo.

REM Kill backend processes
echo Stopping backend server...
taskkill /F /FI "WINDOWTITLE eq SentinTinel Backend*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend stopped
) else (
    echo [WARNING] Backend process not found
)

REM Kill frontend processes
echo Stopping frontend server...
taskkill /F /FI "WINDOWTITLE eq SentinTinel Frontend*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend stopped
) else (
    echo [WARNING] Frontend process not found
)

REM Kill any remaining Node and Python processes related to our app
echo Cleaning up processes...
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq *react-scripts*" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1

echo.
echo ==================================
echo SentinTinel Stopped
echo ==================================
echo.
echo All services have been stopped successfully
echo.
echo To start the system again, run: start.bat
echo.
pause
