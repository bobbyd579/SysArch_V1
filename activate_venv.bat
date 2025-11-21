@echo off
REM Activate the Python virtual environment

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run setup_venv.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo You can now use Python and install packages.
echo.
echo To deactivate, type: deactivate
echo.


