#!/bin/bash
# Simple wrapper to run streamlit with UV

# Ensure UV is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing now..."
    curl -fsSL https://astral.sh/uv/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    uv venv .venv
    echo "Installing dependencies..."
    source .venv/bin/activate
    uv pip install -e .
    echo "Explicitly installing lxml and statsmodels..."
    uv pip install lxml statsmodels
else
    # Activate the virtual environment
    source .venv/bin/activate
fi

# Run streamlit using Python in the virtual environment
echo "Running Streamlit app..."
cd streamlit_app
python -m streamlit run app.py "$@"
