#!/bin/bash

# Tivrag Quick Start Script

echo "🚀 Starting Tivrag Application"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo ""
echo "📦 Setting up Backend..."
echo "================================"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo ""
echo "⚠️  IMPORTANT: Configure Google OAuth"
echo "================================"
echo "Before starting the server, you need to:"
echo "1. Create a Google Cloud project"
echo "2. Enable Gmail and Drive APIs"
echo "3. Create OAuth 2.0 credentials"
echo "4. Update google_services.py with your Client ID and Secret"
echo ""
echo "Or set environment variables:"
echo "  export GOOGLE_CLIENT_ID='your-client-id'"
echo "  export GOOGLE_CLIENT_SECRET='your-client-secret'"
echo ""
read -p "Press Enter when ready to continue..."

# Start backend in background
echo ""
echo "🚀 Starting Backend Server on http://localhost:8002"
python main.py &
BACKEND_PID=$!

cd ../frontend

echo ""
echo "📦 Setting up Frontend..."
echo "================================"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo ""
echo "🚀 Starting Frontend Server on http://localhost:5175"
echo "================================"
echo ""
echo "✅ Application is starting!"
echo ""
echo "Open your browser and navigate to: http://localhost:5175"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start frontend (this will run in foreground)
npm run dev

# When frontend is stopped, also stop backend
kill $BACKEND_PID 2>/dev/null

