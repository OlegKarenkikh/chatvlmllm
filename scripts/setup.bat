@echo off
REM Setup script for ChatVLMLLM project (Windows)

echo ==================================
echo ChatVLMLLM Setup Script
echo ==================================
echo.

REM Check Python version
echo [1/5] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo OK: Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo OK: Pip upgraded
echo.

REM Install dependencies
echo [5/5] Installing dependencies...
echo This may take 5-10 minutes...
pip install -r requirements.txt --quiet
echo OK: Dependencies installed
echo.

echo ==================================
echo Setup completed successfully!
echo ==================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run the application: streamlit run app.py
echo 3. Open browser: http://localhost:8501
echo.
echo For more information, see QUICKSTART.md
echo.
pause