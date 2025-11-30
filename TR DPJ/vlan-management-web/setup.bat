@echo off
REM VLAN Management System - Setup Script for Windows

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   VLAN Management System - Setup                       ║
echo ║   This script will set up the project                 ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencies installed

REM Create .env file
echo.
echo Setting up environment configuration...
if exist .env (
    echo .env file already exists, skipping...
) else (
    copy .env.example .env
    echo ✅ .env file created (please update with your credentials)
)

REM Initialize database
echo.
echo Initializing database...
python -c "from backend.app import create_app, db; app = create_app(); db.create_all()"
echo ✅ Database initialized

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Setup Complete!                                      ║
echo ║                                                        ║
echo ║   Next steps:                                          ║
echo ║   1. Edit .env file with your Cisco credentials       ║
echo ║   2. Run: python run.py                               ║
echo ║   3. Open http://localhost:5000 in your browser       ║
echo ║                                                        ║
echo ║   To activate venv again:                             ║
echo ║   venv\Scripts\activate.bat                           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

pause
