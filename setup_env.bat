@echo off
echo ========================================================
echo Setting up Python Virtual Environment
echo ========================================================

IF NOT EXIST venv (
    echo Creating virtual environment "venv"...
    python -m venv venv
) ELSE (
    echo Virtual environment "venv" already exists.
)

echo.
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -U pip
pip install -r requirements.txt

echo.
echo ========================================================
echo Environment setup complete!
echo ========================================================
pause
