@echo off
echo ===================================================
echo Running WindowsInstallHelper Unit Tests...
echo ===================================================

:: Ensure we are in the script directory
cd /d "%~dp0"

:: Check for virtual environment and activate it if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment 'venv' not found.
    echo Using global Python environment...
)

:: Install dev requirements automatically
echo Ensuring testing dependencies are installed...
pip install -q -r requirements-dev.txt

:: Ensure pytest is available
where pytest >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pytest is not installed or not in PATH.
    pause
    exit /b 1
)

:: Run pytest with coverage
echo Running pytest...
pytest --cov=migration_tool --cov-report=term-missing tests/

echo.
echo Tests completed.
pause
