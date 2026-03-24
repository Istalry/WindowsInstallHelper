@echo off
echo ========================================================
echo Building Windows Install Helper (Self-Contained EXE)
echo ========================================================

REM Ensure environment is set up
IF NOT EXIST venv (
    echo Virtual environment not found. Please run setup_env.bat first.
    echo Running setup_env.bat automatically...
    call setup_env.bat
) ELSE (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Creation du build via PyInstaller
echo.
echo Running PyInstaller...
pyinstaller --noconfirm --onedir --windowed --name "MigrationTool" migration_tool\main.py

echo.
echo ========================================================
echo Build complete.
echo Check the "dist" folder for your standalone executable.
echo ========================================================
pause
