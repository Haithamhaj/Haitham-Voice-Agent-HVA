#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🚀 Starting Haitham Voice Agent Backend..."

# Kill any existing instances
pkill -f "api/main.py" || true

# Activate virtual environment and run
source .venv/bin/activate
python3 api/main.py
