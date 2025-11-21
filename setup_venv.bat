@echo off
REM Setup script for creating a Python virtual environment on Windows

echo Checking for Python installation...

REM Try different Python commands
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :create_venv
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :create_venv
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :create_venv
)

echo.
echo ERROR: Python is not installed or not in PATH.
echo.
echo Please install Python 3.8 or later from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:create_venv
echo Python found: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.
echo Creating virtual environment in 'venv' folder...
%PYTHON_CMD% -m venv venv

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to create virtual environment.
    echo Make sure you have the 'venv' module installed.
    pause
    exit /b 1
)

echo.
echo Virtual environment created successfully!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo Or use the activate_venv.bat script.
echo.
pause


