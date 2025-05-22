#!/bin/bash
# Setup UV environment and run streamlit

# Ensure UV is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing now..."
    curl -fsSL https://astral.sh/uv/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with UV..."
    uv venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from pyproject.toml and ensure specific packages are installed
echo "Installing dependencies with UV..."
uv pip install -e .
echo "Explicitly installing lxml and statsmodels..."
uv pip install lxml statsmodels

# Run streamlit using UV
echo "Running Streamlit app with UV..."
cd streamlit_app
python -m streamlit run app.py "$@"

# Note: To pass additional arguments to streamlit, add them after this script
# For example: ./run_dashboard.sh --server.port 8501
