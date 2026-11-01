#!/usr/bin/env bash

ALLOC_PLACE="./backend/"
if [ ! -d "$ALLOC_PLACE" ]; then
    echo "Error: Could not find allocation fodler."
    exit 1
fi

# 1. Detect the operating system
OS_TYPE="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
fi

echo "Detected OS: $OS_TYPE"

# 2. Find the correct Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
else
    echo "Error: Python is not installed or not in PATH."
    exit 1
fi

# 3. Create the .venv virtual environment if it doesn't exist
if [ ! -d ".vnv" ]; then
    echo "Creating virtual environment using $PYTHON_CMD..."
    $PYTHON_CMD -m venv "${ALLOC_PLACE}.vnv"
else
    echo ".vnv folder already exists. Skipping creation."
fi

# 4. Determine activation script path based on OS
# Note: For execution within this script, we call it directly,
# but to keep your current terminal active, read the instructions below.
if [ "$OS_TYPE" == "windows" ]; then
    ACTIVATE_PATH="${ALLOC_PLACE}.vnv/Scripts/activate"
else
    ACTIVATE_PATH="${ALLOC_PLACE}/bin/activate"
fi

# 5. Activate environment and install dependencies
if [ -f "$ACTIVATE_PATH" ]; then
    echo "Activating virtual environment..."
    echo "$ALLOC_PLACE/requirements.txt"
    source "$ACTIVATE_PATH"
    
    if [ -f "${ALLOC_PLACE}requirements.txt" ]; then
        echo "Installing requirements.txt..."
        python -m pip install --upgrade pip
        pip install -r "${ALLOC_PLACE}requirements.txt"
        echo "Setup complete! Environment is ready."
    else
        echo "Warning: requirements.txt not found. No packages installed."
    fi
else
    echo "Error: Activation script not found at $ACTIVATE_PATH"
    exit 1
fi