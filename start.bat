@echo off
REM Tivrag Quick Start Script for Windows

echo 🚀 Starting Tivrag Application
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo.
echo 📦 Setting up Backend...
echo ================================

cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -q -r requirements.txt

echo.
echo ⚠️  IMPORTANT: Configure Google OAuth
echo ================================
echo Before starting the server, you need to:
echo 1. Create a Google Cloud project
echo 2. Enable Gmail and Drive APIs
echo 3. Create OAuth 2.0 credentials
echo 4. Update google_services.py with your Client ID and Secret
echo.
echo Or set environment variables:
echo   set GOOGLE_CLIENT_ID=your-client-id
echo   set GOOGLE_CLIENT_SECRET=your-client-secret
echo.
pause

REM Start backend in background
echo.
echo 🚀 Starting Backend Server on http://localhost:8002
start /b python main.py

cd ..\frontend

echo.
echo 📦 Setting up Frontend...
echo ================================

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

echo.
echo 🚀 Starting Frontend Server on http://localhost:5175
echo ================================
echo.
echo ✅ Application is starting!
echo.
echo Open your browser and navigate to: http://localhost:5175
echo.
echo Press Ctrl+C to stop the servers
echo.

REM Start frontend
npm run dev

