#!/bin/bash

echo "======================================"
echo "  Nonprofit CRM - Startup Script"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✓ Python is installed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Generate sample data if database doesn't exist
if [ ! -f "nonprofit_crm.db" ]; then
    echo ""
    echo "No database found. Generating sample data..."
    python3 generate_sample_data.py
fi

echo ""
echo "======================================"
echo "  Starting Backend Server"
echo "======================================"
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo ""

# Start backend in background
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo ""
    echo "======================================"
    echo "  Starting Frontend Server"
    echo "======================================"
    echo ""

    cd frontend

    # Install frontend dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    echo ""
    echo "Frontend will be available at: http://localhost:3000"
    echo ""
    echo "Default login credentials:"
    echo "  Username: admin"
    echo "  Password: secret"
    echo ""
    echo "======================================"
    echo "  CRM is ready!"
    echo "======================================"
    echo ""

    # Start frontend
    npm run dev
else
    echo "Frontend directory not found. Running backend only."
    wait $BACKEND_PID
fi

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
