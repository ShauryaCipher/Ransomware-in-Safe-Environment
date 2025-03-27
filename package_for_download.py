#!/usr/bin/env python3
"""
Package for Download Script - Educational Ransomware Simulation

This script creates a downloadable ZIP package containing all the files
needed for the educational ransomware simulation tool.

DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY.
Using this code for malicious purposes is ILLEGAL and UNETHICAL.
"""

import os
import sys
import shutil
import zipfile
import datetime

def create_package(output_filename=None):
    """Create a ZIP package containing all necessary files."""
    
    # Set default filename if not provided
    if not output_filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ransomware_simulation_educational_{timestamp}.zip"
    
    # List of files to include in the package
    files_to_include = [
        "ransomware_simulation_desktop.py",
        "ransomware_client.py",
        "ransomware_server.py", 
        "crypto.py",
        "README.md",
        "usage_example.md"
    ]
    
    # Directories to include (will include all files within)
    dirs_to_include = [
        "educational_resources"
    ]
    
    try:
        # Create the ZIP file
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add individual files
            for file in files_to_include:
                if os.path.exists(file):
                    print(f"Adding file: {file}")
                    zipf.write(file)
                else:
                    print(f"Warning: File not found: {file}")
            
            # Add directories and their contents
            for directory in dirs_to_include:
                if os.path.exists(directory) and os.path.isdir(directory):
                    print(f"Adding directory: {directory}")
                    for root, _, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Add the file with its relative path to maintain directory structure
                            print(f"  - {file_path}")
                            zipf.write(file_path)
                else:
                    print(f"Warning: Directory not found: {directory}")
            
            # Add a requirements.txt file
            requirements = """
# Requirements for Educational Ransomware Simulation Tool
cryptography>=41.0.0
tqdm>=4.66.0
schedule>=1.2.0
requests>=2.31.0
"""
            zipf.writestr("requirements.txt", requirements.strip())
            print("Added requirements.txt")
            
            # Add an installation script
            install_script = """#!/bin/bash
# Installation script for the Educational Ransomware Simulation Tool

echo "=========================================================="
echo "  Installing dependencies for Ransomware Simulation Tool  "
echo "=========================================================="
echo ""
echo "This will install the required Python packages."
echo ""

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python 3.6+ before continuing."
    exit 1
fi

# Check Python version
$PYTHON_CMD -c "import sys; exit(0) if sys.version_info >= (3, 6) else exit(1)" || {
    echo "Error: Python 3.6 or higher is required."
    exit 1
}

echo "Using Python: $($PYTHON_CMD --version)"
echo ""

# Install required packages
echo "Installing required packages..."
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo ""
echo "To run the simulator:"
echo "  $PYTHON_CMD ransomware_simulation_desktop.py --interactive"
echo ""
echo "For help and options:"
echo "  $PYTHON_CMD ransomware_simulation_desktop.py --help"
echo ""
"""
            zipf.writestr("install.sh", install_script.strip())
            print("Added install.sh")
            
            # Add a Windows batch file for installation
            batch_script = """@echo off
echo ========================================================
echo   Installing dependencies for Ransomware Simulation Tool  
echo ========================================================
echo.
echo This will install the required Python packages.
echo.

rem Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found. Please install Python 3.6+ before continuing.
    exit /b 1
)

echo Installing required packages...
python -m pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the simulator:
echo   python ransomware_simulation_desktop.py --interactive
echo.
echo For help and options:
echo   python ransomware_simulation_desktop.py --help
echo.
pause
"""
            zipf.writestr("install.bat", batch_script.strip())
            print("Added install.bat")
            
        print(f"\nPackage created successfully: {output_filename}")
        print(f"Size: {os.path.getsize(output_filename) / 1024 / 1024:.2f} MB")
        
        return output_filename
        
    except Exception as e:
        print(f"Error creating package: {str(e)}")
        return None

def main():
    """Main function."""
    print("""
========================================================
  EDUCATIONAL RANSOMWARE SIMULATION - PACKAGING TOOL
========================================================

This script will create a downloadable package containing
all the files needed for the ransomware simulation tool.

All files will be included in a single ZIP archive for
easy distribution and installation.

========================================================
""")
    
    # Get optional output filename from command line
    output_filename = None
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    
    filename = create_package(output_filename)
    
    if filename:
        print("\nPackage created successfully!")
        print(f"You can download the file: {filename}")
    else:
        print("\nPackaging failed.")

if __name__ == "__main__":
    main()