#!/usr/bin/env bash

# 1. Define allocation folder path
ALLOC_PLACE="./frontend/"

if [ ! -d "$ALLOC_PLACE" ]; then
    echo "Error: Could not find allocation folder at $ALLOC_PLACE"
    exit 1
fi

# 2. Verify Node.js and npm are installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH."
    exit 1
fi

# 3. Navigate into the backend directory
# (This ensures npm commands run relative to your package.json)
cd "$ALLOC_PLACE" || { echo "Error: Failed to enter $ALLOC_PLACE"; exit 1; }

# 4. Install dependencies if package.json exists
if [ -f "package.json" ]; then
    echo "Found package.json. Installing dependencies..."
    npm i
else
    echo "Error: package.json not found in $ALLOC_PLACE"
    exit 1
fi

# 5. Start the development server
echo "Starting development server..."
npm run dev
