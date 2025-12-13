#!/usr/bin/env python3
"""
Script to set up Python virtual environment for the backend.
Run this script to create and configure the virtual environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, cwd=cwd, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None


def main():
    """Set up the virtual environment."""
    backend_dir = Path(__file__).parent
    venv_path = backend_dir / "venv"
    
    print("Setting up Python virtual environment for canteen menu backend...")
    
    # Create virtual environment
    if not venv_path.exists():
        print("Creating virtual environment...")
        if run_command(f"python -m venv {venv_path}", cwd=backend_dir) is None:
            print("Failed to create virtual environment")
            sys.exit(1)
        print("Virtual environment created successfully")
    else:
        print("Virtual environment already exists")
    
    # Determine activation script path based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip"
    else:  # Unix/Linux/macOS
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
    
    # Install requirements
    print("Installing requirements...")
    if run_command(f"{pip_path} install -r requirements.txt", cwd=backend_dir) is None:
        print("Failed to install requirements")
        sys.exit(1)
    
    print("Setup complete!")
    print(f"To activate the virtual environment:")
    if os.name == 'nt':
        print(f"  {activate_script}")
    else:
        print(f"  source {activate_script}")


if __name__ == "__main__":
    main()