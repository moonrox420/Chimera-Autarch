#!/bin/bash
# CHIMERA AUTARCH Startup Script for Linux/macOS
# This script activates the virtual environment and starts the system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
CONFIG_FILE="config.yaml"
LOG_LEVEL=""
OPEN_BROWSER=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --no-browser)
            OPEN_BROWSER=false
            shift
            ;;
        --help)
            echo "CHIMERA AUTARCH Startup Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --config FILE       Path to configuration file (default: config.yaml)"
            echo "  --log-level LEVEL   Override logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
            echo "  --no-browser        Don't automatically open dashboard in browser"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0"
            echo "  $0 --log-level DEBUG"
            echo "  $0 --config custom-config.yaml --no-browser"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}🧠 CHIMERA AUTARCH Startup Script${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l) -eq 1 ]]; then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Python 3.12+ is required but not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if virtual environment exists
VENV_PATH="$SCRIPT_DIR/droxai-env"
VENV_ACTIVATE="$VENV_PATH/bin/activate"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo -e "${YELLOW}📦 Virtual environment not found, creating...${NC}"
    $PYTHON_CMD -m venv "$VENV_PATH"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source "$VENV_ACTIVATE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Check and install dependencies
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}📦 Checking dependencies...${NC}"
    
    # Simple check if key packages are installed
    if ! python -c "import websockets, aiosqlite, numpy" 2>/dev/null; then
        echo -e "${YELLOW}📥 Installing dependencies...${NC}"
        pip install -q -r "$REQUIREMENTS_FILE"
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ All dependencies satisfied${NC}"
    fi
fi

# Set environment variables
if [ -n "$LOG_LEVEL" ]; then
    export CHIMERA_LOGGING_LEVEL="$LOG_LEVEL"
    echo -e "${YELLOW}🔧 Log level set to: $LOG_LEVEL${NC}"
fi

if [ "$CONFIG_FILE" != "config.yaml" ] && [ -f "$CONFIG_FILE" ]; then
    export CHIMERA_CONFIG_FILE="$CONFIG_FILE"
    echo -e "${YELLOW}🔧 Using config file: $CONFIG_FILE${NC}"
fi

# Check if main script exists
MAIN_SCRIPT="$SCRIPT_DIR/chimera_autarch.py"
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}❌ Main script not found: $MAIN_SCRIPT${NC}"
    exit 1
fi

# Start the system
echo ""
echo -e "${GREEN}🚀 Starting CHIMERA AUTARCH...${NC}"
echo -e "${CYAN}=================================${NC}"
echo ""
echo -e "${CYAN}📊 Dashboard: http://localhost:8000${NC}"
echo -e "${CYAN}🔌 WebSocket: ws://localhost:8765${NC}"
echo -e "${CYAN}📈 Metrics API: http://localhost:8000/metrics${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the system${NC}"
echo ""

# Open browser if not disabled
if [ "$OPEN_BROWSER" = true ]; then
    sleep 2
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8000" &> /dev/null &
    elif command -v open &> /dev/null; then
        open "http://localhost:8000" &> /dev/null &
    fi
fi

# Trap Ctrl+C for clean shutdown
trap 'echo -e "\n${YELLOW}👋 CHIMERA AUTARCH stopped${NC}"; exit 0' SIGINT SIGTERM

# Start CHIMERA
python "$MAIN_SCRIPT"
