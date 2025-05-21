#!/usr/bin/env python
"""
This script sets up a Python virtual environment using UV,
a modern alternative to pip and virtualenv.
"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and print output"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"Setting up UV environment in {project_root}")
    
    # Check if UV is installed
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("UV is already installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Installing UV...")
        # Install UV using the official install script
        install_cmd = ["curl", "-fsSL", "https://astral.sh/uv/install.sh", "|", "bash"]
        os.system(" ".join(install_cmd))  # Using os.system as shell piping is needed
    
    # Generate requirements.txt file if it doesn't exist
    requirements_file = os.path.join(project_root, "requirements.txt")
    if not os.path.exists(requirements_file):
        print("Creating requirements.txt...")
        with open(requirements_file, "w") as f:
            f.write("""
# Data processing libraries
pandas>=2.0.0
numpy>=1.24.0

# Database libraries
duckdb>=0.9.0
dbt-duckdb>=1.6.0

# Web scraping
requests>=2.31.0
beautifulsoup4>=4.12.0

# Data visualization
streamlit>=1.29.0
plotly>=5.18.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Other utilities
python-dotenv>=1.0.0
            """.strip())
    
    # Create virtual environment with UV
    venv_dir = os.path.join(project_root, ".venv")
    if not os.path.exists(venv_dir):
        print("Creating virtual environment with UV...")
        run_command(["uv", "venv", ".venv"], cwd=project_root)
    
    # Install dependencies with UV
    print("Installing dependencies with UV...")
    run_command(["uv", "pip", "install", "-r", "requirements.txt"], cwd=project_root)
    
    # Create activation scripts for different shells
    create_activation_scripts(project_root)
    
    print("\nUV environment setup complete!")
    print("To activate the environment:")
    print(f"  source {os.path.join(project_root, 'activate.sh')}")

def create_activation_scripts(project_root):
    """Create shell scripts to activate the virtual environment"""
    # Bash activation script
    bash_script = os.path.join(project_root, "activate.sh")
    with open(bash_script, "w") as f:
        f.write(f"""#!/bin/bash
# Activate the UV virtual environment
source "{os.path.join(project_root, '.venv', 'bin', 'activate')}"
echo "UV environment activated"
""")
    os.chmod(bash_script, 0o755)  # Make executable
    
if __name__ == "__main__":
    main()
