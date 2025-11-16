#!/bin/bash

################################################################################
# SentinTinel Surveillance System - Startup Script
# Starts all required services (PostgreSQL, Redis, Backend, Frontend)
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message "$BLUE" "=================================="
    print_message "$BLUE" "$1"
    print_message "$BLUE" "=================================="
}

print_success() {
    print_message "$GREEN" "✓ $1"
}

print_error() {
    print_message "$RED" "✗ $1"
}

print_warning() {
    print_message "$YELLOW" "⚠ $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create PID directory
PID_DIR="$SCRIPT_DIR/.pids"
mkdir -p "$PID_DIR"

print_header "🛡️  Starting SentinTinel Surveillance System"

################################################################################
# Check Prerequisites
################################################################################

print_header "Checking Prerequisites"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js is not installed"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm found: v$NPM_VERSION"
else
    print_error "npm is not installed"
    exit 1
fi

################################################################################
# Check and Start PostgreSQL
################################################################################

print_header "Starting PostgreSQL"

if command -v pg_isready &> /dev/null; then
    if pg_isready -q; then
        print_success "PostgreSQL is already running"
    else
        print_warning "PostgreSQL is not running. Attempting to start..."

        # Try to start PostgreSQL (different methods for different systems)
        if command -v systemctl &> /dev/null; then
            sudo systemctl start postgresql || print_warning "Could not start PostgreSQL via systemctl"
        elif command -v brew &> /dev/null; then
            brew services start postgresql || print_warning "Could not start PostgreSQL via brew"
        else
            print_warning "Please start PostgreSQL manually"
        fi

        # Wait a bit and check again
        sleep 2
        if pg_isready -q; then
            print_success "PostgreSQL started successfully"
        else
            print_error "PostgreSQL is not running. Please start it manually."
            exit 1
        fi
    fi
else
    print_warning "PostgreSQL tools not found. Assuming it's running..."
fi

################################################################################
# Check and Start Redis
################################################################################

print_header "Starting Redis"

if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis is already running"
    else
        print_warning "Redis is not running. Attempting to start..."

        # Try to start Redis (different methods for different systems)
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis || print_warning "Could not start Redis via systemctl"
        elif command -v brew &> /dev/null; then
            brew services start redis || print_warning "Could not start Redis via brew"
        else
            print_warning "Please start Redis manually or continue without it"
        fi

        # Wait a bit and check again
        sleep 2
        if redis-cli ping &> /dev/null; then
            print_success "Redis started successfully"
        else
            print_warning "Redis is not running (optional service)"
        fi
    fi
else
    print_warning "Redis not found (optional service, continuing...)"
fi

################################################################################
# Setup Backend
################################################################################

print_header "Setting up Backend"

cd "$SCRIPT_DIR/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/.installed" ]; then
    print_warning "Installing backend dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    touch venv/.installed
    print_success "Backend dependencies installed"
else
    print_success "Backend dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit backend/.env and add your Gemini API key!"
    print_warning "Waiting 5 seconds for you to configure..."
    sleep 5
fi

# Initialize database if needed
if [ ! -f ".db_initialized" ]; then
    print_warning "Initializing database..."
    python init_db.py
    touch .db_initialized
    print_success "Database initialized"
fi

# Start backend
print_message "$BLUE" "Starting backend server..."
nohup python main.py > "$SCRIPT_DIR/.pids/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_DIR/backend.pid"

# Wait for backend to start
sleep 3

if kill -0 $BACKEND_PID 2>/dev/null; then
    print_success "Backend started (PID: $BACKEND_PID)"
    print_message "$GREEN" "Backend running at: http://localhost:8000"
else
    print_error "Backend failed to start. Check $SCRIPT_DIR/.pids/backend.log"
    exit 1
fi

################################################################################
# Setup Frontend
################################################################################

print_header "Setting up Frontend"

cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_success ".env file created"
fi

# Start frontend
print_message "$BLUE" "Starting frontend server..."
nohup npm start > "$SCRIPT_DIR/.pids/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PID_DIR/frontend.pid"

# Wait for frontend to start
sleep 5

if kill -0 $FRONTEND_PID 2>/dev/null; then
    print_success "Frontend started (PID: $FRONTEND_PID)"
    print_message "$GREEN" "Frontend running at: http://localhost:3000"
else
    print_error "Frontend failed to start. Check $SCRIPT_DIR/.pids/frontend.log"
    # Kill backend since frontend failed
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

################################################################################
# Summary
################################################################################

print_header "✅ SentinTinel Started Successfully!"

echo ""
print_message "$GREEN" "Services Status:"
print_message "$GREEN" "  • Backend:  http://localhost:8000"
print_message "$GREEN" "  • Frontend: http://localhost:3000"
print_message "$GREEN" "  • API Docs: http://localhost:8000/docs"
echo ""
print_message "$BLUE" "Process IDs:"
print_message "$BLUE" "  • Backend PID:  $BACKEND_PID"
print_message "$BLUE" "  • Frontend PID: $FRONTEND_PID"
echo ""
print_message "$YELLOW" "Logs:"
print_message "$YELLOW" "  • Backend:  tail -f .pids/backend.log"
print_message "$YELLOW" "  • Frontend: tail -f .pids/frontend.log"
echo ""
print_message "$GREEN" "To stop the system, run: ./stop.sh"
echo ""
print_message "$BLUE" "Opening dashboard in browser..."
sleep 2

# Try to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null
elif command -v open &> /dev/null; then
    open http://localhost:3000 &> /dev/null
else
    print_warning "Could not open browser automatically. Please visit: http://localhost:3000"
fi

print_message "$GREEN" "🎉 Happy Monitoring!"
