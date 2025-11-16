#!/bin/bash

################################################################################
# SentinTinel Surveillance System - Stop Script
# Stops all running services
################################################################################

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

PID_DIR="$SCRIPT_DIR/.pids"

print_header "🛑 Stopping SentinTinel Surveillance System"

################################################################################
# Stop Frontend
################################################################################

print_header "Stopping Frontend"

if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_message "$YELLOW" "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID

        # Wait for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 $FRONTEND_PID 2>/dev/null; then
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_warning "Force killing frontend..."
            kill -9 $FRONTEND_PID 2>/dev/null
        fi

        print_success "Frontend stopped"
    else
        print_warning "Frontend process not running"
    fi

    rm -f "$PID_DIR/frontend.pid"
else
    print_warning "Frontend PID file not found"
fi

# Also kill any remaining npm/node processes related to the frontend
pkill -f "react-scripts start" 2>/dev/null || true

################################################################################
# Stop Backend
################################################################################

print_header "Stopping Backend"

if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")

    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_message "$YELLOW" "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID

        # Wait for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 $BACKEND_PID 2>/dev/null; then
                break
            fi
            sleep 1
        done

        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_warning "Force killing backend..."
            kill -9 $BACKEND_PID 2>/dev/null
        fi

        print_success "Backend stopped"
    else
        print_warning "Backend process not running"
    fi

    rm -f "$PID_DIR/backend.pid"
else
    print_warning "Backend PID file not found"
fi

# Also kill any remaining uvicorn processes
pkill -f "uvicorn main:app" 2>/dev/null || true

################################################################################
# Optional: Stop PostgreSQL and Redis
################################################################################

print_header "Database Services"

read -p "$(echo -e ${YELLOW}Do you want to stop PostgreSQL and Redis? [y/N]: ${NC})" -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_message "$YELLOW" "Stopping PostgreSQL..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop postgresql && print_success "PostgreSQL stopped" || print_warning "Could not stop PostgreSQL"
    elif command -v brew &> /dev/null; then
        brew services stop postgresql && print_success "PostgreSQL stopped" || print_warning "Could not stop PostgreSQL"
    fi

    print_message "$YELLOW" "Stopping Redis..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop redis && print_success "Redis stopped" || print_warning "Could not stop Redis"
    elif command -v brew &> /dev/null; then
        brew services stop redis && print_success "Redis stopped" || print_warning "Could not stop Redis"
    fi
else
    print_message "$GREEN" "PostgreSQL and Redis left running"
fi

################################################################################
# Cleanup
################################################################################

print_header "Cleanup"

# Clean up log files if desired
if [ -d "$PID_DIR" ]; then
    LOG_COUNT=$(ls -1 "$PID_DIR"/*.log 2>/dev/null | wc -l)
    if [ $LOG_COUNT -gt 0 ]; then
        echo ""
        read -p "$(echo -e ${YELLOW}Do you want to delete log files? [y/N]: ${NC})" -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$PID_DIR"/*.log
            print_success "Log files deleted"
        else
            print_message "$GREEN" "Log files preserved at: $PID_DIR/"
        fi
    fi
fi

################################################################################
# Summary
################################################################################

print_header "✅ SentinTinel Stopped"

echo ""
print_message "$GREEN" "All services have been stopped successfully"
echo ""
print_message "$BLUE" "To start the system again, run: ./start.sh"
echo ""
