#!/bin/bash
# Script to run the Streamlit app with the UV environment

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if UV environment is set up
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "UV environment not found. Setting up now..."
    python "$PROJECT_ROOT/scripts/setup_uv_env.py"
fi

# Activate the UV environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Run the Streamlit app
echo "Starting Streamlit app..."
cd "$PROJECT_ROOT"
streamlit run "$PROJECT_ROOT/streamlit_app/app.py"
