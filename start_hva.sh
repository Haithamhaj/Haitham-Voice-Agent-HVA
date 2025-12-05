#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🚀 Starting Haitham Voice Agent Backend..."

# Kill any existing instances
pkill -f "api/main.py" || true

# Activate virtual environment and run
source .venv/bin/activate

# Run Integrity Check
echo "🔍 Running Integrity Check..."
python3 verify_integrity.py
if [ $? -ne 0 ]; then
    echo "❌ Integrity Check Failed. Aborting startup."
    exit 1
fi

# Start Backend
echo "🚀 Starting HVA Backend..."
python3 api/main.py
