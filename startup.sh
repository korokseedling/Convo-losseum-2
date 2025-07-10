#!/bin/bash

# Agora Chat Startup Script
echo "🚀 Starting Agora Chat..."

# Load environment variables
source .env

# Aggressive port killer for 7632
echo "🔪 Killing any processes on port 7632..."
lsof -ti:7632 | xargs kill -9 2>/dev/null || true
fuser -k 7632/tcp 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

# Wait a moment for processes to die
sleep 2

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found! Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install/upgrade requirements
echo "📦 Installing/updating Python dependencies..."
pip install -r requirements.txt --upgrade --quiet

# Verify port is free
echo "🔍 Verifying port 7632 is available..."
if lsof -Pi :7632 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 7632 is still in use. Please wait and try again."
    exit 1
fi

# Start the Flask application in background
echo "🌟 Starting Agora Chat on http://localhost:7632"
echo "📝 Chat logs will appear below..."
echo "🛑 Press Ctrl+C to stop the server"
echo "=================================="

# Start the server with virtual environment
nohup python app.py > agora_chat.log 2>&1 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Agora Chat server started successfully (PID: $SERVER_PID)"
    
    # Open browser automatically
    echo "🌐 Opening browser..."
    if command -v open &> /dev/null; then
        # macOS
        open http://localhost:7632
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:7632
    elif command -v start &> /dev/null; then
        # Windows
        start http://localhost:7632
    else
        echo "🔗 Please open http://localhost:7632 in your browser"
    fi
    
    # Show real-time logs
    echo "📊 Real-time logs (Ctrl+C to stop):"
    echo "======================================"
    tail -f agora_chat.log
    
else
    echo "❌ Failed to start Agora Chat server"
    echo "📋 Check agora_chat.log for error details:"
    cat agora_chat.log
    exit 1
fi

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down Agora Chat..."
    kill $SERVER_PID 2>/dev/null || true
    lsof -ti:7632 | xargs kill -9 2>/dev/null || true
    echo "✅ Agora Chat stopped successfully"
    exit 0
}

# Handle Ctrl+C
trap cleanup SIGINT SIGTERM

# Keep script running
wait
